import requests

from ..exceptions import CiscoSupportApiException


class AccessTokensAPI(object):
    def __init__(self, request_token_url):
        self.request_token_url = request_token_url

    def get(self, client_id, client_secret, grant_type):
        """Get OAuth access token

        Returns:
            str: access token
        """
        if grant_type != "client_credentials":
            raise CiscoSupportApiException(
                "Grant flows other than 'client_credentials' have not been implemented yet"
            )

        response = requests.post(
            self.request_token_url,
            params={
                "client_id": client_id,
                "client_secret": client_secret,
            },
            data={"grant_type": grant_type},
        )

        data = response.json()
        return data.get("access_token")
