import logging
from typing import Optional
from workflow.exceptions import FailedWorkflowDBCreation
from workflow.models import Workflow
from workflow.error_messages import workflow_errors


logger = logging.getLogger(__name__)


class WorkFlowServices:
    def __init__(self, json_file):
        self.json_file = json_file
        self.steps = self.json_file['steps']
        self.trigger = self.json_file['trigger']
        self.total_steps = len(self.json_file['steps'])
        self.user_id = self.get_user_id_from_trigger()
        self.pin = self.get_pin_from_trigger()
        self.create_workflow_in_db()

    def get_user_id_from_trigger(
        self
    ) -> Optional[str]:
        if 'user_id' in self.trigger['params'].keys():
            return self.trigger['params']['user_id']
        return None

    def get_pin_from_trigger(
        self
    ) -> Optional[int]:
        if 'pin' in self.trigger['params'].keys():
            return self.trigger['params']['pin']
        return None

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
