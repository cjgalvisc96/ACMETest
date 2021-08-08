import logging
from typing import Optional
from workflow.exceptions import FailedWorkflowDBCreation
from workflow.models import Workflow
from workflow.error_messages import workflow_errors


logger = logging.getLogger(__name__)


class WorkFlowServices:
    def __init__(self, json_file):
        self.json_file = json_file
        self.create_workflow_in_db()
        self.steps = ''
        self.triggers = ''

    def create_workflow_in_db(
        self
    ) -> Optional[FailedWorkflowDBCreation]:
        try:
            Workflow.objects.create(
                steps=self.json_file['steps'],
                trigger=self.json_file['trigger']
            )
        except FailedWorkflowDBCreation as error:
            logger.error(
                f"WorkFlowServices::create_workflow_in_db() -> {error}"
            )
            raise FailedWorkflowDBCreation(workflow_errors['db_creation'])
        return None

    def execute_workflow(self):
        pass
