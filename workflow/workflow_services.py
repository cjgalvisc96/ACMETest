import logging
from typing import Optional, Dict, List
from workflow.exceptions import FailedWorkflowDBCreation
from workflow.models import Workflow
from workflow.error_messages import workflow_errors
from workflow.account_services import AccountServices

logger = logging.getLogger(__name__)


class WorkFlowServices:
    def __init__(self, json_file):
        self.json_file = json_file
        self.steps = self.json_file['steps']
        self.trigger = self.json_file['trigger']
        self.total_steps = len(self.json_file['steps'])
        self.user = {
            "user_id": self.trigger['params']['user_id'],
            "pin": self.trigger['params']['pin']
        }
        self.create_workflow_in_db()
        self.account_services = AccountServices()

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
        """
            By default the first element is always 'validate_account' using
            triggers params
        """
        self.account_services.validate_account(user=self.user)
        for step in self.steps:
            params = self.get_params_values(params=step['params'])
            for transition in step['transition']:
                pass

    def get_params_values(
        self,
        *,
        params: Dict
    ) -> Dict:
        params_results = {}
        for param_key, param_values in params.items():
            if not param_values['from_id']:
                params_results[param_key] = param_values['value']
            else:
                # For params with step reference
                reference_step = self.found_step_by_id_in_steps_and_trigger(
                    step_id=param_values['from_id']
                )
                params_results[param_key] = (
                    reference_step['params'][param_key]
                )
        
        return params_results

    def found_step_by_id_in_steps_and_trigger(
        self,
        *,
        step_id: str
    ) -> Dict:
        filter_step = list(filter(
            lambda step: step['id'] == step_id, self.steps
        ))
        if not filter_step:
            return self.trigger # Is because the step is the trigger
        return filter_step[0]

    def check_transition_conditions(
        self,
        *,
        conditions: List[Dict]
    ) -> None:
        for condition in conditions:
            pass
