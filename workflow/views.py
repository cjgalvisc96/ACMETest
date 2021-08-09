import json
import logging
from typing import Optional, Union, Dict
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from workflow.constants import ALLOWED_FILE_EXTENSIONS
from workflow.error_messages import workflow_errors
from workflow.workflow_services import WorkFlowServices
from workflow.serializers import WorkflowSerializer
from workflow.success_messages import workflow_success_messages
from workflow.exceptions import (
    FileNotExist,
    InvalidFileExtension,
    InvalidFileStructure,
    InvalidFileContent,
    InvalidWorkflowExecution
)
from workflow.utils import utils as workflow_utils

logger = logging.getLogger(__name__)


class WorkflowJsonView(APIView):
    parser_classes = (MultiPartParser, )

    def post(self, request):
        file = request.data.get('file')
        self.check_file_existence(file=file)
        file_content = file.read().decode('utf-8')
        self.check_file_extension(file_name=file.name)

        json_file = self.parse_file_content_to_json(file_content=file_content)
        self.check_file_structure(json_file=json_file)

        self.execute_workflow(json_file=json_file)
        return Response(
            {
                "success": workflow_success_messages['success_workflow_execution']
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def execute_workflow(
        json_file
    ) -> Optional[Response]:
        try:
            workflow = WorkFlowServices(json_file=json_file)
            workflow.execute_workflow()
        except Exception as error:
            logger.exception(f"WorkflowJsonView::execute_workflow() -> {error}")
            raise InvalidWorkflowExecution()
        return None

    @staticmethod
    def parse_file_content_to_json(
        *,
        file_content: str
    ) -> Union[InvalidFileContent, Dict]:
        try:
            json_file = json.loads(file_content)
        except json.decoder.JSONDecodeError as error:
            logger.exception(
                f"WorkflowJsonView::parse_file_content_to_json() -> {error}"
            )
            raise InvalidFileContent()
        return json_file

    @staticmethod
    def check_file_structure(
        *,
        json_file: Dict
    ) -> Optional[InvalidFileStructure]:
        workflow_serializer = WorkflowSerializer(data=json_file)
        if not workflow_serializer.is_valid():
            logger.error(
                f"WorkflowJsonView::check_file_structure() -> "
                f"-> {workflow_serializer.errors}"
            )
            raise InvalidFileStructure()
        return None

    @staticmethod
    def check_file_extension(
        *,
        file_name: str
    ) -> Optional[InvalidFileExtension]:
        file_extension = workflow_utils.get_file_extension(file_name=file_name)
        if file_extension not in ALLOWED_FILE_EXTENSIONS:
            logger.error(
                f"WorkflowJsonView::check_file_extension() -> "
                f"{workflow_errors.get('invalid_file_extension')}"
            )
            raise InvalidFileExtension()
        return None

    @staticmethod
    def check_file_existence(
        *,
        file: MultiPartParser
    ) -> Optional[FileNotExist]:
        if not file:
            logger.error(
                f"WorkflowJsonView::check_file_existence() -> "
                f"{workflow_errors.get('required_json_file')}"
            )
            raise FileNotExist()
        return None
