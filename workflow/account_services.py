import logging
from typing import Union, List, Dict, Optional
from workflow.utils import utils as workflow_utils
from workflow.exceptions import (
    AccountWithoutBalance,
    InvalidUserPIN,
    UserNotExists,
    FailedAccountDBCreation,
    FailedAccountDBUpdate
)
from workflow.constants import MINIMUM_BALANCE
from workflow.error_messages import account_errors
from workflow import account_selectors
from workflow.models import Account

logger = logging.getLogger(__name__)


class AccountServices:

    @staticmethod
    def validate_account(
        *,
        user: Dict
    ) -> Union[bool, UserNotExists, InvalidUserPIN]:
        user_id = user['user_id']
        pin = user['pin']
        account_by_user_id = account_selectors.get_account_by_user_id(
            user_id=user_id
        )
        if not account_by_user_id:
            msg = account_errors['user_not_exists'].format(user_id)
            logger.exception(f"AccountServices::validate_account() -> {msg}")
            raise UserNotExists(msg)

        is_valid_pin = True if account_by_user_id.user.pin == pin else False

        if not is_valid_pin:
            msg = account_errors['invalid_pin'].format(pin, user_id)
            logger.exception(f"AccountServices::validate_account() -> {msg}")
            raise InvalidUserPIN(msg)

        return True

    @staticmethod
    def get_account_balance(
        *,
        user: Dict,
        workflow_id: str
    ) -> Union[float, AccountWithoutBalance]:
        account = account_selectors. \
            get_account_by_user_id_and_pin_and_workflow_id(
                user_id=user['user_id'],
                pin=user['pin'],
                workflow_id=workflow_id
            )
        return account.balance

    @staticmethod
    def deposit_money(
        *,
        amount_to_deposit: float,
        user: Dict,
        workflow_id: str
    ) -> Union[float, AccountWithoutBalance]:
        account = account_selectors. \
            get_account_by_user_id_and_pin_and_workflow_id(
                user_id=user['user_id'],
                pin=user['pin'],
                workflow_id=workflow_id
            )
        account.balance += amount_to_deposit
        account.save()
        return account.balance

    @staticmethod
    def withdraw_in_pesos(
        *,
        amount_to_withdraw: float,
        user: Dict,
        workflow_id: str
    ) -> Union[float, AccountWithoutBalance]:
        account = account_selectors. \
            get_account_by_user_id_and_pin_and_workflow_id(
                user_id=user['user_id'],
                pin=user['pin'],
                workflow_id=workflow_id
            )
        current_balance = account.balance
        new_balance = current_balance - amount_to_withdraw
        if new_balance < MINIMUM_BALANCE:
            currency = "COP"
            msg = account_errors['account_without_balance'].format(
                amount_to_withdraw, currency
            )
            logger.error(f"AccountServices::withdraw_in_pesos() -> {msg}")
            raise AccountWithoutBalance(msg)

        account.balance = new_balance
        account.save()

        return account.balance

    @staticmethod
    def withdraw_in_dollars(
        *,
        amount_to_withdraw: float,
        user: Dict,
        workflow_id: str
    ) -> Union[float, AccountWithoutBalance]:
        account = account_selectors. \
            get_account_by_user_id_and_pin_and_workflow_id(
                user_id=user['user_id'],
                pin=user['pin'],
                workflow_id=workflow_id
            )
        current_balance = account.balance
        current_trm = workflow_utils.get_current_trm()
        new_balance = current_balance - (amount_to_withdraw * current_trm)
        if new_balance < MINIMUM_BALANCE:
            currency = "USD"
            msg = account_errors['account_without_balance'].format(
                amount_to_withdraw, currency
            )
            logger.error(
                f"AccountServices::withdraw_in_dollars() -> {msg}"
            )
            raise AccountWithoutBalance(msg)

        account.balance = new_balance
        account.save()

        return account.balance

    @staticmethod
    def create_account_in_db(
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

    @staticmethod
    def create_transaction_in_account(
        *,
        user: Dict,
        transaction: Dict,
        workflow_id: str
    ) -> Optional[FailedAccountDBCreation]:
        try:
            account = account_selectors.\
                get_account_by_user_id_and_pin_and_workflow_id(
                    user_id=user['user_id'],
                    pin=user['pin'],
                    workflow_id=workflow_id
                )
            account.transactions += [transaction]
            account.save()
        except FailedAccountDBUpdate as error:
            logger.error(
                f"AccountServices::create_transaction_in_account() -> {error}"
            )
            raise FailedAccountDBUpdate(account_errors['db_update'])
        return None
