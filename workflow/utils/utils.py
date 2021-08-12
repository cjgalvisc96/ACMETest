import requests
from typing import Union
from datetime import datetime
from workflow.constants import TRM_SERVICE_URL
from workflow.exceptions import FailedTRMService
from workflow.error_messages import external_services_errors


def get_current_trm() -> Union[float, FailedTRMService]:
    current_date = datetime.today().strftime('%Y-%m-%d')
    year, month, day = current_date.split('-')
    try:
        trm_service_request = requests.get(
            TRM_SERVICE_URL.format(year, month, day)
        )
        trm_service_response = trm_service_request.json()
        current_trm = trm_service_response['data']['value']
        return current_trm
    except FailedTRMService as trm_service_error:
        msg = external_services_errors['trm_service_failed'].format(
            trm_service_error
        )
        raise FailedTRMService(msg)


def get_file_extension(
    file_name: str
) -> str:
    split_file_name = file_name.split('.')
    return split_file_name[-1]
