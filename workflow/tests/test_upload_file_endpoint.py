import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.status import HTTP_400_BAD_REQUEST
from workflow.constants import (
    FIXTURES_PATH,
    UPLOAD_FILE_ENDPOINT
)
from workflow.error_messages import workflow_errors
from workflow.exceptions import (
    FileNotExist,
    InvalidFileExtension,
    InvalidFileStructure,
    InvalidFileContent
)


class UploadFileEndpointTest(TestCase):

    def test_required_json_file(self):
        client = APIClient()
        response = client.post(
            UPLOAD_FILE_ENDPOINT,
            dict(file=''),
            format='multipart'
        )
        result = json.loads(response.content)
        self.assertRaises(FileNotExist)
        self.assertEqual(
            response.status_code,
            HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            result.get('detail'),
            workflow_errors.get('required_json_file')
        )

    def test_invalid_file_extension(self):
        client = APIClient()
        workflow_file_name = 'workflow_invalid_file_extension.txt'
        with open(f'{FIXTURES_PATH}{workflow_file_name}', 'rb') as txt_file:
            response = client.post(
                UPLOAD_FILE_ENDPOINT,
                dict(file=txt_file),
                format='multipart'
            )
            result = json.loads(response.content)
            self.assertRaises(InvalidFileExtension)
            self.assertEqual(
                response.status_code,
                HTTP_400_BAD_REQUEST
            )
            self.assertEqual(
                result.get('detail'),
                workflow_errors.get('invalid_file_extension')
            )

    def test_invalid_structure_json_file(self):
        client = APIClient()
        workflow_file_name = 'workflow_invalid_structure.json'
        with open(f'{FIXTURES_PATH}{workflow_file_name}', 'rb') as json_file:
            response = client.post(
                UPLOAD_FILE_ENDPOINT,
                dict(file=json_file),
                format='multipart'
            )
            result = json.loads(response.content)
            self.assertRaises(InvalidFileStructure)
            self.assertEqual(
                response.status_code,
                HTTP_400_BAD_REQUEST
            )
            self.assertEqual(
                result.get('detail'),
                workflow_errors.get('invalid_structure_json_file')
            )

    def test_invalid_content_json_file(self):
        client = APIClient()
        workflow_file_name = 'workflow_invalid_content.json'
        with open(f'{FIXTURES_PATH}{workflow_file_name}', 'rb') as json_file:
            response = client.post(
                UPLOAD_FILE_ENDPOINT,
                dict(file=json_file),
                format='multipart'
            )
            result = json.loads(response.content)
            self.assertRaises(json.decoder.JSONDecodeError)
            self.assertRaises(InvalidFileContent)
            self.assertEqual(
                response.status_code,
                HTTP_400_BAD_REQUEST
            )
            self.assertEqual(
                result.get('detail'),
                workflow_errors.get('invalid_content_json_file')
            )
