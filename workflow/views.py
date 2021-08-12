import json
from typing import Optional, Union, Dict
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from workflow.constants import (
    ALLOWED_FILE_EXTENSIONS,
    CONSOLE_RED_COLOR
)
from workflow.workflow_services import WorkFlowServices
from workflow.serializers import WorkflowSerializer
from workflow.exceptions import (
    FileNotExist,
    InvalidFileExtension,
    InvalidFileStructure,
    InvalidFileContent,
    InvalidWorkflowExecution
)
from workflow.utils import utils as workflow_utils


class WorkflowJsonView(APIView):
    parser_classes = (MultiPartParser, )

    def post(self, request):
        file = request.data.get('file')
        self.check_file_existence(file=file)

        file_content = file.read().decode('utf-8')
        self.check_file_extension(file_name=file.name)

        json_file = self.parse_file_content_to_json(file_content=file_content)
        self.check_file_structure(json_file=json_file)

        account_with_transactions = self.execute_workflow(json_file=json_file)

        return Response(account_with_transactions, status=status.HTTP_200_OK)

    def execute_workflow(
        self,
        *,
        json_file: Dict
    ) -> Union[Dict, InvalidWorkflowExecution]:
        try:
            workflow = WorkFlowServices(json_file=json_file)
            account_with_transactions = workflow.execute_workflow()
        except Exception as workflow_execution_error:
            self.print_error(error=workflow_execution_error)
            raise InvalidWorkflowExecution(workflow_execution_error)
        return account_with_transactions

    @staticmethod
    def parse_file_content_to_json(
        *,
        file_content: str
    ) -> Union[InvalidFileContent, Dict]:
        try:
            json_file = json.loads(file_content)
        except json.decoder.JSONDecodeError:
            raise InvalidFileContent()
        return json_file

    @staticmethod
    def check_file_structure(
        *,
        json_file: Dict
    ) -> Optional[InvalidFileStructure]:
        workflow_serializer = WorkflowSerializer(data=json_file)
        if not workflow_serializer.is_valid():
            raise InvalidFileStructure()
        return None

    @staticmethod
    def check_file_extension(
        *,
        file_name: str
    ) -> Optional[InvalidFileExtension]:
        file_extension = workflow_utils.get_file_extension(file_name=file_name)
        if file_extension not in ALLOWED_FILE_EXTENSIONS:
            raise InvalidFileExtension()
        return None

    @staticmethod
    def check_file_existence(
        *,
        file: MultiPartParser
    ) -> Optional[FileNotExist]:
        if not file:
            raise FileNotExist()
        return None

    @staticmethod
    def print_error(
        *,
        error
    ) -> None:
        string_separator = f"{'*' * 30}\n"
        print(
            f"{string_separator}"
            f"{CONSOLE_RED_COLOR}"
            f'[ERROR] = {error}\n'
            f"{CONSOLE_RED_COLOR}"
            f"{string_separator}\n"
        )
