import io
import os
import zipfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile

from slay_the_spire2.services.run_file_upload import RunFileUploadService


class RunZipUploadService:
    def upload_zip_file(self, uploaded_zip_file: UploadedFile) -> dict:
        zip_file = self._open_zip(uploaded_zip_file)

        imported_count = 0
        error_messages = []
        processed_files_count = 0

        for zip_info in zip_file.infolist():
            if zip_info.is_dir():
                continue

            processed_files_count += 1
            try:
                file_bytes = zip_file.read(zip_info)
                uploaded_file = self._build_uploaded_file(
                    member_name=zip_info.filename,
                    file_bytes=file_bytes,
                )
                RunFileUploadService().upload_run_file(uploaded_file)
                imported_count += 1
            except (ValidationError, ValueError) as error:
                error_message = self._extract_error_message(error)
                error_messages.append(f"{zip_info.filename}: {error_message}")

        return {
            "processed_files_count": processed_files_count,
            "imported_count": imported_count,
            "error_messages": error_messages,
        }

    def _open_zip(self, uploaded_zip_file: UploadedFile) -> zipfile.ZipFile:
        uploaded_zip_file.open("rb")
        zip_bytes = uploaded_zip_file.read()
        uploaded_zip_file.seek(0)
        try:
            return zipfile.ZipFile(io.BytesIO(zip_bytes))
        except zipfile.BadZipFile as error:
            raise ValidationError({"file": "Le fichier zip est invalide."}) from error

    def _build_uploaded_file(self, member_name: str, file_bytes: bytes) -> SimpleUploadedFile:
        base_name = os.path.basename(member_name) or member_name
        return SimpleUploadedFile(
            name=base_name,
            content=file_bytes,
            content_type="application/json",
        )

    def _extract_error_message(self, error: Exception) -> str:
        if isinstance(error, ValidationError):
            return error.message_dict.get("file", ["Le fichier est invalide."])[0]
        return str(error)
