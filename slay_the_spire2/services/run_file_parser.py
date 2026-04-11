import json


class RunFileParserService:
    def parse_uploaded_file(self, uploaded_file) -> dict:
        raw_content = self._read_uploaded_file(uploaded_file)
        return self._parse_json(raw_content)

    def _read_uploaded_file(self, uploaded_file) -> str:
        uploaded_file.open("rb")
        raw_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        return raw_bytes.decode("utf-8")

    def _parse_json(self, raw_content: str) -> dict:
        try:
            parsed_payload = json.loads(raw_content)
        except json.JSONDecodeError as error:
            raise ValueError("Le fichier run doit contenir un JSON valide.") from error

        if not isinstance(parsed_payload, dict):
            raise ValueError("Le JSON du fichier run doit etre un objet JSON.")

        return parsed_payload
