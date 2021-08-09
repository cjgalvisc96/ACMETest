workflow_errors = {
    "required_json_file": "The Workflow json file is required",
    "invalid_file_extension": (
        "The extension file is invalid, only 'json' extension is allow"
    ),
    "invalid_structure_json_file": (
        "The Workflow structure json file is invalid"
    ),
    "invalid_content_json_file": "The Workflow content json file is invalid",
    "db_creation": (
        "An error occurred while trying to create the Workflow in the db "
    ),
    "invalid_workflow_execution": (
        "One error happened during workflow execution"
    ),
    "failed_step_conditions": (
        "The conditions **{0}** of parent node **'{1}'** "
        "are not met to pass the node **'{2}'**"
    )
}

account_errors = {
    "user_not_exists": "User with id {0} don't exists in db",
    "invalid_pin": "The pin {0} is invalid for user with id {0}",
    "account_without_balance": (
        "If you withdraw {0} {1} ({2} COP) from the "
        "account this don't will have balance"
    ),
    "db_update": "Account can't update in DB"
}
