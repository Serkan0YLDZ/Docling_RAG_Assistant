import pytest

from app.constants import messages
from app.domain.errors import ValidationError
from app.services.query_validator import QueryValidator

pytestmark = pytest.mark.tc_qry

validator = QueryValidator(min_length=10, max_length=500)


def test_tc_qry_01_too_short():
    with pytest.raises(ValidationError) as exc:
        validator.validate("kısa")
    assert exc.value.message == messages.QUERY_TOO_SHORT


def test_tc_qry_02_min_boundary():
    assert validator.validate("1234567890") == "1234567890"


def test_tc_qry_03_max_boundary():
    text = "a" * 500
    assert validator.validate(text) == text


def test_tc_qry_04_over_max():
    with pytest.raises(ValidationError) as exc:
        validator.validate("a" * 501)
    assert exc.value.message == messages.QUERY_TOO_LONG
