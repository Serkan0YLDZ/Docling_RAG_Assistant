"""RAG prompt oluşturma."""

def _system_prompt(ref_count: int) -> str:
    nums = (
        ", ".join(f"[{i}]" for i in range(1, ref_count + 1))
        if ref_count > 0
        else "(yok)"
    )
    return (
        "Sen bir asistansın. Yalnızca aşağıdaki BAĞLAM alanında verilen bilgileri "
        "kullanarak kullanıcının sorusunu yanıtla. Bağlamda olmayan bilgi uydurma.\n"
        f"Kullanılabilir kaynak numaraları: {nums}. "
        "Yanıtında yalnızca bu numaraları kullan; her önemli cümlede ilgili [n] atıfını yaz. "
        "Numaralar BAĞLAMdaki parça sırasıyla aynıdır ([1] ilk parça, [2] ikinci parça, …)."
    )


def build_rag_prompt(
    context_blocks: list[tuple[int, str]],
    history: list[dict],
    user_question: str,
) -> str:
    """Bağlam + sohbet geçmişi + son soru ile tek prompt metni."""
    ref_count = len(context_blocks)
    parts = [_system_prompt(ref_count), "", "BAĞLAM:"]
    for ref_index, text in context_blocks:
        parts.append(f"[{ref_index}] {text.strip()}")
    parts.append("")

    if history:
        parts.append("SOHBET GEÇMİŞİ:")
        for msg in history:
            role = msg.get("role", "user")
            label = "Kullanıcı" if role == "user" else "Asistan"
            content = (msg.get("content") or "").strip()
            if content:
                parts.append(f"{label}: {content}")
        parts.append("")

    parts.append("SORU:")
    parts.append(user_question.strip())
    return "\n".join(parts)
