import csv
import io

import pytest

from corwave.services.csv_enrichment_service import (
    CorwaveCsvEnrichmentService,
    CorwaveCsvEnrichmentServiceError,
)
from corwave.services.openai_extraction_service import OpenAIExtractionServiceError


class FakeOpenAIExtractionService:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def classify_publication(self, *, title, abstract):
        self.calls.append(
            {
                "title": title,
                "abstract": abstract,
            }
        )
        current_response = self._responses[len(self.calls) - 1]
        if isinstance(current_response, Exception):
            raise current_response
        return current_response


class TestCorwaveCsvEnrichmentService:
    def test_enrich_csv_adds_fixed_classification_columns(self):
        csv_content = "Title,Abstract,PMID\nTitle A,Abstract A,1\nTitle B,Abstract B,2\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {"article_type": "Review", "subject": "Clinical", "category": "LVAD"},
                {"article_type": "Clinical trial", "subject": "Epidemiology", "category": "HTx"},
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        result = service.enrich_csv(
            csv_file_name="input.csv",
            csv_file_content=csv_content,
        )

        output_rows = list(csv.DictReader(io.StringIO(result.content)))

        assert result.filename == "input_enriched.csv"
        assert output_rows[0]["PMID"] == "1"
        assert output_rows[0]["article_type"] == "Review"
        assert output_rows[0]["subject"] == "Clinical"
        assert output_rows[0]["category"] == "LVAD"
        assert output_rows[1]["article_type"] == "Clinical trial"
        assert output_rows[1]["subject"] == "Epidemiology"
        assert output_rows[1]["category"] == "HTx"

        assert fake_service.calls[0]["title"] == "Title A"
        assert fake_service.calls[0]["abstract"] == "Abstract A"

    def test_enrich_csv_raises_error_when_output_column_already_exists(self):
        csv_content = "Title,Abstract,article_type\nA,B,existing\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[{"article_type": "Review", "subject": "Clinical", "category": "LVAD"}]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        with pytest.raises(CorwaveCsvEnrichmentServiceError, match="already contains output columns"):
            service.enrich_csv(
                csv_file_name="input.csv",
                csv_file_content=csv_content,
            )

    def test_enrich_csv_raises_error_when_header_is_missing(self):
        fake_service = FakeOpenAIExtractionService(responses=[])
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        with pytest.raises(CorwaveCsvEnrichmentServiceError, match="header row"):
            service.enrich_csv(
                csv_file_name="input.csv",
                csv_file_content=b"",
            )

    def test_enrich_csv_raises_error_with_csv_line_number_on_openai_failure(self):
        csv_content = "Title,Abstract\nA,a\nB,b\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {"article_type": "Review", "subject": "Clinical", "category": "LVAD"},
                OpenAIExtractionServiceError("network down"),
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        with pytest.raises(CorwaveCsvEnrichmentServiceError, match="line 3"):
            service.enrich_csv(
                csv_file_name="input.csv",
                csv_file_content=csv_content,
            )

    def test_enrich_csv_uses_title_when_abstract_is_missing(self):
        csv_content = "Title,Abstract\nA,\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[{"article_type": "Review", "subject": "Clinical", "category": "LVAD"}]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        result = service.enrich_csv(
            csv_file_name="input.csv",
            csv_file_content=csv_content,
        )
        output_rows = list(csv.DictReader(io.StringIO(result.content)))
        assert output_rows[0]["article_type"] == "Review"
        assert fake_service.calls[0]["title"] == "A"
        assert fake_service.calls[0]["abstract"] == ""

    def test_enrich_csv_raises_error_when_title_and_abstract_are_missing(self):
        csv_content = "Title,Abstract\n,\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(responses=[])
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        with pytest.raises(CorwaveCsvEnrichmentServiceError, match="line 2"):
            service.enrich_csv(
                csv_file_name="input.csv",
                csv_file_content=csv_content,
            )
