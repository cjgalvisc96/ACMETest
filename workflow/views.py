import json
import logging
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from workflow.error_messages import workflow_errors
from workflow.services import WorkFlow

logger = logging.getLogger(__name__)


class WorkflowJsonView(APIView):
    parser_classes = (MultiPartParser, )

    def post(self, request):
        file = request.data.get('file')
        if not file:
            return Response(
                {"error": workflow_errors.get('required_json_file')},
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

        workflow = WorkFlow(json_file=json_file)
        workflow.create_workflow_in_db()

        return Response(json_file, status=status.HTTP_200_OK)
