from typing import Optional
from workflow.models import Account


def get_account_by_user_id(
    *,
    user_id: str
) -> Optional[Account]:
    try:
        return Account.objects.get(
            user__user_id=user_id
        )
    except Account.DoesNotExist:
        return None


def get_account_by_user_id_and_pin(
    *,
    user_id: str,
    pin: int
) -> Optional[Account]:
    try:
        return Account.objects.get(
            user__user_id=user_id,
            user__pin=pin
        )
    except Account.DoesNotExist:
        return None
