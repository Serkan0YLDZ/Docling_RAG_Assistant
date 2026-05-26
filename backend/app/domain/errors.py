class ValidationError(Exception):
    """İş kuralı veya girdi doğrulama hatası."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(Exception):
    """Kayıt bulunamadı."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.status_code = 404
