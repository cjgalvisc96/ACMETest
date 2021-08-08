import logging
from typing import Union
from workflow.utils.get_current_trm import get_current_trm
from workflow.exceptions import (
    AccountWithoutBalance,
    InvalidUserPIN,
    UserNotExists
)
from workflow.models import Workflow

logger = logging.getLogger(__name__)


class WorkFlow:
    def __init__(self, json_file):
        self.json_file = json_file
        self.steps = ''
        self.triggers = ''

    def create_workflow_in_db(self):
        Workflow.objects.create(
            steps=self.json_file['steps'],
            trigger=self.json_file['trigger']
        )


    def execute_workflow(self):
        pass


class Account:

    def check_account(
        self,
        *,
        user_id: str,
        pin: int
    ) -> Union[bool, UserNotExists, InvalidUserPIN]:
        pass

    def check_balance(
        self
    ) -> float:
        pass

    def deposit_money(
        self,
        *,
        amount: float
    ) -> float:
        pass

    def withdraw_money_in_pesos(
        self,
        *,
        amount: float
    ) -> Union[float, AccountWithoutBalance]:
        pass

    def withdraw_money_in_dolars(
        self,
        *,
        amount: float
    ) -> Union[float, AccountWithoutBalance]:
        current_trm = get_current_trm()
        amount_to_withdraw = amount * current_trm
        return amount_to_withdraw
