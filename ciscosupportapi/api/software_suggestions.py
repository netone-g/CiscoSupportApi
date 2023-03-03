import itertools
import logging

from requests.exceptions import HTTPError

from ..exceptions import CiscoSupportApiException
from ..utility import filter_none_value_keys, split_list

logger = logging.getLogger(__name__)

API_PATH = "software/suggestion/v2/suggestions/"


class SoftwareSuggestionV2API(object):
    """Software Suggestion API
    https://developer.cisco.com/docs/support-apis/#!software-suggestion

    """

    def __init__(self, session, base_url):
        self._session = session
        self._base_url = base_url + API_PATH
        logger.debug("SoftwareSuggestionV2API initialized")

    def __paginated_request(
        self, method, path, result_list_name: str = "productList", params: dict = {}
    ):
        next_index = None
        results = []
        _params = {}
        _params.update(params)
        while True:
            if next_index:
                _params["pageIndex"] = next_index
            response = self._session.request(
                method, self._base_url + path, params=_params
            )
            result = response.json()
            # logger.debug(result)
            try:
                response.raise_for_status()
            except HTTPError as e:
                logger.error(str(e))
                if "error" in result:
                    raise CiscoSupportApiException(result["error"])
                raise e
            if result["status"] != "Success":
                raise Exception(f'{result["status"]}: {result["errorDetailsResponse"]}')
            results.append(result[result_list_name])

            pagination = result["paginationResponseRecord"]
            # logger.debug(pagination)
            if int(pagination["pageIndex"]) >= int(pagination["lastIndex"]):
                break
            next_index = int(pagination["pageIndex"]) + 1
            # time.sleep(0.3)
        return list(itertools.chain.from_iterable(results))

    def get_suggested_releases_and_images_by_product_ids(self, product_ids):
        """Returns a list of Cisco suggested software releases and images for a list of product IDs.
        https://developer.cisco.com/docs/support-apis/#!software-suggestion/get-suggested-releases-and-images-by-product-ids

        Args:
            product_ids (list): Base product IDs for which to return suggested software releases.

        Returns:
            list: Cisco suggested releases and images list
        """
        results = []
        for _product_ids in split_list(product_ids, 10):
            path = "software/productIds/{productIds}".format(
                productIds=",".join(_product_ids)
            )
            results.append(self.__paginated_request("get", path))
        return list(itertools.chain.from_iterable(results))

    def get_suggested_releases_by_product_ids(self, product_ids):
        """Returns a list of Cisco suggested software releases (without images) for a list of product IDs.
        https://developer.cisco.com/docs/support-apis/#!software-suggestion/get-suggested-releases-by-product-ids-no-images

        Args:
            product_ids (list): Base product IDs for which to return suggested software releases.

        Returns:
            list: Cisco suggested releases list
        """
        results = []
        for _product_ids in split_list(product_ids, 10):
            path = "releases/productIds/{productIds}".format(
                productIds=",".join(_product_ids)
            )
            results.append(self.__paginated_request("get", path))
        return list(itertools.chain.from_iterable(results))

    def get_compatible_and_suggested_software_releases_by_product_id(
        self,
        product_id,
        current_image=None,
        current_release=None,
        supported_features=None,
        supported_hardware=None,
    ):
        """Returns compatible and suggested software releases for a product given its product identifier (PID) and specific software attributes.
        https://developer.cisco.com/docs/support-apis/#!software-suggestion/get-compatible-and-suggested-software-releases-by-product-id

        Args:
            product_id (str): Base product ID for which to return suggested software releases.
            current_image (str, optional): Current image id from which to filter the result. Defaults to None.
            current_release (str, optional): Current release version from which to filter result. Defaults to None.
            supported_features (str, optional): CommaComma-separated list of feature identifiers by which to filter the results. Defaults to None.
            supported_hardware (str, optional): CommaComma-separated list of supported hardware identifiers from which to filter the results. Defaults to None.

        Returns:
            list: Compatible and suggested software releases
        """

        params = {
            "currentImage": current_image,
            "currentRelease": current_release,
            "supportedFeatures": supported_features,
            "supportedHardware": supported_hardware,
        }
        params = filter_none_value_keys(params)
        path = f"compatible/productId/{product_id}"
        return self.__paginated_request(
            "get", path, result_list_name="suggestions", params=params
        )

    def get_suggested_releases_and_images_by_mdf_ids(self, mdf_ids):
        """Returns a list of Cisco suggested software releases and images for a list of mdf IDs.
        https://developer.cisco.com/docs/support-apis/#!software-suggestion/get-suggested-releases-and-images-by-mdf-ids

        Args:
            mdf_ids (list): Base mdf IDs for which to return suggested software releases.

        Returns:
            list: Cisco suggested software releases and images list
        """
        results = []
        for _mdf_ids in split_list(mdf_ids, 10):
            path = "software/mdfIds/{mdfIds}".format(mdfIds=",".join(_mdf_ids))
            results.append(self.__paginated_request("get", path))
        return list(itertools.chain.from_iterable(results))

    def get_suggested_releases_by_mdf_ids(self, mdf_ids):
        """Returns a list of Cisco suggested software releases (without images) for a list of mdf IDs.
        https://developer.cisco.com/docs/support-apis/#!software-suggestion/get-suggested-releases-by-mdf-ids-no-images

        Args:
            mdf_ids (list): Base mdf IDs for which to return suggested software releases

        Returns:
            list: Cisco suggested software releases list
        """
        results = []
        for _mdf_ids in split_list(mdf_ids, 10):
            path = "releases/mdfIds/{mdfIds}".format(mdfIds=",".join(_mdf_ids))
            results.append(self.__paginated_request("get", path))
        return list(itertools.chain.from_iterable(results))

    def get_compatible_and_suggested_software_releases_by_mdf_id(
        self,
        mdf_id,
        current_image=None,
        current_release=None,
        supported_features=None,
        supported_hardware=None,
    ):
        """Returns compatible and suggested software releases for a product given its mdf identifier (mdfId) and specific software attributes.
        https://developer.cisco.com/docs/support-apis/#!software-suggestion/get-compatible-and-suggested-software-releases-by-mdf-id

        Args:
            mdf_id (str): Base mdf ID for which to return suggested software releases.
            current_image (str, optional): Current image id from which to filter the result. Defaults to None.
            current_release (str, optional): Current release version from which to filter result. Defaults to None.
            supported_features (str, optional): CommaComma-separated list of feature identifiers by which to filter the results. Defaults to None.
            supported_hardware (str, optional): CommaComma-separated list of supported hardware identifiers from which to filter the results. Defaults to None.

        Returns:
            list: Compatible and suggested software releases list
        """

        params = {
            "currentImage": current_image,
            "currentRelease": current_release,
            "supportedFeatures": supported_features,
            "supportedHardware": supported_hardware,
        }
        params = filter_none_value_keys(params)
        path = f"compatible/mdfId/{mdf_id}"
        return self.__paginated_request(
            "get", path, result_list_name="suggestions", params=params
        )
