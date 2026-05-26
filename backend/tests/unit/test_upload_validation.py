import pytest

from app.config import Config
from app.constants import messages
from app.domain.errors import ValidationError
from app.services.upload_validator import UploadValidator

validator = UploadValidator(Config.MAX_UPLOAD_BYTES, Config.ALLOWED_EXTENSIONS)


@pytest.mark.tc_doc
def test_tc_doc_01_empty_file_rejected():
    with pytest.raises(ValidationError) as exc:
        validator.validate("report.pdf", 0)
    assert exc.value.message == messages.EMPTY_FILE
    assert exc.value.status_code == 400


@pytest.mark.tc_doc
def test_tc_doc_02_under_max_accepted():
    size = int(49.9 * 1024 * 1024)
    validator.validate("report.pdf", size)


@pytest.mark.tc_doc
def test_tc_doc_03_exact_max_accepted():
    validator.validate("report.pdf", Config.MAX_UPLOAD_BYTES)


@pytest.mark.tc_doc
def test_tc_doc_04_over_max_rejected():
    with pytest.raises(ValidationError) as exc:
        validator.validate("report.pdf", Config.MAX_UPLOAD_BYTES + 1)
    assert exc.value.message == messages.MAX_FILE_SIZE
    assert exc.value.status_code == 413


@pytest.mark.tc_fmt
def test_tc_fmt_01_invalid_extension_rejected():
    with pytest.raises(ValidationError) as exc:
        validator.validate("notes.exe", 1024)
    assert exc.value.message == messages.INVALID_EXTENSION


def test_allowed_extensions_accepted():
    validator.validate("a.pdf", 100)
    validator.validate("b.docx", 100)
    validator.validate("c.txt", 100)
