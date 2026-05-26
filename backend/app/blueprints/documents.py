from flask import Blueprint, jsonify, request, send_file

from app.domain.document import MimeKind
from app.domain.errors import NotFoundError, ValidationError

MIME_BY_KIND: dict[MimeKind, str] = {
    "pdf": "application/pdf",
    "text": "text/plain; charset=utf-8",
    "doc": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

documents_bp = Blueprint("documents", __name__)


def _service():
    from flask import current_app

    return current_app.extensions["document_service"]


@documents_bp.get("/api/documents")
def list_documents():
    """Yüklenen belgeleri listeler."""
    return jsonify(_service().list_documents())


@documents_bp.post("/api/documents")
def upload_document():
    """Multipart dosya yükler."""
    if "file" not in request.files:
        raise ValidationError("Dosya alanı gerekli", status_code=400)

    uploaded = request.files["file"]
    if not uploaded.filename:
        raise ValidationError("Dosya adı gerekli", status_code=400)

    file_bytes = uploaded.read()
    try:
        item = _service().upload(uploaded.filename, file_bytes)
        return jsonify(item), 201
    except ValidationError:
        raise


@documents_bp.get("/api/documents/<document_id>/status")
def document_status(document_id: str):
    """Belge işleme ilerlemesini döner."""
    return jsonify(_service().get_status(document_id))


@documents_bp.delete("/api/documents/<document_id>")
def delete_document(document_id: str):
    """Belgeyi siler."""
    _service().delete(document_id)
    return "", 204


def _file_store():
    from flask import current_app

    return current_app.extensions["file_store"]


@documents_bp.get("/api/documents/<document_id>/file")
def document_file(document_id: str):
    """Orijinal belge dosyasını inline sunar."""
    store = _file_store()
    doc = store.get(document_id)
    try:
        path = store.get_file_path(document_id)
    except FileNotFoundError as exc:
        raise NotFoundError(str(exc)) from exc
    mimetype = MIME_BY_KIND.get(doc.mime_kind, "application/octet-stream")
    return send_file(
        path,
        mimetype=mimetype,
        as_attachment=False,
        download_name=doc.name,
        conditional=True,
    )


def _source_preview():
    from flask import current_app

    return current_app.extensions["source_preview"]


@documents_bp.get("/api/documents/<document_id>/source")
def document_source(document_id: str):
    """Kaynak önizlemesi (ref = chunk_index)."""
    ref = request.args.get("ref", type=int)
    if ref is None:
        raise ValidationError("ref parametresi gerekli", status_code=400)
    return jsonify(_source_preview().get_preview(document_id, ref))
