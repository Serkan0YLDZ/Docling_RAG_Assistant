from app.services.rag_prompt import build_rag_prompt


def test_build_rag_prompt_includes_context_history_and_question():
    prompt = build_rag_prompt(
        [(1, "Ar-Ge en büyük kalemdir."), (2, "Üçüncü çeyrek tablosu.")],
        [
            {"role": "user", "content": "İlk soru nedir?"},
            {"role": "assistant", "content": "İlk cevap."},
        ],
        "Bunu özetler misin?",
    )
    assert "BAĞLAM:" in prompt
    assert "[1] Ar-Ge" in prompt
    assert "SOHBET GEÇMİŞİ:" in prompt
    assert "Kullanıcı: İlk soru" in prompt
    assert "Asistan: İlk cevap" in prompt
    assert "SORU:" in prompt
    assert "Bunu özetler misin?" in prompt


def test_build_rag_prompt_without_history():
    prompt = build_rag_prompt([(1, "Metin.")], [], "Yeni soru?")
    assert "SOHBET GEÇMİŞİ:" not in prompt
    assert "Yeni soru?" in prompt
