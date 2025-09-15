"""API views for data source imports."""

import logging
from pathlib import Path
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .importers import BancoInterImportService
from .models import DocumentImport
from .serializers import DocumentImportSerializer

logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    """Handle document upload and import operations."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Upload and import a Banco Inter document.

        Expected parameters:
        - file: The uploaded file
        - document_type: Type of document (BANCO_INTER_MONTHLY_REPORT, etc.)
        """
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = request.FILES["file"]
        document_type = request.data.get("document_type")

        if not document_type:
            return Response(
                {"error": "document_type is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate document type
        valid_types = [choice[0] for choice in DocumentImport.DOCUMENT_TYPES]
        if document_type not in valid_types:
            return Response(
                {
                    "error": f"Invalid document_type. Must be one of: {', '.join(valid_types)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file extension
        file_ext = Path(uploaded_file.name).suffix.lower()
        allowed_extensions = [".csv", ".xlsx", ".xls", ".pdf"]
        if file_ext not in allowed_extensions:
            return Response(
                {
                    "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Save file temporarily
            file_path = f"imports/{request.user.id}/{uploaded_file.name}"
            stored_path = default_storage.save(
                file_path, ContentFile(uploaded_file.read())
            )
            full_path = default_storage.path(stored_path)

            # Import document
            import_service = BancoInterImportService()
            import_record = import_service.import_document(
                file_path=full_path,
                document_type=document_type,
                user=request.user,
            )

            # Serialize and return result
            serializer = DocumentImportSerializer(import_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Import failed for user {request.user.id}: {e}")
            return Response(
                {"error": f"Import failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DocumentImportListView(APIView):
    """List user's document imports."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get list of user's document imports."""
        imports = DocumentImport.objects.filter(user=request.user)

        # Filter by status if provided
        status_filter = request.query_params.get("status")
        if status_filter:
            imports = imports.filter(status=status_filter)

        # Filter by document type if provided
        doc_type_filter = request.query_params.get("document_type")
        if doc_type_filter:
            imports = imports.filter(document_type=doc_type_filter)

        serializer = DocumentImportSerializer(imports, many=True)
        return Response(serializer.data)


class DocumentImportDetailView(APIView):
    """Get details of a specific document import."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, import_id):
        """Get details of a specific import."""
        try:
            import_record = DocumentImport.objects.get(
                id=import_id, user=request.user
            )
            serializer = DocumentImportSerializer(import_record)
            return Response(serializer.data)

        except DocumentImport.DoesNotExist:
            return Response(
                {"error": "Import not found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def supported_document_types(request):
    """Get list of supported document types."""
    types = [
        {
            "value": choice[0],
            "label": choice[1],
            "description": _get_document_description(choice[0]),
        }
        for choice in DocumentImport.DOCUMENT_TYPES
    ]

    return Response(
        {
            "supported_types": types,
            "supported_formats": [".csv", ".xlsx", ".xls", ".pdf"],
        }
    )


def _get_document_description(document_type: str) -> str:
    """Get description for document type."""
    descriptions = {
        "BANCO_INTER_MONTHLY_REPORT": "Monthly investment portfolio report showing current positions and performance",
        "BANCO_INTER_BROKERAGE_NOTE": "Trading confirmation document showing buy/sell transactions with fees",
        "BANCO_INTER_EXTRACT": "Bank account statement showing all account transactions",
    }
    return descriptions.get(document_type, "Document import")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def retry_import(request, import_id):
    """Retry a failed import."""
    try:
        import_record = DocumentImport.objects.get(
            id=import_id, user=request.user, status="FAILED"
        )

        # Reset status and error message
        import_record.status = "PENDING"
        import_record.error_message = ""
        import_record.save()

        # Re-import
        import_service = BancoInterImportService()
        updated_record = import_service.import_document(
            file_path=import_record.file_path,
            document_type=import_record.document_type,
            user=request.user,
        )

        serializer = DocumentImportSerializer(updated_record)
        return Response(serializer.data)

    except DocumentImport.DoesNotExist:
        return Response(
            {"error": "Failed import not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Retry import failed: {e}")
        return Response(
            {"error": f"Retry failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
