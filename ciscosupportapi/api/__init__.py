import logging
import os

import requests

from ciscosupportapi.config import (
    ACCESS_TOKEN_ENVIRONMENT_VARIABLE,
    DEFAULT_BASE_URL,
    REQUEST_TOKEN_URL,
)

from ..exceptions import CiscoSupportApiException
from .auth import AccessTokensAPI
from .bug import BugV2API
from .eox import EoXAPI
from .software_suggestions import SoftwareSuggestionV2API

logger = logging.getLogger(__name__)


class CiscoSupportApi(object):
    def __init__(
        self,
        access_token=None,
        base_url=DEFAULT_BASE_URL,
        request_token_url=REQUEST_TOKEN_URL,
        client_id=None,
        client_secret=None,
        grant_type="client_credentials",
        caller=None,
    ):
        access_token = access_token or os.environ.get(ACCESS_TOKEN_ENVIRONMENT_VARIABLE)

        self.access_tokens = AccessTokensAPI(request_token_url=REQUEST_TOKEN_URL)
        access_token = self.access_tokens.get(client_id, client_secret, grant_type)

        if not access_token:
            raise CiscoSupportApiException(
                "You must provide an access token or oauth credentials."
            )

        self._session = requests.session()
        self._session.headers.update(
            {
                "Authorization": "Bearer " + access_token,
                "Content-type": "application/json;charset=utf-8",
            }
        )

        self.software_suggestions = SoftwareSuggestionV2API(
            session=self._session, base_url=base_url
        )
        self.bug = BugV2API(session=self._session, base_url=base_url)
        self.eox = EoXAPI(session=self._session, base_url=base_url)

    def close(self):
        self._session.close()
