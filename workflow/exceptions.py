from rest_framework.exceptions import APIException
from rest_framework import status
from workflow.error_messages import workflow_errors


class WorkflowExceptions(Exception):
    pass


class UserNotExists(WorkflowExceptions):
    pass


class InvalidUserPIN(WorkflowExceptions):
    pass


class AccountWithoutBalance(WorkflowExceptions):
    pass


class FailedTRMService(WorkflowExceptions):
    pass


class FailedWorkflowDBCreation(WorkflowExceptions):
    pass


class FailedAccountDBUpdate(WorkflowExceptions):
    pass


class FileNotExist(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = workflow_errors.get('required_json_file')


class InvalidFileExtension(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = workflow_errors.get('invalid_file_extension')


class InvalidFileStructure(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = workflow_errors.get('invalid_structure_json_file')


class InvalidFileContent(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = workflow_errors.get('invalid_content_json_file')


class InvalidWorkflowExecution(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = workflow_errors.get('invalid_workflow_execution')
