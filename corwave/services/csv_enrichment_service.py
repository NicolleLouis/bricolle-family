from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from corwave.services.openai_extraction_service import (
    OpenAIExtractionService,
    OpenAIExtractionServiceError,
)


class CorwaveCsvEnrichmentServiceError(RuntimeError):
    """Raised when CSV enrichment cannot be completed."""


@dataclass
class CsvEnrichmentResult:
    filename: str
    content: str


class CorwaveCsvEnrichmentService:
    """Enrich each CSV row with structured data extracted by OpenAI."""

    _OUTPUT_COLUMNS = ["article_type", "subject", "category"]

    def __init__(self) -> None:
        self._openai_extraction_service = OpenAIExtractionService()

    def enrich_csv(
        self,
        *,
        csv_file_name: str,
        csv_file_content: bytes,
    ) -> CsvEnrichmentResult:
        original_column_names, original_rows = self._parse_csv(csv_file_content=csv_file_content)
        extracted_rows = self._extract_rows(original_rows=original_rows)
        output_content = self._build_output_csv(
            original_column_names=original_column_names,
            original_rows=original_rows,
            extracted_rows=extracted_rows,
        )
        return CsvEnrichmentResult(
            filename=self._build_output_file_name(csv_file_name),
            content=output_content,
        )

    @staticmethod
    def _parse_csv(*, csv_file_content: bytes) -> tuple[list[str], list[dict[str, str]]]:
        try:
            decoded_content = csv_file_content.decode("utf-8-sig")
        except UnicodeDecodeError as decode_error:
            raise CorwaveCsvEnrichmentServiceError(
                "CSV encoding must be UTF-8."
            ) from decode_error

        reader = csv.DictReader(io.StringIO(decoded_content))
        if not reader.fieldnames:
            raise CorwaveCsvEnrichmentServiceError("CSV must contain a header row.")

        parsed_rows: list[dict[str, str]] = []
        for row in reader:
            parsed_rows.append(
                {column_name: (column_value or "") for column_name, column_value in row.items()}
            )

        return list(reader.fieldnames), parsed_rows

    def _extract_rows(
        self,
        *,
        original_rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        extracted_rows: list[dict[str, str]] = []
        for row_index, current_row in enumerate(original_rows):
            source_line_number = row_index + 2
            try:
                title, abstract = self._read_publication_fields(current_row=current_row)
            except CorwaveCsvEnrichmentServiceError as row_error:
                raise CorwaveCsvEnrichmentServiceError(
                    f"CSV validation failed at line {source_line_number}: {row_error}"
                ) from row_error

            try:
                extracted_row = self._openai_extraction_service.classify_publication(
                    title=title,
                    abstract=abstract,
                )
            except OpenAIExtractionServiceError as extraction_error:
                raise CorwaveCsvEnrichmentServiceError(
                    f"OpenAI extraction failed at CSV line {source_line_number}: {extraction_error}"
                ) from extraction_error

            extracted_rows.append(extracted_row)

        return extracted_rows

    def _read_publication_fields(self, *, current_row: dict[str, str]) -> tuple[str, str]:
        title = self._get_field_value(current_row=current_row, target_field_name="Title")
        abstract = self._get_field_value(current_row=current_row, target_field_name="Abstract")
        if not title.strip() and not abstract.strip():
            raise CorwaveCsvEnrichmentServiceError(
                "CSV row has empty Title and Abstract values."
            )
        return title, abstract

    @staticmethod
    def _get_field_value(*, current_row: dict[str, str], target_field_name: str) -> str:
        for field_name, field_value in current_row.items():
            if (field_name or "").strip().lower() == target_field_name.lower():
                return field_value or ""
        return ""

    def _build_output_csv(
        self,
        *,
        original_column_names: list[str],
        original_rows: list[dict[str, str]],
        extracted_rows: list[dict[str, str]],
    ) -> str:
        additional_columns, extraction_column_map = self._build_output_columns(existing_columns=original_column_names)
        output_columns = original_column_names + additional_columns

        output_buffer = io.StringIO()
        writer = csv.DictWriter(output_buffer, fieldnames=output_columns)
        writer.writeheader()

        for original_row, extracted_row in zip(original_rows, extracted_rows):
            output_row = dict(original_row)
            for extracted_key, output_column in extraction_column_map.items():
                output_row[output_column] = extracted_row.get(extracted_key, "")
            writer.writerow(output_row)

        return output_buffer.getvalue()

    def _build_output_columns(
        self,
        *,
        existing_columns: list[str],
    ) -> tuple[list[str], dict[str, str]]:
        self._validate_output_columns_do_not_exist(existing_columns=existing_columns)
        output_columns: list[str] = []
        extraction_column_map: dict[str, str] = {}
        for extracted_key in self._OUTPUT_COLUMNS:
            output_column_name = extracted_key
            output_columns.append(output_column_name)
            extraction_column_map[extracted_key] = output_column_name

        return output_columns, extraction_column_map

    def _validate_output_columns_do_not_exist(self, *, existing_columns: list[str]) -> None:
        normalized_existing_columns = {(column_name or "").strip().lower() for column_name in existing_columns}
        conflicting_columns = [
            expected_column
            for expected_column in self._OUTPUT_COLUMNS
            if expected_column.lower() in normalized_existing_columns
        ]
        if conflicting_columns:
            conflicts = ", ".join(conflicting_columns)
            raise CorwaveCsvEnrichmentServiceError(
                f"CSV already contains output columns: {conflicts}."
            )

    @staticmethod
    def _build_output_file_name(input_name: str) -> str:
        cleaned_name = (input_name or "").strip() or "input.csv"
        if "." not in cleaned_name:
            return f"{cleaned_name}_enriched.csv"
        base_name, extension = cleaned_name.rsplit(".", 1)
        return f"{base_name}_enriched.{extension}"
