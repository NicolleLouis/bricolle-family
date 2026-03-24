from __future__ import annotations

import json
from typing import Any

import requests
from decouple import config


class OpenAIExtractionServiceError(RuntimeError):
    """Raised when the OpenAI extraction request cannot be completed."""


class OpenAIExtractionService:
    """Call OpenAI and return structured data extracted from publication text."""

    _CLASSIFICATION_SCHEMA = {
        "type": "object",
        "properties": {
            "article_type": {
                "type": "string",
                "enum": [
                    "Review",
                    "Case report",
                    "Prospective study",
                    "Retrospective study",
                    "Clinical trial",
                    "Preclinical trial",
                ],
            },
            "subject": {
                "type": "string",
                "enum": [
                    "R&D",
                    "Clinical",
                    "Epidemiology",
                ],
            },
            "category": {
                "type": "string",
                "enum": [
                    "LVAD",
                    "HTx",
                    "Xenotransplantation",
                    "ECMO",
                    "IABP",
                    "Interatrial shunt device",
                    "pVAD",
                    "TAH",
                    "BiVAD",
                    "RVAD",
                    "Acute HF",
                    "Chronic HF",
                    "HFpEF",
                    "Valve",
                    "Cardiac surgery",
                    "Vascular",
                    "Trial design",
                    "Pediatric",
                    "TET",
                    "Other",
                ],
            },
        },
        "required": ["article_type", "subject", "category"],
        "additionalProperties": False,
    }

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        self._api_key = api_key or config("OPENAI_API_KEY", default="")
        self._model = model or config("OPENAI_MODEL", default="gpt-4.1-mini")
        self._timeout_seconds = timeout_seconds

    def classify_publication(
        self,
        *,
        title: str,
        abstract: str,
    ) -> dict[str, str]:
        self._validate_inputs(title=title, abstract=abstract)
        self._validate_configuration()

        request_payload = self._build_classification_payload(
            title=title.strip(),
            abstract=abstract.strip(),
        )
        response_payload = self._perform_request(request_payload=request_payload)
        message_content = self._extract_message_content(response_payload=response_payload)
        parsed_content = self._parse_json(message_content=message_content)
        return self._validate_classification_output(parsed_content=parsed_content)

    @staticmethod
    def _validate_inputs(*, title: str, abstract: str) -> None:
        if not title.strip() and not abstract.strip():
            raise ValueError("title and abstract cannot both be empty.")

    def _validate_configuration(self) -> None:
        if not self._api_key:
            raise OpenAIExtractionServiceError(
                "Missing OPENAI_API_KEY. Define it in your environment."
            )

    def _build_classification_payload(
        self,
        *,
        title: str,
        abstract: str,
    ) -> dict:
        return {
            "model": self._model,
            "messages": self._build_classification_messages(
                title=title,
                abstract=abstract,
            ),
            "temperature": 0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "publication_classification",
                    "strict": True,
                    "schema": self._CLASSIFICATION_SCHEMA,
                },
            },
        }

    @staticmethod
    def _build_classification_messages(*, title: str, abstract: str) -> list[dict[str, str]]:
        abstract_for_prompt = abstract if abstract else "Not available."
        return [
            {
                "role": "system",
                "content": (
                    "Role: retrieve relevant information and help sort scientific publications in a systematic way. "
                    "Context: we work at Corwave, a company developing a novel LVAD. "
                    "Use only the title and abstract provided. "
                    "Return only valid JSON with keys article_type, subject, category. "
                    "Avoid any invention, remain factual."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Classify this publication.\n\n"
                    "Article type options:\n"
                    "- Review\n"
                    "- Case report\n"
                    "- Prospective study\n"
                    "- Retrospective study\n"
                    "- Clinical trial\n"
                    "- Preclinical trial\n\n"
                    "Subject options:\n"
                    "- R&D\n"
                    "- Clinical\n"
                    "- Epidemiology\n\n"
                    "Category options:\n"
                    "- LVAD\n"
                    "- HTx\n"
                    "- Xenotransplantation\n"
                    "- ECMO\n"
                    "- IABP\n"
                    "- Interatrial shunt device\n"
                    "- pVAD\n"
                    "- TAH\n"
                    "- BiVAD\n"
                    "- RVAD\n"
                    "- Acute HF\n"
                    "- Chronic HF\n"
                    "- HFpEF\n"
                    "- Valve\n"
                    "- Cardiac surgery\n"
                    "- Vascular\n"
                    "- Trial design\n"
                    "- Pediatric\n"
                    "- TET\n"
                    "- Other\n\n"
                    f"Title:\n{title}\n\n"
                    f"Abstract:\n{abstract_for_prompt}"
                ),
            },
        ]

    def _perform_request(self, *, request_payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self._build_headers(),
                json=request_payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as request_error:
            raise OpenAIExtractionServiceError(
                f"OpenAI request failed: {request_error}"
            ) from request_error
        except ValueError as parse_error:
            raise OpenAIExtractionServiceError(
                "OpenAI response could not be decoded as JSON."
            ) from parse_error

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _extract_message_content(*, response_payload: dict) -> str:
        choices = response_payload.get("choices")
        if not choices:
            raise OpenAIExtractionServiceError("OpenAI response does not contain choices.")

        first_choice = choices[0]
        message = first_choice.get("message")
        if not message:
            raise OpenAIExtractionServiceError("OpenAI response does not contain a message.")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OpenAIExtractionServiceError(
                "OpenAI response does not contain textual JSON content."
            )
        return content

    @staticmethod
    def _parse_json(*, message_content: str) -> dict:
        try:
            parsed_content = json.loads(message_content)
        except json.JSONDecodeError as decode_error:
            raise OpenAIExtractionServiceError(
                "OpenAI response content is not valid JSON."
            ) from decode_error

        if not isinstance(parsed_content, dict):
            raise OpenAIExtractionServiceError(
                "OpenAI response JSON must be an object."
            )
        return parsed_content

    @staticmethod
    def _validate_classification_output(*, parsed_content: dict) -> dict[str, str]:
        expected_keys = {"article_type", "subject", "category"}
        parsed_keys = set(parsed_content.keys())
        if parsed_keys != expected_keys:
            raise OpenAIExtractionServiceError(
                "OpenAI response must contain exactly article_type, subject, category."
            )

        for key in expected_keys:
            if not isinstance(parsed_content[key], str) or not parsed_content[key].strip():
                raise OpenAIExtractionServiceError(
                    f"OpenAI response field '{key}' must be a non-empty string."
                )

        return {
            "article_type": parsed_content["article_type"].strip(),
            "subject": parsed_content["subject"].strip(),
            "category": parsed_content["category"].strip(),
        }
