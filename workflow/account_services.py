from datetime import datetime
from typing import Union, Dict, Optional
from workflow.utils import utils as workflow_utils
from workflow.exceptions import (
    AccountWithoutBalance,
    InvalidUserPIN,
    UserNotExists,
    FailedAccountDBUpdate
)
from workflow.constants import MINIMUM_BALANCE
from workflow.error_messages import account_errors
from workflow import account_selectors
from workflow.decorators import print_action_decorator


class AccountServices:
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id

    @print_action_decorator
    def validate_account(
        self,
        *,
        user_filter: Dict
    ) -> Union[bool, UserNotExists, InvalidUserPIN]:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        if not account_qry.exists():
            msg = account_errors['user_not_exists'].format(
                user_filter['user_id']
            )
            raise UserNotExists(msg)

        account = account_qry.first()

        is_valid_pin = (
            True if account.user['pin'] == user_filter['pin'] else False
        )
        if not is_valid_pin:
            msg = account_errors['invalid_pin'].format(
                user_filter['pin'], user_filter['user_id']
            )
            raise InvalidUserPIN(msg)

        transaction = dict(
            action='validate_account',
            old_balance=account.balance,
            balance_after_transaction=account.balance
        )
        self.create_transaction_in_account(
            user_filter=user_filter,
            transaction=transaction
        )
        return True

    @print_action_decorator
    def get_account_balance(
        self,
        *,
        user_filter: Dict
    ) -> Union[float, AccountWithoutBalance]:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        account = account_qry.first()

        transaction = dict(
            action='get_account_balance',
            old_balance=account.balance,
            balance_after_transaction=account.balance
        )
        self.create_transaction_in_account(
            user_filter=user_filter,
            transaction=transaction
        )
        return account.balance

    @print_action_decorator
    def deposit_money(
        self,
        *,
        user_filter: Dict,
        amount_to_deposit: float
    ) -> float:
        account_qry = account_selectors.filter_account_by_user(
            user_filter=user_filter
        )
        account = account_qry.first()
        current_balance = account.balance
        account.balance = current_balance + amount_to_deposit
        account.save()

        transaction = dict(
            action='deposit_money',
            old_balance=current_balance,
            balance_after_transaction=account.balance
        )
        self.create_transaction_in_account(
            user_filter=user_filter,
            transaction=transaction
        )
        return account.balance

    @print_action_decorator
    def withdraw_in_pesos(
        self,
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
            raise AccountWithoutBalance(msg)

        account.balance = new_balance
        account.save()

        transaction = dict(
            action='withdraw_in_pesos',
            old_balance=current_balance,
            balance_after_transaction=account.balance
        )
        self.create_transaction_in_account(
            user_filter=user_filter,
            transaction=transaction
        )
        return account.balance

    @print_action_decorator
    def withdraw_in_dollars(
        self,
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
            raise AccountWithoutBalance(msg)

        account.balance = new_balance
        account.save()

        transaction = dict(
            action='withdraw_in_dollars',
            old_balance=current_balance,
            balance_after_transaction=account.balance
        )
        self.create_transaction_in_account(
            user_filter=user_filter,
            transaction=transaction
        )
        return account.balance

    def create_transaction_in_account(
        self,
        *,
        user_filter: Dict,
        transaction: Dict
    ) -> Optional[FailedAccountDBUpdate]:
        current_datetime = datetime.now()
        transaction['workflow_id'] = self.workflow_id
        transaction['date'] = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
        try:
            account_qry = account_selectors.filter_account_by_user(
                    user_filter=user_filter
                )
            account = account_qry.first()
            account.transactions += [transaction]
            account.save()
        except FailedAccountDBUpdate:
            msg = account_errors['db_update']
            raise FailedAccountDBUpdate(msg)
        return None
