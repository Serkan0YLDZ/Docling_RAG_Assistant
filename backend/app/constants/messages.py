"""API ve doğrulama için sabit kullanıcı mesajları."""

EMPTY_FILE = "Boş dosya yüklenemez"
MAX_FILE_SIZE = "Maksimum dosya boyutu aşıldı (50 MB)"
INVALID_EXTENSION = "Yalnızca PDF, DOCX veya TXT dosyaları kabul edilir"
DOCUMENT_NOT_FOUND = "Belge bulunamadı"
MISSING_GEMINI_KEY = "GEMINI_API_KEY tanımlı değil; indeksleme yapılamaz"
INDEXING_FAILED = "Vektör indeksleme başarısız oldu"
EMBEDDING_QUOTA_EXCEEDED = (
    "Gemini embedding kotası doldu. Yaklaşık 1 dakika bekleyip belgeyi yeniden yükleyin "
    "veya ai.google.dev üzerinden kotanızı kontrol edin."
)

QUERY_TOO_SHORT = "Lütfen daha açıklayıcı bir soru giriniz (En az 10 karakter)"
QUERY_TOO_LONG = "Karakter sınırı aşıldı, lütfen sorunuzu kısaltınız"

NO_CONTEXT_SIM = "Bu konuda bilgi bulunamadı"
NO_CONTEXT_ACTIVITY = "Bu bilgi dokümanlarda bulunmamaktadır"
NO_CONTEXT_PSEUDO = (
    "Üzgünüm, bu soruya yanıt verebilecek bir bilgi yüklenen dokümanlarda bulunamadı."
)
