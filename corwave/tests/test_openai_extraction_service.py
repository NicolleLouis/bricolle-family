import json
from unittest.mock import Mock, patch

import pytest

from corwave.services.openai_extraction_service import (
    OpenAIExtractionService,
    OpenAIExtractionServiceError,
)


class TestOpenAIExtractionService:
    def test_classify_publication_returns_dictionary_from_openai_json_content(self) -> None:
        mocked_response = Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "article_type": "Review",
                                "subject": "Clinical",
                                "category": "LVAD",
                                "relevance_score": 3,
                                "tag": "empagliflozin",
                            }
                        )
                    }
                }
            ]
        }

        service = OpenAIExtractionService(api_key="test-api-key", model="test-model")

        with patch("corwave.services.openai_extraction_service.requests.post", return_value=mocked_response):
            extracted_data = service.classify_publication(
                title="Interesting LVAD study",
                abstract="A retrospective analysis of LVAD outcomes.",
            )

        assert extracted_data == {
            "article_type": "Review",
            "subject": "Clinical",
            "category": "LVAD",
            "relevance_score": 3,
            "tag": "empagliflozin",
        }

    def test_classify_publication_uses_expected_json_schema_without_summary(self) -> None:
        mocked_response = Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "article_type": "Clinical trial",
                                "subject": "Clinical",
                                "category": "LVAD",
                                "relevance_score": 3,
                                "tag": "",
                            }
                        )
                    }
                }
            ]
        }
        service = OpenAIExtractionService(api_key="test-api-key", model="test-model")

        with patch("corwave.services.openai_extraction_service.requests.post", return_value=mocked_response) as mocked_post:
            service.classify_publication(
                title="Title",
                abstract="Abstract",
            )

        request_payload = mocked_post.call_args.kwargs["json"]
        assert request_payload["response_format"]["type"] == "json_schema"
        assert request_payload["response_format"]["json_schema"]["name"] == "publication_classification"
        assert request_payload["response_format"]["json_schema"]["schema"]["required"] == [
            "article_type",
            "subject",
            "category",
            "relevance_score",
            "tag",
        ]

    def test_classify_publication_uses_expected_json_schema_with_summary(self) -> None:
        mocked_response = Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "article_type": "Clinical trial",
                                "subject": "Clinical",
                                "category": "LVAD",
                                "summary": "Assesses outcomes of LVAD-supported patients.",
                                "relevance_score": 3,
                                "tag": "NuPulse",
                            }
                        )
                    }
                }
            ]
        }
        service = OpenAIExtractionService(api_key="test-api-key", model="test-model")

        with patch("corwave.services.openai_extraction_service.requests.post", return_value=mocked_response) as mocked_post:
            extracted_data = service.classify_publication(
                title="Title",
                abstract="Abstract",
                include_summary=True,
            )

        request_payload = mocked_post.call_args.kwargs["json"]
        assert request_payload["response_format"]["json_schema"]["schema"]["required"] == [
            "article_type",
            "subject",
            "category",
            "relevance_score",
            "summary",
            "tag",
        ]
        assert extracted_data["summary"] == "Assesses outcomes of LVAD-supported patients."
        assert extracted_data["tag"] == "NuPulse"

    def test_classify_publication_raises_error_when_openai_returns_invalid_json_content(self) -> None:
        mocked_response = Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {"choices": [{"message": {"content": "not-json"}}]}
        service = OpenAIExtractionService(api_key="test-api-key", model="test-model")

        with patch("corwave.services.openai_extraction_service.requests.post", return_value=mocked_response):
            with pytest.raises(OpenAIExtractionServiceError, match="not valid JSON"):
                service.classify_publication(
                    title="Title",
                    abstract="Abstract",
                )

    def test_classify_publication_raises_error_when_title_and_abstract_are_empty(self) -> None:
        service = OpenAIExtractionService(api_key="test-api-key", model="test-model")

        with pytest.raises(ValueError, match="both be empty"):
            service.classify_publication(
                title="   ",
                abstract="   ",
            )
