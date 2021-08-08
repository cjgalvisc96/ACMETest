import json
import logging
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from workflow.error_messages import workflow_errors
from workflow.workflow_services import WorkFlowServices

logger = logging.getLogger(__name__)


class WorkflowJsonView(APIView):
    parser_classes = (MultiPartParser, )

    def post(self, request):
        file = request.data.get('file')
        if not file:
            msg = (
                f"WorkflowJsonView::post() -> "
                f"{workflow_errors.get('required_json_file')}"
            )
            logger.error(msg)
            return Response(
                {"error": msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_content = file.read().decode('utf-8')

        try:
            json_file = json.loads(file_content)
        except json.decoder.JSONDecodeError as error:
            logger.exception(f"WorkflowJsonView::post() -> {error}")
            return Response(
                {"error": workflow_errors.get('invalid_content_json_file')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workflow = WorkFlowServices(json_file=json_file)
            workflow.execute_workflow()
        except Exception as error:
            logger.exception(f"WorkflowJsonView::post() -> {error}")
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(json_file, status=status.HTTP_200_OK)
