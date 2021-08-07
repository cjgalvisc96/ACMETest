import logging
from typing import Union
from workflow.utils.get_current_trm import get_current_trm
from workflow.exceptions import (
    AccountWithoutBalance,
    InvalidUserPIN,
    UserNotExists
)

logger = logging.getLogger(__name__)


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
