from typing import Optional, Dict
from workflow.models import Account


def filter_account_by_user(
    *,
    user_filter: Dict
) -> Optional[Account]:
    return Account.objects.filter(
        user=user_filter
    )
