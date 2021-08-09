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
        user_filter: Dict
    ) -> Union[bool, UserNotExists, InvalidUserPIN]:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        if not account_qry.exists():
            msg = account_errors['user_not_exists'].format(user_filter['user_id'])
            logger.exception(f"AccountServices::validate_account() -> {msg}")
            raise UserNotExists(msg)

        account = account_qry.first()
        is_valid_pin = True if account.user['pin'] == user_filter['pin'] else False

        if not is_valid_pin:
            msg = account_errors['invalid_pin'].format(
                user_filter['pin'], user_filter['user_id']
            )
            logger.exception(f"AccountServices::validate_account() -> {msg}")
            raise InvalidUserPIN(msg)

        return True

    @staticmethod
    def get_account_balance(
        *,
        user_filter: Dict
    ) -> Union[float, AccountWithoutBalance]:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        account = account_qry.first()
        current_balance = account.balance
        return current_balance

    @staticmethod
    def deposit_money(
        *,
        user_filter: Dict,
        amount_to_deposit: float
    ) -> float:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        account = account_qry.first()
        account.balance += amount_to_deposit
        account.save()
        new_balance = account.balance
        return new_balance

    @staticmethod
    def withdraw_in_pesos(
        *,
        user_filter: Dict,
        amount_to_withdraw: float
    ) -> Union[float, AccountWithoutBalance]:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        account = account_qry.first()
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
        user_filter: Dict,
        amount_to_withdraw: float
    ) -> Union[float, AccountWithoutBalance]:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        account = account_qry.first()
        current_balance = account.balance
        current_trm = workflow_utils.get_current_trm()
        amount_dollars_to_pesos = amount_to_withdraw * current_trm
        new_balance = current_balance - amount_dollars_to_pesos
        if new_balance < MINIMUM_BALANCE:
            currency = "USD"
            msg = account_errors['account_without_balance'].format(
                amount_to_withdraw, currency, amount_dollars_to_pesos
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
