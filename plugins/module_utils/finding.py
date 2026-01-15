# -*- coding: utf-8 -*-
"""Splunk Finding module utilities for Ansible."""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import re

from typing import Any, Optional


# Default API path components
DEFAULT_API_NAMESPACE = "servicesNS"
DEFAULT_API_USER = "nobody"
DEFAULT_API_APP = "SplunkEnterpriseSecuritySuite"

# Fixed app for investigations/update API
INVESTIGATIONS_API_APP = "missioncontrol"

# API path for findings API
FINDING_API_OBJECT = (
    f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/findings"
)

# Key transformation: API param -> module param
FINDING_KEY_TRANSFORM = {
    "rule_title": "title",
    "rule_description": "description",
    "security_domain": "security_domain",
    "risk_object": "entity",
    "risk_object_type": "entity_type",
    "risk_score": "finding_score",
    "owner": "owner",
    "status": "status",
    "urgency": "urgency",
    "disposition": "disposition",
}

# Fields that can be updated via the investigations API
UPDATABLE_FIELDS = ["owner", "status", "urgency", "disposition"]

# Key transformation for update API: module param -> API param
UPDATE_KEY_TRANSFORM = {
    "owner": "assignee",
    "status": "status",
    "urgency": "urgency",
    "disposition": "disposition",
}

# Disposition mapping: module value -> API value
DISPOSITION_TO_API = {
    "unassigned": "disposition:0",
    "true_positive": "disposition:1",
    "benign_positive": "disposition:2",
    "false_positive": "disposition:3",
    "false_positive_inaccurate_data": "disposition:4",
    "other": "disposition:5",
    "undetermined": "disposition:6",
}

# Disposition mapping: API value -> module value
DISPOSITION_FROM_API = {v: k for k, v in DISPOSITION_TO_API.items()}

# Status mapping: module value -> API value
STATUS_TO_API = {
    "unassigned": "0",
    "new": "1",
    "in_progress": "2",
    "pending": "3",
    "resolved": "4",
    "closed": "5",
}

# Status mapping: API value -> module value
STATUS_FROM_API = {v: k for k, v in STATUS_TO_API.items()}


def build_finding_api_path(
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the findings API path from components.

    Args:
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'SplunkEnterpriseSecuritySuite'.

    Returns:
        The complete findings API path.
    """
    return f"{namespace}/{user}/{app}/public/v2/findings"


def build_update_api_path(
    ref_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
) -> str:
    """Build the investigations update API path.

    The update API uses a fixed app (missioncontrol).

    Args:
        ref_id: The finding reference ID (e.g., 'uuid@@notable@@time{timestamp}').
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.

    Returns:
        The investigations update API path (without query parameters).
    """
    return f"{namespace}/{user}/{INVESTIGATIONS_API_APP}/v1/investigations/{ref_id}"


def extract_notable_time(ref_id: str) -> Optional[str]:
    """Extract the notable_time from a finding reference ID.

    The ref_id format is typically: uuid@@notable@@time{timestamp}
    Example: 2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865

    Args:
        ref_id: The finding reference ID.

    Returns:
        The extracted notable_time as a string, or None if not found.
    """
    if not ref_id:
        return None

    # Pattern to match 'time' followed by digits at the end
    match = re.search(r"time(\d+)$", ref_id)
    if match:
        return match.group(1)

    return None


def map_finding_from_api(
    config: dict[str, Any],
    key_transform: dict[str, str] = None,
) -> dict[str, Any]:
    """Convert finding API response to module params format.

    Args:
        config: The API response config dictionary.
        key_transform: Optional key transformation dict. Defaults to FINDING_KEY_TRANSFORM.

    Returns:
        Dictionary with module parameter names and normalized values.
    """
    from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import map_params_to_obj

    if key_transform is None:
        key_transform = FINDING_KEY_TRANSFORM

    res = {}

    # Extract ref_id from finding_id field
    if "finding_id" in config:
        res["ref_id"] = config["finding_id"]

    # Use the helper from module_utils
    res.update(map_params_to_obj(config, key_transform))

    # Handle status conversion
    if "status" in res and res["status"]:
        res["status"] = STATUS_FROM_API.get(str(res["status"]), res["status"])

    # Handle disposition conversion
    if "disposition" in res and res["disposition"]:
        res["disposition"] = DISPOSITION_FROM_API.get(str(res["disposition"]), res["disposition"])

    # Normalize finding_score to int (API returns string like "25.0")
    if "finding_score" in res and res["finding_score"]:
        try:
            res["finding_score"] = int(float(res["finding_score"]))
        except (ValueError, TypeError):
            pass

    return res


def map_finding_to_api(
    finding: dict[str, Any],
    key_transform: dict[str, str] = None,
) -> dict[str, Any]:
    """Convert module params to API payload format.

    Args:
        finding: The finding parameters dictionary.
        key_transform: Optional key transformation dict. Defaults to FINDING_KEY_TRANSFORM.

    Returns:
        Dictionary formatted for the Splunk findings API.
    """
    from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import map_obj_to_params

    if key_transform is None:
        key_transform = FINDING_KEY_TRANSFORM

    # Use the helper from module_utils
    res = map_obj_to_params(finding.copy(), key_transform)

    # Add default values for API
    res["app"] = "SplunkEnterpriseSecuritySuite"
    res["creator"] = "admin"

    # Handle status conversion
    if "status" in res and res["status"]:
        res["status"] = STATUS_TO_API.get(res["status"], res["status"])

    # Handle disposition conversion
    if "disposition" in res and res["disposition"]:
        res["disposition"] = DISPOSITION_TO_API.get(res["disposition"], res["disposition"])

    # Handle custom fields - flatten them into the payload
    if "fields" in finding and finding["fields"]:
        for field in finding["fields"]:
            if "name" in field and "value" in field:
                res[field["name"]] = field["value"]

    return res


def map_update_to_api(finding: dict[str, Any]) -> dict[str, Any]:
    """Convert module params to API payload format for updating findings.

    Args:
        finding: The finding parameters dictionary.

    Returns:
        Dictionary formatted for the Splunk investigations update API.
    """
    res = {}

    for module_key, api_key in UPDATE_KEY_TRANSFORM.items():
        if module_key in finding and finding[module_key] is not None:
            value = finding[module_key]

            # Handle status conversion
            if module_key == "status":
                value = STATUS_TO_API.get(value, value)

            # Handle disposition conversion
            if module_key == "disposition":
                value = DISPOSITION_TO_API.get(value, value)

            res[api_key] = value

    return res
