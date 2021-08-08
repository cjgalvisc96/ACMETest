import logging
from treelib import Tree
from typing import Optional, Dict, List, Union
from workflow.exceptions import FailedWorkflowDBCreation
from workflow.models import Workflow
from workflow.error_messages import workflow_errors
from workflow.account_services import AccountServices
from workflow.constants import OPERATORS_CONVERSIONS
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
        #self.account_services.validate_account(user=self.user)
        execution_workflow_tree = self.create_execution_workflow_tree()
        logger.info(execution_workflow_tree.show(line_type="ascii-em"))
        return

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

    @staticmethod
    def check_if_all_transition_conditions_are_valid(
        *,
        conditions: List[Dict],
        result: Union[bool, float]
    ) -> bool:
        conditions_results = []
        for condition in conditions:
            check_condition = (
                eval(
                    f"{result} "
                    f"{OPERATORS_CONVERSIONS[condition['operator']]} "
                    f"{condition['value']}"
                )
            )
            conditions_results.append(check_condition)

        all_conditions_are_valid = (
             all(
                 condition_result is True for condition_result in
                 conditions_results
             )
         )
        return all_conditions_are_valid

    def create_execution_workflow_tree(
        self
    ) -> Tree:
        """
            This method transform the "transitions"
            in a "General Tree" using "treelib" library
            Example:
                Validate_account
                ╚══ Account_balance
                    ╠══ Deposit_200
                    ║   ╚══ Account_balance_200
                    ║       ╚══ Withdraw_50
                    ║           ╚══ Account_balance_end_50
                    ╚══ Withdraw_30
                        ╚══ Account_balance_end_30
        """
        execution_workflow_tree = Tree()
        for step in self.steps:
            self.get_transitions(
                root_name=step['id'],
                execution_workflow_tree=execution_workflow_tree,
                transitions=step['transitions']
            )
        return execution_workflow_tree

    def get_transitions(
        self,
        *,
        root_name: str,
        execution_workflow_tree: Tree,
        transitions: List[Dict]
    ) -> None:
        if not transitions:
            return

        if not execution_workflow_tree.get_node(root_name):
            execution_workflow_tree.create_node(
                tag=root_name.capitalize(),
                identifier=root_name
            )
        for transition in transitions:
            son_name = transition['target']
            if not execution_workflow_tree.get_node(son_name):
                execution_workflow_tree.create_node(
                    tag=son_name.capitalize(),
                    identifier=son_name,
                    parent=root_name
                )
                target_transitions = self.found_step_by_id_in_steps_and_trigger(
                    step_id=son_name
                )
                return self.get_transitions(
                    root_name=son_name,
                    execution_workflow_tree=execution_workflow_tree,
                    transitions=target_transitions['transitions']
                )

