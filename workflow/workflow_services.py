from treelib import Tree
from typing import Dict, List, Union
from workflow.exceptions import (
    WorkflowExceptions,
    FailedWorkflowDBCreation,
    InvalidStepConditions
)
from workflow.models import Workflow
from workflow.error_messages import workflow_errors
from workflow.account_services import AccountServices
from workflow import account_selectors
from workflow.constants import (
    OPERATORS_CONVERSIONS,
    CONSOLE_YELLOW_COLOR
)


class WorkFlowServices:
    def __init__(self, json_file):
        self.json_file = json_file
        self.steps = self.json_file['steps']
        self.trigger = self.json_file['trigger']
        self.workflow_id = self.create_workflow_in_db()
        self.account_services = AccountServices(
            workflow_id=self.workflow_id
        )
        self.actions_results = dict(
            validate_account=False,
            account_balance=0.0,
            deposit_money=0.0,
            withdraw_in_dollars=0.0,
            withdraw_in_pesos=0.0
        )

    def create_workflow_in_db(
        self
    ) -> Union[str, FailedWorkflowDBCreation]:
        try:
            workflow = Workflow.objects.create(
                steps=self.json_file['steps'],
                trigger=self.json_file['trigger']
            )
        except FailedWorkflowDBCreation:
            msg = workflow_errors['db_creation']
            raise FailedWorkflowDBCreation(msg)
        return str(workflow._id)

    def execute_workflow(
        self
    ) -> Union[WorkflowExceptions, Dict]:
        execution_workflow_tree = self.create_execution_workflow_tree()
        print(f"{CONSOLE_YELLOW_COLOR}EXECUTION WORKFLOW TREE")
        execution_workflow_tree.show(line_type='ascii-em')  # Print Tree
        # The tree is traversed using the "DEPTH" technique
        for node in execution_workflow_tree.expand_tree(sorting=True):
            current_node = execution_workflow_tree.get_node(nid=node)
            step_to_execute = self.found_step(step_id=current_node.identifier)
            action = step_to_execute['action']
            step_params = self.get_step_params_values(
                step_params=step_to_execute['params']
            )
            user_filter = {'user_id': step_params['user_id']}
            node_parent = execution_workflow_tree.parent(
                nid=current_node.identifier
            )
            if node_parent:  # Is necessary check conditions
                transition = self.found_transition_in_step(
                    step_id=node_parent.identifier,
                    transition_id=step_to_execute['id']
                )
                all_transition_conditions_are_valid = self. \
                    check_if_all_transition_conditions_are_valid(
                        conditions=transition['condition']
                    )
                if not all_transition_conditions_are_valid:
                    msg = workflow_errors['invalid_step_conditions'].format(
                        transition['condition'],
                        node_parent.identifier,
                        step_to_execute['id']
                    )
                    raise InvalidStepConditions(msg)

            if action == "validate_account":
                user_filter['pin'] = step_params['pin']
                self.actions_results["validate_account"] = (
                    self.account_services.validate_account(
                        user_filter=user_filter
                    )
                )

            if action == "get_account_balance":
                self.actions_results["account_balance"] = (
                    self.account_services.get_account_balance(
                        user_filter=user_filter
                    )
                )

            if action == "deposit_money":
                self.actions_results["deposit_money"] = (
                    self.account_services.deposit_money(
                        user_filter=user_filter,
                        amount_to_deposit=step_params['money']
                    )
                )

            if action == "withdraw_in_dollars":
                self.actions_results["withdraw_in_dollars"] = (
                    self.account_services.withdraw_in_dollars(
                        user_filter=user_filter,
                        amount_to_withdraw=step_params['money']
                    )
                )

            if action == "withdraw_in_pesos":
                self.actions_results["withdraw_in_pesos"] = (
                    self.account_services.withdraw_in_pesos(
                        user_filter=user_filter,
                        amount_to_withdraw=step_params['money']
                    )
                )

        account_qry = account_selectors.filter_account_by_user(
            user_filter=self.trigger['params']
        )
        account = account_qry.first()
        account_with_transactions = dict(
            balance=account.balance,
            user=account.user,
            transactions=account.transactions
        )
        return account_with_transactions

    def get_step_params_values(
        self,
        *,
        step_params: Dict
    ) -> Dict:
        params_results = {}
        for param_key, param_values in step_params.items():
            if not param_values['from_id']:
                params_results[param_key] = param_values['value']
            else:
                # For params with step reference
                reference_step = self.found_step(
                    step_id=param_values['from_id']
                )
                params_results[param_key] = (
                    reference_step['params'][param_key]
                )
        
        return params_results

    def found_step(
        self,
        *,
        step_id: str
    ) -> Dict:
        """
            This method return the step find by "id" in 'steps' and 'trigger'
        """
        filter_step = list(filter(
            lambda step: step['id'] == step_id, self.steps
        ))
        if not filter_step:
            return self.trigger  # Because the step is the trigger
        return filter_step[0]

    def create_execution_workflow_tree(
        self
    ) -> Tree:
        """
            This method transform the "transitions"
            in a "General Tree" using "treelib" library
            Example:
                Validate_account
                ????????? Account_balance
                    ????????? Deposit_200
                    ???   ????????? Account_balance_200
                    ???       ????????? Withdraw_50
                    ???           ????????? Account_balance_end_50
                    ????????? Withdraw_30
                        ????????? Account_balance_end_30
        """
        execution_workflow_tree = Tree()
        for step in self.steps:
            self.get_recursive_transitions(
                parent_node_name=step['id'],
                execution_workflow_tree=execution_workflow_tree,
                step_transitions=step['transitions']
            )
        return execution_workflow_tree

    def get_recursive_transitions(
        self,
        *,
        parent_node_name: str,
        execution_workflow_tree: Tree,
        step_transitions: List[Dict]
    ) -> None:
        """
            This is a RECURSIVE method for get all nested transitions
        """
        if not step_transitions:
            return

        if not execution_workflow_tree.get_node(parent_node_name):
            execution_workflow_tree.create_node(
                tag=parent_node_name.capitalize(),
                identifier=parent_node_name
            )
        for step_transition in step_transitions:
            son_node_name = step_transition['target']
            if not execution_workflow_tree.get_node(son_node_name):
                execution_workflow_tree.create_node(
                    tag=son_node_name.capitalize(),
                    identifier=son_node_name,
                    parent=parent_node_name
                )
                target_transitions = self.found_step(step_id=son_node_name)
                return self.get_recursive_transitions(
                    parent_node_name=son_node_name,
                    execution_workflow_tree=execution_workflow_tree,
                    step_transitions=target_transitions['transitions']
                )

    def check_if_all_transition_conditions_are_valid(
        self,
        *,
        conditions: List[Dict]
    ) -> bool:
        conditions_results = list()
        for condition in conditions:
            result = self.actions_results[condition['from_id']]
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

    def found_transition_in_step(
        self,
        *,
        step_id: str,
        transition_id: str
    ) -> Dict:
        """
            This method return the transition find by "target" in specific
            'step'
        """
        filter_step = list(filter(
            lambda step: step['id'] == step_id, self.steps
        ))
        step_found = filter_step[0]
        filter_transition = list(filter(
            lambda transition: transition['target'] == transition_id,
            step_found['transitions']
        ))
        return filter_transition[0]
