import logging

from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tablib import UnsupportedFormat, InvalidDimensions, Dataset

from lily.importer.models import ImportUpload
from lily.utils.api.permissions import IsAccountAdmin

from ..tasks import import_csv_file

logger = logging.getLogger(__name__)


class AccountContactImport(APIView):
    permission_classes = (IsAuthenticated, IsAccountAdmin, )
    classes = (FileUploadParser, )
    swagger_schema = None

    def post(self, request):
        import_type = request.data['import_type']
        try:
            csv_file = request.data['csv']
            imported_data = Dataset().load(csv_file.read())
        except MultiValueDictKeyError:
            # Form submit without a file, or the file size exceeds upload limit.
            return Response(
                {'file_contacts': {'Please choose a CSV file within file size limit to import'}},
                status=status.HTTP_409_CONFLICT
            )
        except UnsupportedFormat:
            return Response({'import_file': {'CSV file not properly formatted'}}, status=status.HTTP_409_CONFLICT)
        except InvalidDimensions:
            return Response({'import_file': {'Number of columns differs per row'}}, status=status.HTTP_409_CONFLICT)

        if import_type not in ['contacts', 'accounts']:
            return Response({'import': {'Import type incorrect'}}, status=status.HTTP_409_CONFLICT)

        # The following set of fields should be present as headers in the uploaded file.
        if import_type == 'contacts':
            required_fields = {u'first name', u'last name'}
        else:  # 'accounts'
            required_fields = {u'company name'}

        # The following headers are present in the uploaded file.
        available_in_upload = set(imported_data.headers)

        # Use set operations to determine which of the headers in the uploaded file are missing, optional or extra.
        missing_in_upload = required_fields - (required_fields & available_in_upload)

        if bool(missing_in_upload):
            return Response(
                {'import_file': {'The follwing columns are missing: {0}'.format(', '.join(missing_in_upload))}},
                status=status.HTTP_409_CONFLICT
            )

        tenant_id = self.request.user.tenant_id
        csv_upload = ImportUpload.objects.create(tenant_id=tenant_id, csv=csv_file)

        import_csv_file.apply_async(
            queue='other_tasks',
            kwargs={
                'upload_id': csv_upload.id,
                'iteration': 0,
                'import_type': import_type,
            },
        )

        return Response(
            {'import_file': {'Your file is being imported in the background'}},
            status=status.HTTP_201_CREATED
        )
