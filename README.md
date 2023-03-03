# Cisco Support API SDK(ciscosupportapi)  

Ciscosupportapi is a python library that from Cisco Support API to be manipulated in python.

**[Cisco Support API](https://developer.cisco.com/docs/support-apis/)**  
The user calling this API must either become Cisco Smart Net Total Care (SNTC) customer from Cisco Partner Support Service (PSS) partner.
However, this shall not be applied to specific registered Cisco.com user accounts.

## Authentication  
### OAuth2.0 Client Credentials Authentication  

1. Sign in to [Cisco.com](https://apiconsole.cisco.com/).
2. Click the icon of [My apps & Keys] tab.
3. Click the button to Register a New App.
4. Enter a specific app name.
5. Put a check in Client Credentials in OAuth2.0 Credentials.
6. Put a check in APIs you want to use in [Select APIs].
7. Accept the terms of service and click the button to Register.
8. Write down [KEY] and [CLIENT SECRET].
9. Set [KEY] and [CLIENT SECRET] as CiscoSupportApi instance creation argument. 
    ```python
    from ciscosupportapi import CiscoSupportApi

    api = CiscoSupportApi(
        client_id="{[KEY]}",
        client_secret="{[CLIENT SECRET]}")

    ```

Please see below for the details.  
https://developer.cisco.com/docs/support-apis/#!user-onboarding-process/user-onboarding-process

## Supported APIs
- [Software Suggestion API](https://developer.cisco.com/docs/support-apis/#!software-suggestion) (v0.1.0+)
- [Bug API](https://developer.cisco.com/docs/support-apis/#!bug) (v0.2.0+)
- [EoX API](https://developer.cisco.com/docs/support-apis/#!eox) (v0.2.0+)

## Installation  
To install the latest release of ciscosupportapi, do this:
```sh
pip install git+https://<TODO: Change to GitHub URL>
```

To install a specific version:  
```sh
pip install git+https://<TODO: Change to GitHub URL>@{version}
```

The URL for installation can also be written in a text file:
requirements.txt
``` sh
pip install -r requirements.txt
```

## Getting Started  
Import and create a CiscoSupportApi class object
```python
>>> from ciscosupportapi import CiscoSupportApi
>>> api = CiscoSupportApi(client_id="{KEY}", client_secret="{CLIENT_SECRET}")
```

### Software Suggestions API  
Get suggested releases by-product ids.
```python
>>> suggestions = api.software_suggestions.get_suggested_releases_by_product_ids(["ASR1001-X", "C4KX-NM-8SFP+", "WS-F4531"])
>>> print(json.dumps(suggestions[0], indent=4))
```

```sh
{
    "id": "1",
    "product": {
        "basePID": "ASR1001-X",
        "mdfId": "286305946",
        "productName": "Nexus 93180YC-EX Switch",
        "softwareType": "NX-OS System Software"
    },
    "suggestions": [
        {
            "id": "1",
            "isSuggested": "Y",
            "releaseFormat1": "9.3(7)",
            "releaseFormat2": "9.3(7)",
            "releaseDate": "11-Mar-2021",
            "majorRelease": "9",
            "releaseTrain": "9.3",
            "releaseLifeCycle": "NA",
            "relDispName": "9.3(7)",
            "trainDispName": "9.3",
            "errorDetailsResponse": null
        }
    ]
}
```

### Bug API  
Search bugs by keywords.
```python
>>> bugs = api.bug.search_for_bugs_by_keyword("IOS-XE devices with smart licensing", status="O", sort_by="severity", limit=10)
>>> print(json.dumps(bugs[0], indent=4))
```

```sh
{
    "id": "1",
    "bug_id": "CSCwa34749",
    "headline": "IOS-XE device reloaded after using \"license smart factory reset\"",
    "description": "<B>Symptom:</B>\nAfter using the command 'license smart factory reset' the device reloaded by itself generating crashfiles and corefiles.\n\n<B>Conditions:</B>\nThe issue has been identified in IOS-XE devices with smart licensing using policy feature.\nThis feature is present in most IOS-XE devices from 17.3.2 version.\nIn smart licensing feature codes (previous 17.3.2), the unexpected reload has not been documented, however at this point it is not discarded.\n\n<B>Workaround:</B>\nThere is no workaround at this time.\nThe device is recovered by itself after the reboot.\n\n<B>Further Problem Description:</B>\nTo confirm that the unexpected reload is related to this defect a TAC case can be opened with the crashfile and core files from the event.\n",
    "severity": "3",
    "status": "O",
    "behavior_changed": "",
    "last_modified_date": "2021-12-20",
    "product": "smart_licensing",
    "known_affected_releases": "17.3.3",
    "known_fixed_releases": "",
    "support_case_count": "5"
}
```

### EoX API  
Get the EoX information announced between 2021-12-01 and 2021-12-31.
```python
>>> eox = api.eox.get_eox_by_dates('2021-12-01', '2021-12-31', limit=10, eox_attrib='EO_EXT_ANNOUNCE_DATE')
>>> print(json.dumps(eox[0], indent=4))
```

```sh
{
    "EOLProductID": "C1-1Y-NFVB-TRK",
    "ProductIDDescription": "C1 Branch NFV - Contract Tracking 1-Yr",
    "ProductBulletinNumber": "EOL14603",
    "LinkToProductBulletinURL": "https://www.cisco.com/c/en/us/products/collateral/routers/cloud-services-router-1000v-series/integrated-services-virtual-router-eol.html",
    "EOXExternalAnnouncementDate": {
        "value": "2021-12-16",
        "dateFormat": "YYYY-MM-DD"
    },
    "EndOfSaleDate": {
        "value": "2022-12-16",
        "dateFormat": "YYYY-MM-DD"
    },
    "EndOfSWMaintenanceReleases": {
        "value": "",
        "dateFormat": "YYYY-MM-DD"
    },
    "EndOfSecurityVulSupportDate": {
        "value": "",
        "dateFormat": "YYYY-MM-DD"
    },
    "EndOfRoutineFailureAnalysisDate": {
        "value": "",
        "dateFormat": "YYYY-MM-DD"
    },
    "EndOfServiceContractRenewal": {
        "value": "",
        "dateFormat": "YYYY-MM-DD"
    },
    "LastDateOfSupport": {
        "value": "",
        "dateFormat": "YYYY-MM-DD"
    },
    "EndOfSvcAttachDate": {
        "value": "",
        "dateFormat": "YYYY-MM-DD"
    },
    "UpdatedTimeStamp": {
        "value": "2021-12-20",
        "dateFormat": "YYYY-MM-DD"
    },
    "EOXMigrationDetails": {
        "PIDActiveFlag": "Y",
        "MigrationInformation": "Cisco DNA Subscription for Catalyst 8000V",
        "MigrationOption": "Enter PID(s)",
        "MigrationProductId": "L-DNA-C8000V",
        "MigrationProductName": "",
        "MigrationStrategy": "",
        "MigrationProductInfoURL": ""
    },
    "EOXInputType": "showEoXByDates",
    "EOXInputValue": "2021-12-01 , 2021-12-31 , EO_EXT_ANNOUNCE_DATE"
}
```
