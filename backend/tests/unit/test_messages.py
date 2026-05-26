from app.constants import messages


def test_upload_messages_match_report():
    assert messages.EMPTY_FILE == "Boş dosya yüklenemez"
    assert messages.MAX_FILE_SIZE == "Maksimum dosya boyutu aşıldı (50 MB)"


def test_query_messages_defined():
    assert "10 karakter" in messages.QUERY_TOO_SHORT
    assert "kısaltınız" in messages.QUERY_TOO_LONG
