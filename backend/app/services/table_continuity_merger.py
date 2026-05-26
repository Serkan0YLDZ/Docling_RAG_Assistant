import re


class TableContinuityMerger:
    """Sayfa kırılımında bölünmüş markdown tablolarını birleştirir."""

    _TABLE_ROW_RE = re.compile(r"^\s*\|.+\|\s*$")
    _TABLE_SEP_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")

    def merge(self, markdown: str) -> str:
        """Ardışık tablo satırları arasındaki gereksiz boş satırları kaldırır."""
        lines = markdown.splitlines()
        if not lines:
            return markdown

        merged: list[str] = []
        for line in lines:
            if not line.strip():
                if merged and self._is_table_line(merged[-1]):
                    continue
            merged.append(line)

        return self._join_split_table_blocks("\n".join(merged))

    def _is_table_line(self, line: str) -> bool:
        return bool(
            self._TABLE_ROW_RE.match(line) or self._TABLE_SEP_RE.match(line)
        )

    def _join_split_table_blocks(self, text: str) -> str:
        """İki ayrı tablo bloğunu tek tabloda birleştirir (ortak sütun sayısı)."""
        blocks = text.split("\n\n")
        if len(blocks) < 2:
            return text

        result: list[str] = [blocks[0]]
        for block in blocks[1:]:
            prev = result[-1]
            if self._can_merge_tables(prev, block):
                result[-1] = self._merge_two_tables(prev, block)
            else:
                result.append(block)
        return "\n\n".join(result)

    def _can_merge_tables(self, left: str, right: str) -> bool:
        left_rows = [ln for ln in left.splitlines() if self._is_table_line(ln)]
        right_rows = [ln for ln in right.splitlines() if self._is_table_line(ln)]
        if not left_rows or not right_rows:
            return False
        if any(self._TABLE_SEP_RE.match(r) for r in right_rows[:1]):
            right_rows = right_rows[1:]
        if not right_rows:
            return False
        return self._column_count(left_rows[-1]) == self._column_count(right_rows[0])

    def _merge_two_tables(self, left: str, right: str) -> str:
        left_lines = left.splitlines()
        right_lines = right.splitlines()
        right_data = [
            ln
            for ln in right_lines
            if self._is_table_line(ln) and not self._TABLE_SEP_RE.match(ln)
        ]
        if right_lines and self._TABLE_SEP_RE.match(right_lines[0]):
            right_data = [
                ln
                for ln in right_lines[1:]
                if self._is_table_line(ln) and not self._TABLE_SEP_RE.match(ln)
            ]
        return "\n".join(left_lines + right_data)

    def _column_count(self, row: str) -> int:
        return len([cell for cell in row.split("|") if cell.strip()])
