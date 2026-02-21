import re


class MassYesNameParser:
    def parse_names(self, raw_names: str) -> list[str]:
        candidates = self._split_raw_names(raw_names)
        unique_names: list[str] = []
        seen_names: set[str] = set()

        for candidate in candidates:
            normalized_name = self._normalize_name(candidate)
            if not normalized_name:
                continue

            lowercase_name = normalized_name.lower()
            if lowercase_name in seen_names:
                continue

            seen_names.add(lowercase_name)
            unique_names.append(normalized_name)

        return unique_names

    def _split_raw_names(self, raw_names: str) -> list[str]:
        return re.split(r"[\n,;]+", raw_names)

    def _normalize_name(self, name: str) -> str:
        return re.sub(r"\s+", " ", name).strip()
