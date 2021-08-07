from json.decoder import JSONDecodeError


class WorkflowExceptions(Exception):
    pass


class InvalidWorkflowJsonFile(JSONDecodeError, Exception):
    pass
