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

    def classify_publication(self, *, title, abstract, include_summary=False):
        self.calls.append(
            {
                "title": title,
                "abstract": abstract,
                "include_summary": include_summary,
            }
        )
        current_response = self._responses[len(self.calls) - 1]
        if isinstance(current_response, Exception):
            raise current_response
        return current_response


class TestCorwaveCsvEnrichmentService:
    def test_enrich_csv_adds_fixed_classification_columns(self):
        csv_content = (
            "Title,Abstract,PMID,PMCID,Journal/Book\n"
            "Title A,Abstract A,1,,Random journal\n"
            "Title B,Abstract B,2,PMC123456,Random journal\n"
        ).encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal A",
                    "relevance_score": 3,
                    "tag": "empagliflozin",
                },
                {
                    "article_type": "Clinical trial",
                    "subject": "Epidemiology",
                    "category": "HTx",
                    "summary": "Goal B",
                    "relevance_score": 2,
                    "tag": "NuPulse",
                },
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
        assert output_rows[0]["Free text availability"] == "No"
        assert output_rows[0]["To distribute"] == ""
        assert output_rows[0]["Type"] == "Review"
        assert output_rows[0]["Topic"] == "Clinical"
        assert output_rows[0]["Category"] == "LVAD"
        assert output_rows[0]["Summary"] == "Goal A"
        assert output_rows[0]["Relevance"] == "3"
        assert output_rows[0]["Tag"] == "empagliflozin"
        assert output_rows[1]["Free text availability"] == "Yes"
        assert output_rows[1]["To distribute"] == ""
        assert output_rows[1]["Type"] == "Clinical trial"
        assert output_rows[1]["Topic"] == "Epidemiology"
        assert output_rows[1]["Category"] == "HTx"
        assert output_rows[1]["Summary"] == "Goal B"
        assert output_rows[1]["Relevance"] == "2"
        assert output_rows[1]["Tag"] == "NuPulse"

        assert fake_service.calls[0]["title"] == "Title A"
        assert fake_service.calls[0]["abstract"] == "Abstract A"
        assert fake_service.calls[0]["include_summary"] is True

    def test_enrich_csv_marks_free_text_available_when_journal_is_whitelisted(self):
        csv_content = (
            "Title,Abstract,PMCID,Journal/Book\n"
            "Title A,Abstract A,,JACC: Heart Failure\n"
        ).encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal A",
                    "relevance_score": 3,
                    "tag": "",
                }
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        result = service.enrich_csv(
            csv_file_name="input.csv",
            csv_file_content=csv_content,
        )

        output_rows = list(csv.DictReader(io.StringIO(result.content)))

        assert output_rows[0]["Free text availability"] == "Yes"

    def test_enrich_csv_marks_free_text_unavailable_when_pmcid_and_journal_do_not_match(self):
        csv_content = (
            "Title,Abstract,PMCID,Journal/Book\n"
            "Title A,Abstract A,,Some other journal\n"
        ).encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal A",
                    "relevance_score": 3,
                    "tag": "",
                }
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        result = service.enrich_csv(
            csv_file_name="input.csv",
            csv_file_content=csv_content,
        )

        output_rows = list(csv.DictReader(io.StringIO(result.content)))

        assert output_rows[0]["Free text availability"] == "No"

    def test_enrich_csv_raises_error_when_output_column_already_exists(self):
        csv_content = "Title,Abstract,Type\nA,B,existing\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal",
                    "relevance_score": 3,
                    "tag": "",
                }
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        with pytest.raises(CorwaveCsvEnrichmentServiceError, match="already contains output columns"):
            service.enrich_csv(
                csv_file_name="input.csv",
                csv_file_content=csv_content,
            )

    def test_enrich_csv_raises_error_when_free_text_availability_column_already_exists(self):
        csv_content = "Title,Abstract,Free text availability\nA,B,Yes\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal",
                    "relevance_score": 3,
                    "tag": "",
                }
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        with pytest.raises(CorwaveCsvEnrichmentServiceError, match="already contains output columns"):
            service.enrich_csv(
                csv_file_name="input.csv",
                csv_file_content=csv_content,
            )

    def test_enrich_csv_raises_error_when_to_distribute_column_already_exists(self):
        csv_content = "Title,Abstract,To distribute\nA,B,\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal",
                    "relevance_score": 3,
                    "tag": "",
                }
            ]
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
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal",
                    "relevance_score": 3,
                    "tag": "",
                },
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
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "relevance_score": 3,
                    "tag": "",
                }
            ]
        )
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        result = service.enrich_csv(
            csv_file_name="input.csv",
            csv_file_content=csv_content,
        )
        output_rows = list(csv.DictReader(io.StringIO(result.content)))
        assert output_rows[0]["Type"] == "Review"
        assert output_rows[0]["Summary"] == ""
        assert output_rows[0]["Relevance"] == "3"
        assert output_rows[0]["Tag"] == ""
        assert fake_service.calls[0]["title"] == "A"
        assert fake_service.calls[0]["abstract"] == ""
        assert fake_service.calls[0]["include_summary"] is False

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

    def test_enrich_csv_calls_progress_callback_for_each_processed_row(self):
        csv_content = "Title,Abstract\nA,a\nB,b\n".encode("utf-8")
        fake_service = FakeOpenAIExtractionService(
            responses=[
                {
                    "article_type": "Review",
                    "subject": "Clinical",
                    "category": "LVAD",
                    "summary": "Goal A",
                    "relevance_score": 3,
                    "tag": "empagliflozin",
                },
                {
                    "article_type": "Clinical trial",
                    "subject": "Epidemiology",
                    "category": "HTx",
                    "summary": "Goal B",
                    "relevance_score": 2,
                    "tag": "NuPulse",
                },
            ]
        )
        progress_updates = []
        service = CorwaveCsvEnrichmentService()
        service._openai_extraction_service = fake_service

        service.enrich_csv(
            csv_file_name="input.csv",
            csv_file_content=csv_content,
            progress_callback=lambda processed, total: progress_updates.append((processed, total)),
        )

        assert progress_updates == [(1, 2), (2, 2)]
