import logging
from typing import Union, List, Dict, Optional
from workflow.utils.get_current_trm import get_current_trm
from workflow.exceptions import (
    AccountWithoutBalance,
    InvalidUserPIN,
    UserNotExists,
    FailedAccountDBCreation
)
from workflow.constants import MINIMUM_BALANCE
from workflow.error_messages import account_errors
from workflow import account_selectors
from workflow.models import Account
logger = logging.getLogger(__name__)


class AccountServices:

    """
    def __init__(self, user_id, pin):
        self.user_id = user_id
        self.pin = pin
    """

    def create_account_in_db(
        self,
        *,
        user: Dict,
        transactions: List[Dict],
        workflow_id: str
    ) -> Optional[FailedAccountDBCreation]:
        try:
            Account.objects.create(
                workflow_id=workflow_id,
                user=user,
                transactions=transactions
            )
        except FailedAccountDBCreation as error:
            logger.error(f"AccountServices::create_account_in_db() -> {error}")
            raise FailedAccountDBCreation(account_errors['db_creation'])
        return None

    def check_account(
        self,
        *,
        user_id: str,
        pin: int
    ) -> Union[bool, UserNotExists, InvalidUserPIN]:
        account_by_user_id = account_selectors.get_account_by_user_id(
            user_id=user_id
        )
        if not account_by_user_id:
            msg = account_errors['user_not_exists'].format(user_id)
            logger.exception(f"AccountServices::check_account() -> {msg}")
            raise UserNotExists(msg)

        is_valid_pin = True if account_by_user_id.user.pin == pin else False

        if not is_valid_pin:
            msg = account_errors['invalid_pin'].format(pin, user_id)
            logger.exception(f"AccountServices::check_account() -> {msg}")
            raise InvalidUserPIN(msg)

        return True

    def check_balance(
        self,
        user_id: str,
        pin: int
    ) -> float:
        account = account_selectors.get_account_by_user_id_and_pin(
            user_id=user_id,
            pin=pin
        )
        return account.balance

    def deposit_money(
        self,
        *,
        amount: float,
        user_id: str,
        pin: int
    ) -> float:
        account = account_selectors.get_account_by_user_id_and_pin(
            user_id=user_id,
            pin=pin
        )
        account.balance += amount
        account.save()
        return account.balance

    def withdraw_money_in_pesos(
        self,
        *,
        amount_to_withdraw: float,
        user_id: str,
        pin: int
    ) -> Union[float, AccountWithoutBalance]:
        account = account_selectors.get_account_by_user_id_and_pin(
            user_id=user_id,
            pin=pin
        )
        current_balance = account.balance
        new_balance = current_balance - amount_to_withdraw
        if new_balance < MINIMUM_BALANCE:
            currency = "COP"
            msg = account_errors['account_without_balance'].format(
                amount_to_withdraw, currency
            )
            logger.error(f"AccountServices::withdraw_money_in_pesos() -> {msg}")
            raise AccountWithoutBalance(msg)

        account.balance = new_balance
        account.save()

        return account.balance

    def withdraw_money_in_dolars(
        self,
        *,
        amount_to_withdraw: float,
        user_id: str,
        pin: int
    ) -> Union[float, AccountWithoutBalance]:
        account = account_selectors.get_account_by_user_id_and_pin(
            user_id=user_id,
            pin=pin
        )
        current_balance = account.balance
        current_trm = get_current_trm()
        new_balance = current_balance - (amount_to_withdraw * current_trm)
        if new_balance < MINIMUM_BALANCE:
            currency = "USD"
            msg = account_errors['account_without_balance'].format(
                amount_to_withdraw, currency
            )
            logger.error(
                f"AccountServices::withdraw_money_in_dolars() -> {msg}"
            )
            raise AccountWithoutBalance(msg)

        account.balance = new_balance
        account.save()

        return account.balance
