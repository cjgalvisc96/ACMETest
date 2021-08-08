class WorkflowExceptions(Exception):
    pass


class UserNotExists(WorkflowExceptions):
    pass


class InvalidUserPIN(WorkflowExceptions):
    pass


class AccountWithoutBalance(WorkflowExceptions):
    pass


class FailedTRMService(WorkflowExceptions):
    pass


class FailedWorkflowDBCreation(WorkflowExceptions):
    pass


class FailedAccountDBCreation(WorkflowExceptions):
    pass
