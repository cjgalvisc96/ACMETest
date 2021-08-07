import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.status import HTTP_400_BAD_REQUEST
from workflow.constants import (
    FIXTURES_PATH,
    UPLOAD_FILE_ENDPOINT
)
from workflow.error_messages import workflow_errors


class UploadFileEndpointTest(TestCase):

    def test_required_json_file(self):
        client = APIClient()
        response = client.post(
            UPLOAD_FILE_ENDPOINT,
            {'file': ''},
            format='multipart'
        )
        result = json.loads(response.content)
        self.assertEqual(
            response.status_code,
            HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            result.get('error'),
            workflow_errors.get('required_json_file')
        )

    def test_invalid_content_json_file(self):
        client = APIClient()
        workflow_file_name = 'workflow_invalid_content.json'
        with open(f'{FIXTURES_PATH}{workflow_file_name}', 'rb') as json_file:
            response = client.post(
                UPLOAD_FILE_ENDPOINT,
                {'file': json_file},
                format='multipart'
            )
            result = json.loads(response.content)
            self.assertRaises(json.decoder.JSONDecodeError)
            self.assertEqual(
                response.status_code,
                HTTP_400_BAD_REQUEST
            )
            self.assertEqual(
                result.get('error'),
                workflow_errors.get('invalid_content_json_file')
            )
