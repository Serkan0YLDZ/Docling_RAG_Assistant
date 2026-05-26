import os

from flask import Flask, jsonify
from flask_cors import CORS

from app.env_loader import load_repo_env
from app.blueprints.chat import chat_bp
from app.blueprints.documents import documents_bp
from app.blueprints.health import health_bp
from app.blueprints.sources import sources_bp
from app.config import Config
from app.domain.errors import NotFoundError, ValidationError
from app.infrastructure.chroma_vector_store import ChromaVectorStore
from app.infrastructure.deterministic_embedding import DeterministicEmbedding
from app.infrastructure.docling_adapter import DoclingAdapter
from app.infrastructure.fake_docling_parser import FakeDoclingParser
from app.infrastructure.gemini_embedding import GeminiEmbedding
from app.infrastructure.noop_chunk_enricher import NoOpChunkEnricher
from app.infrastructure.fake_llm import FakeLLM
from app.infrastructure.gemini_llm import GeminiLLM
from app.services.chunk_store import ChunkStore
from app.services.contextual_chunk_enricher import ContextualChunkEnricher
from app.services.document_processor import DocumentProcessor
from app.services.document_service import DocumentService
from app.services.file_store import FileStore
from app.services.chat_session_service import ChatSessionService
from app.services.context_filter import ContextFilter
from app.services.indexing_service import IndexingService
from app.services.query_pipeline import QueryPipeline
from app.services.query_validator import QueryValidator
from app.services.rag_engine import RAGEngine
from app.services.search_response_builder import SearchResponseBuilder
from app.services.source_preview_service import SourcePreviewService
from app.services.upload_validator import UploadValidator


def _use_deterministic_embedding(cfg: Config) -> bool:
    if getattr(cfg, "TESTING", False):
        return True
    return os.environ.get("USE_DETERMINISTIC_EMBEDDING", "").lower() in (
        "1",
        "true",
        "yes",
    )


def _build_chunk_enricher(cfg: Config):
    """Test: NoOp; prod + flag: Gemini contextual enricher."""
    if getattr(cfg, "TESTING", False):
        return NoOpChunkEnricher(), False
    if cfg.ENABLE_LLM_CHUNK_ENRICHMENT and cfg.GEMINI_API_KEY.strip():
        llm = GeminiLLM(
            api_key=cfg.GEMINI_API_KEY,
            model=cfg.GEMINI_LLM_MODEL,
            min_interval_sec=cfg.EMBEDDING_MIN_INTERVAL_SEC,
            max_retries=cfg.EMBEDDING_MAX_RETRIES,
        )
        enricher = ContextualChunkEnricher(
            llm=llm,
            max_input_chars=cfg.LLM_ENRICH_MAX_CHARS,
        )
        return enricher, True
    return NoOpChunkEnricher(), False


def create_app(config: Config | None = None) -> Flask:
    """Flask uygulamasını oluşturur ve bağımlılıkları kaydeder."""
    load_repo_env()
    app = Flask(__name__)
    cfg = config if config is not None else Config()

    CORS(app, origins=cfg.CORS_ORIGINS, supports_credentials=True)

    store = FileStore(cfg.UPLOAD_DIR, cfg.REGISTRY_PATH)
    chunk_store = ChunkStore(cfg.CHUNKS_DIR)
    validator = UploadValidator(cfg.MAX_UPLOAD_BYTES, cfg.ALLOWED_EXTENSIONS)

    use_fake_docling = os.environ.get("USE_FAKE_DOCLING", "").lower() in (
        "1",
        "true",
        "yes",
    )
    parser = FakeDoclingParser() if use_fake_docling else DoclingAdapter()
    enricher, use_llm_enrichment = _build_chunk_enricher(cfg)
    processor = DocumentProcessor(
        store=store,
        chunk_store=chunk_store,
        parser=parser,
        enricher=enricher,
        max_tokens=cfg.CHUNK_MAX_TOKENS,
        overlap_ratio=cfg.CHUNK_OVERLAP_RATIO,
        use_llm_enrichment=use_llm_enrichment,
    )

    if _use_deterministic_embedding(cfg):
        embedding = DeterministicEmbedding()
    else:
        embedding = GeminiEmbedding(
            api_key=cfg.GEMINI_API_KEY,
            batch_size=cfg.EMBEDDING_BATCH_SIZE,
            dimension=cfg.EMBEDDING_DIMENSION,
            min_interval_sec=cfg.EMBEDDING_MIN_INTERVAL_SEC,
            max_retries=cfg.EMBEDDING_MAX_RETRIES,
        )

    vector_store = ChromaVectorStore(
        persist_path=cfg.CHROMA_PATH,
        collection_name=cfg.CHROMA_COLLECTION,
        dimension=embedding.dimension,
    )
    indexing_service = IndexingService(
        embedding=embedding,
        vector_store=vector_store,
        batch_size=cfg.EMBEDDING_BATCH_SIZE,
    )

    app.extensions["file_store"] = store
    app.extensions["document_service"] = DocumentService(
        store,
        validator,
        processor,
        chunk_store,
        indexing_service,
    )
    app.extensions["vector_store"] = vector_store
    app.extensions["embedding"] = embedding
    query_validator = QueryValidator(
        min_length=cfg.QUERY_MIN_LENGTH,
        max_length=cfg.QUERY_MAX_LENGTH,
    )
    response_builder = SearchResponseBuilder()
    query_pipeline = QueryPipeline(
        store=store,
        embedding=embedding,
        vector_store=vector_store,
        validator=query_validator,
        context_filter=ContextFilter(threshold=cfg.SIMILARITY_THRESHOLD),
        response_builder=response_builder,
        top_k=cfg.RAG_TOP_K,
    )
    app.extensions["query_pipeline"] = query_pipeline
    app.extensions["config"] = cfg

    if getattr(cfg, "TESTING", False) or not cfg.GEMINI_API_KEY.strip():
        rag_llm = FakeLLM()
    else:
        rag_llm = GeminiLLM(
            api_key=cfg.GEMINI_API_KEY,
            model=cfg.GEMINI_LLM_MODEL,
            min_interval_sec=cfg.EMBEDDING_MIN_INTERVAL_SEC,
            max_retries=cfg.EMBEDDING_MAX_RETRIES,
        )

    app.extensions["rag_engine"] = RAGEngine(
        pipeline=query_pipeline,
        llm=rag_llm,
        response_builder=response_builder,
        max_history_turns=cfg.RAG_MAX_HISTORY_TURNS,
        temperature=cfg.RAG_TEMPERATURE,
    )
    app.extensions["chat_session"] = ChatSessionService()
    app.extensions["source_preview"] = SourcePreviewService(store, chunk_store)

    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(sources_bp)

    @app.errorhandler(ValidationError)
    def handle_validation(err: ValidationError):
        return jsonify({"error": err.message}), err.status_code

    @app.errorhandler(NotFoundError)
    def handle_not_found(err: NotFoundError):
        return jsonify({"error": err.message}), err.status_code

    return app
