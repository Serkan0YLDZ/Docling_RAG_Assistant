import os

from app.config import Config


def test_relative_upload_dir_resolves_to_backend_root(monkeypatch):
    monkeypatch.setenv("UPLOAD_DIR", "data/uploads")
    cfg = Config()
    assert cfg.UPLOAD_DIR.is_absolute()
    assert cfg.UPLOAD_DIR.name == "uploads"
    assert cfg.UPLOAD_DIR.parent.name == "data"
    assert cfg.UPLOAD_DIR.parent.parent == Config._backend_root.resolve()
