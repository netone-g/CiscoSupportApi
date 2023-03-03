import itertools
import logging
from typing import Optional

from ..exceptions import CiscoSupportApiException
from ..utility import filter_none_value_keys

logger = logging.getLogger(__name__)

API_PATH = "supporttools/eox/rest/5/"


class EoXAPI(object):
    """EoX API
    https://developer.cisco.com/docs/support-apis/#!eox

    """

    def __init__(self, session: object, base_url: str) -> None:
        self._session = session
        self._base_url = base_url + API_PATH
        logger.debug("EoXAPI initialized")

    def __paginated_request(
        self,
        method: str,
        path: str,
        result_list_name: str = "EOXRecord",
        params: dict = {},
        limit: Optional[int] = None,
    ) -> list:
        next_index = 1
        results = []
        # Get max index by limit (10 records per page)

        while True:
            _path = path.format(page_index=next_index)
            response = self._session.request(  # type: ignore
                method, self._base_url + _path, params=params
            )
            result = response.json()
            # logger.debug(f'Response: {result}')
            response.raise_for_status()
            if "EOXError" in result:
                logger.error(str(result["EOXError"]))
                raise CiscoSupportApiException(result["EOXError"])
            results.append(result[result_list_name])

            pagination = result["PaginationResponseRecord"]
            # logger.debug(pagination)
            if not pagination or int(pagination["PageIndex"]) >= int(
                pagination["LastIndex"]
            ):
                break
            if next_index == 1:
                max_index = -(-limit // pagination["PageRecords"]) if limit else None
            next_index = int(pagination["PageIndex"]) + 1
            if max_index and max_index < next_index:
                break
            # time.sleep(0.3)

        results = list(itertools.chain.from_iterable(results))
        if limit and len(results) > limit:
            return results[:limit]
        return results

    def get_eox_by_dates(
        self,
        start_date: str,
        end_date: str,
        eox_attrib: Optional[list] = None,
        limit=None,
    ) -> list:
        """Returns all active and inactive EoX records for all products with the specified eoxAttrib value within the startDate and endDate values, inclusive. If you do not specify an eoxAttrib value, this method returns records with an updated time stamp within the specified date range.
        Note: This method can be used to retrieve records based on any date listed in the EoX record. For example, if you specify a date range and enter EO_SALE_DATE and EO_LAST_SUPPORT_DATE as the eoxAttrib values, this method returns records with an end of sale date or last date of support within the specified date range. This feature allows you to target specific date ranges within each attribute without having to pull the entire database.
        https://developer.cisco.com/docs/support-apis/#!eox/get-eox-by-dates

        Args:
            start_date (str): Start date of the date range of records to return in the following format: YYYY-MM-DD. For example: 2010-01-01
            end_date (str): End date of the date range of records to return in the following format: YYYY-MM-DD. For example: 2010-01-01
            eox_attrib (list, optional): Attribute or attributes of the records to return. eoxAttrib must be one of the following values:
                                        - 'UPDATE_TIMESTAMP' (default): Date the EoX record was created or last modified.
                                        - 'EO_EXT_ANNOUNCE_DATE': Date that the end of sale and end of life of the product was announced to the general public.
                                        - 'EO_SALES_DATE': Last date to order the requested product through Cisco point-of-sale mechanisms. The product is no longer for sale after this date.
                                        - 'EO_SW_MAINTENANCE_DATE': Last date that Cisco Engineering might release any software maintenance releases or bug fixes to the software product. After this date, Cisco Engineering no longer develops, repairs, maintains, or tests the product software.
                                        - 'EO_SECURITY_VUL_SUPPORT_DATE': Last date that Cisco Engineering may release a planned maintenance release or scheduled software remedy for a security vulnerability issue.
                                        - 'EO_FAIL_ANALYSIS_DATE': Last date Cisco might perform a routine failure analysis to determine the root cause of an engineering-related or manufacturing-related issue.
                                        - 'EO_CONTRACT_RENEW_DATE': Last date to extend or renew a service contract for the product. The extension or renewal period cannot extend beyond the last date of support.
                                        - 'EO_LAST_SUPPORT_DATE': Last date to receive service and support for the product. After this date, all support services for the product are unavailable, and the product becomes obsolete.
                                        - 'EO_SVC_ATTACH_DATE': Last date to order a new service-and-support contract or add the equipment and/or software to an existing service-and-support contract for equipment and software that is not covered by a service-and-support contract.
                                        See https://developer.cisco.com/docs/support-apis/#eox/EOXRecordType for more information on these values.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco EoX list
        """
        params = {"eoxAttrib": eox_attrib}
        params = filter_none_value_keys(params)
        path = f"EOXByDates/{{page_index}}/{start_date}/{end_date}"
        return self.__paginated_request("get", path, params=params, limit=limit)

    def get_eox_by_product_ids(self, product_ids: list, limit=None) -> list:
        """Returns one or more EOX records for the product or products with the specified product ID (PID) or product IDs.
        https://developer.cisco.com/docs/support-apis/#!eox/get-eox-by-product-ids

        Args:
            product_ids (list): Product IDs for the products to retrieve from the database. Enter up to 20 PIDs.
            Note: To enhance search capabilities, the Cisco Support Tools allows wildcards with the productIDs parameter. A minimum of 3 characters is required. For example, only the following inputs are valid: *VPN*, *VPN, VPN*, and VPN. Using wildcards can result in multiple PIDs in the output.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco EoX list
        """
        path = f'EOXByProductID/{{page_index}}/{",".join(product_ids)}'
        return self.__paginated_request("get", path, params={}, limit=limit)

    def get_eox_by_serial_numbers(self, serial_numbers: list, limit=None) -> list:
        """Returns the EoX record for products with the specified serial numbers.
        https://developer.cisco.com/docs/support-apis/#!eox/get-eox-by-serial-numbers

        Args:
            serial_numbers (list): Device serial number or numbers for which to return results. You can enter up to 20 serial numbers (each with a maximum length of 40).
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco EoX list
        """
        path = f'EOXBySerialNumber/{{page_index}}/{",".join(serial_numbers)}'
        return self.__paginated_request("get", path, params={}, limit=limit)

    def get_eox_by_software_release_strings(
        self, software_release_strings: list, limit=None
    ) -> list:
        """Returns the EoX record for products associated with the specified software release and (optionally) the specified operating system.
        https://developer.cisco.com/docs/support-apis/#!eox/get-eox-by-software-release-strings

        Args:
            software_release_strings (list): String for software release and type of operating system (optional) for the requested product. For example: 12.2,IOS You can enter up to 20 software release and operating system type combinations. Each combination can return multiple EoX records; see SWReleaseStringType for more information.
            limit (int, optional): Limit the maximum number of records in the results.

        Returns:
            list: Cisco EoX list
        """
        params = {
            f"input{i}": software_release_string
            for i, software_release_string in enumerate(
                software_release_strings, start=1
            )
        }
        path = "EOXBySWReleaseString/{page_index}"
        return self.__paginated_request("get", path, params=params, limit=limit)
