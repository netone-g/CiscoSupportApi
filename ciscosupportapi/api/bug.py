import itertools
import logging
from typing import Optional

from requests.exceptions import HTTPError

from ..exceptions import CiscoSupportApiException
from ..utility import filter_none_value_keys, split_list

logger = logging.getLogger(__name__)

API_PATH = "bug/v2.0/bugs/"


class BugV2API(object):
    """Bug API
    https://developer.cisco.com/docs/support-apis/#!bug

    """

    def __init__(self, session: object, base_url: str) -> None:
        self._session = session
        self._base_url = base_url + API_PATH
        logger.debug("BugV2API initialized")

    def __single_request(self, method: str, path: str) -> dict:
        response = self._session.request(method, self._base_url + path)  # type: ignore
        result = response.json()
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.error(str(e))
            if "ErrorResponse" in result:
                raise CiscoSupportApiException(result["ErrorResponse"])
            raise e
        return result

    def __paginated_request(
        self,
        method: str,
        path: str,
        result_list_name: str = "bugs",
        params: dict = {},
        limit: Optional[int] = None,
    ) -> list:
        next_index = None
        results = []
        _params = params.copy()
        # Get max index by limit (10 records per page)
        max_index = -(-limit // 10) if limit else None

        while True:
            if next_index:
                _params["page_index"] = next_index
            response = self._session.request(  # type: ignore
                method, self._base_url + path, params=_params
            )
            result = response.json()
            # logger.debug(f'Response: {result}')
            try:
                response.raise_for_status()
            except HTTPError as e:
                logger.error(str(e))
                if "ErrorResponse" in result:
                    raise CiscoSupportApiException(result["ErrorResponse"])
                raise e
            results.append(result[result_list_name])

            pagination = result["pagination_response_record"]
            # logger.debug(pagination)
            if not pagination or int(pagination["page_index"]) >= int(
                pagination["last_index"]
            ):
                break
            next_index = int(pagination["page_index"]) + 1
            if max_index and max_index < next_index:
                break
            # time.sleep(0.3)

        results = list(itertools.chain.from_iterable(results))
        if limit and len(results) > limit:
            return results[:limit]
        return results

    def get_bug_details_by_bug_ids(self, bug_ids: list) -> list:
        """Returns detailed information for the specified bug ID or IDs.
        https://developer.cisco.com/docs/support-apis/#!bug/get-bug-details-by-bug-ids

        Args:
            bug_ids (list): Identifier of the bug or bugs for which to return detailed information. A maximum of five (5) bug IDs can be submitted.

        Returns:
            list: Cisco bugs list
        """
        results = []
        for _bug_ids in split_list(bug_ids, 5):
            path = "bug_ids/{bug_ids}".format(bug_ids=",".join(_bug_ids))
            r = self.__single_request("get", path)
            results.append(r.get("bugs", []))
        return list(itertools.chain.from_iterable(results))

    def get_bugs_by_base_product_id(
        self,
        product_id: str,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Returns detailed information for the bugs associated with the specified base product ID.
        https://developer.cisco.com/docs/support-apis/#!bug/get-bugs-by-base-product-id

        Args:
            product_id (str): Identifier of the base product for which to return details on associated bugs. Only one base product ID can be submitted.
            status (str, optional): Status of the bug; only bugs with the specified status are returned. One of the following values:
                            O = Open
                            F = Fixed
                            T = Terminated
                            For example, status=O Only one value can be submitted. By default, bugs with all statuses (Open, Fixed, Terminated) are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned. One of the following values:
                                    1 = Last Week
                                    2 = Last 30 Days (default)
                                    3 = Last 6 Months
                                    4 = Last Year
                                    5 = All
                                    For example, modified_date=1. By default, bugs with a last modified date within the last 30 days are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned. One of the following values: 1, 2, 3, 4, 5, 6
                                      Only one value can be submitted; for example, severity=1 By default, bugs with all severities are returned.
            sort_by (str, optional): Parameter on which to sort the results. One of the following values:
                                        status
                                        modified_date (recent first)
                                        severity
                                        support_case_count
                                        modified_date_earliest (earliest first)
                                        For example, sort_by=severity. By default, results are sorted by modified_date (descending, recent first).
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f"products/product_id/{product_id}"
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )

    def get_bugs_by_base_product_id_and_software_releases(
        self,
        product_id: str,
        software_releases: list,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Returns detailed information for the bugs associated with the specified base product ID and software release or releases.
        https://developer.cisco.com/docs/support-apis/#!bug/get-bugs-by-base-product-id-and-software-releases

        Args:
            product_id (str): Identifier of the base product for which to return details on associated bugs. Only one base product ID can be submitted.
            software_releases (list): Version number or numbers of the software release for which to return details on associated bugs.
            status (str, optional): Status of the bug; only bugs with the specified status are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned.
            sort_by (str, optional): Parameter on which to sort the results.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f'products/product_id/{product_id}/software_releases/{",".join(software_releases)}'
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )

    def search_for_bugs_by_keyword(
        self,
        keyword: str,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Returns detailed information for the bugs associated with the specified keyword.
        https://developer.cisco.com/docs/support-apis/#!bug/search-for-bugs-by-keyword

        Args:
            keyword (str): Keyword or keywords for which to return details on associated bugs. Multiple words can be submitted.
            status (str, optional): Status of the bug; only bugs with the specified status are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned.
            sort_by (str, optional): Parameter on which to sort the results.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f"keyword/{keyword}"
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )

    def search_bugs_by_product_series_and_affected_software_release(
        self,
        product_series: str,
        affected_releases: list,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Search Bugs by Product Series and Affected Software Release
        https://developer.cisco.com/docs/support-apis/#!bug/search-bugs-by-product-series-and-affected-software-release

        Args:
            product_series (str): Cisco product series for which to return details on associated bugs. Only one product series can be submitted.
            affected_releases (list): Version number or numbers of the affected software release for which to return details on associated bugs.
            status (str, optional): Status of the bug; only bugs with the specified status are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned.
            sort_by (str, optional): Parameter on which to sort the results.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f'product_series/{product_series}/affected_releases/{",".join(affected_releases)}'
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )

    def search_bugs_by_product_series_and_fixed_in_software_release(
        self,
        product_series: str,
        fixed_in_releases: list,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Returns detailed information for the bugs associated with the specified hardware product series and software release or releases in which the bug was fixed.
        https://developer.cisco.com/docs/support-apis/#!bug/search-bugs-by-product-series-and-fixed-in-software-release

        Args:
            product_series (str): Cisco product series for which to return details on associated bugs. Only one product series can be submitted.
            fixed_in_releases (list): Version number or numbers of the fixed-in software release for which to return details on associated bugs.
            status (str, optional): Status of the bug; only bugs with the specified status are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned.
            sort_by (str, optional): Parameter on which to sort the results.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f'product_series/{product_series}/fixed_in_releases/{",".join(fixed_in_releases)}'
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )

    def search_bugs_by_product_name_and_affected_software_release(
        self,
        product_name: str,
        affected_releases: list,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Returns detailed information for the bugs associated with the specified product name and affected software release or releases.
        https://developer.cisco.com/docs/support-apis/#!bug/search-bugs-by-product-name-and-affected-software-release

        Args:
            product_name (str): Cisco product name for which to return details on associated bugs. Only one product name can be submitted.
            affected_releases (list): Version number or numbers of the affected software release for which to return details on associated bugs.
            status (str, optional): Status of the bug; only bugs with the specified status are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned.
            sort_by (str, optional): Parameter on which to sort the results.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f'product_name/{product_name}/affected_releases/{",".join(affected_releases)}'
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )

    def search_bugs_by_product_name_and_fixed_in_software_release(
        self,
        product_name: str,
        fixed_in_releases: list,
        status: Optional[str] = None,
        modified_date: Optional[int] = None,
        severity: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Returns detailed information for the bugs associated with the specified product name and software release or releases in which the bug was fixed.
        https://developer.cisco.com/docs/support-apis/#!bug/search-bugs-by-product-name-and-fixed-in-software-release

        Args:
            product_name (str): Cisco product name for which to return details on associated bugs. Only one product name can be submitted.
            fixed_in_releases (list): Version number or numbers of the fixed-in software release for which to return details on associated bugs.
            status (str, optional): Status of the bug; only bugs with the specified status are returned.
            modified_date (int, optional): Last modified date of the bug; only bugs modified within the specified time are returned.
            severity (int, optional): Severity of the bug; only bugs with the specified severity are returned.
            sort_by (str, optional): Parameter on which to sort the results.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco bugs list
        """
        params = {
            "status": status,
            "modified_date": modified_date,
            "severity": severity,
            "sort_by": sort_by,
        }
        params = filter_none_value_keys(params)

        path = f'product_name/{product_name}/fixed_in_releases/{",".join(fixed_in_releases)}'
        return self.__paginated_request(
            "get", path, result_list_name="bugs", params=params, limit=limit
        )
