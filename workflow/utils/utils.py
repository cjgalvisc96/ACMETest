import logging
import requests
from typing import Union
from datetime import datetime
from workflow.constants import TRM_SERVICE_URL
from workflow.exceptions import FailedTRMService

logger = logging.getLogger(__name__)


def get_current_trm() -> Union[float, FailedTRMService]:
    current_date = datetime.today().strftime('%Y-%m-%d')
    year, month, day = current_date.split('-')
    try:
        trm_service_request = requests.get(
            TRM_SERVICE_URL.format(year, month, day)
        )
        trm_service_response = trm_service_request.json()
        trm = trm_service_response['data']['value']
        return trm
    except FailedTRMService as error:
        logging.error(f"get_current_trm() -> {error}")


def get_file_extension(
    file_name: str
) -> str:
    split_file_name = file_name.split('.')
    return split_file_name[-1]
