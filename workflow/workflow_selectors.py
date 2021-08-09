from typing import Optional
from workflow.models import Workflow


def get_workflow_by_id(
    *,
    workflow_id: str
) -> Optional[Workflow]:
    try:
        return Workflow.objects.get(_id=workflow_id)
    except Workflow.DoesNotExist:
        return None
