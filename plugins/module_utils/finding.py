# -*- coding: utf-8 -*-
"""Splunk Finding module utilities for Ansible."""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import re

from typing import Any, Optional

from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP_SECURITY_SUITE,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    DISPOSITION_FROM_API,
    STATUS_FROM_API,
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


def build_finding_api_path(
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP_SECURITY_SUITE,
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


# Buffer in seconds to subtract from notable_time when used as 'earliest'
# in time-range queries. The Splunk API may treat 'earliest' as exclusive
# or the finding's _time may have sub-second precision slightly before the
# integer epoch in the ref_id, so a small buffer avoids missing the finding.
_EARLIEST_BUFFER_SECONDS = 1


def get_earliest_from_ref_id(ref_id: str) -> Optional[str]:
    """Get a buffered earliest time suitable for Splunk time-range queries.

    Extracts the notable time from the ref_id and subtracts a small buffer
    to ensure the finding falls within the query's time range.

    Args:
        ref_id: The finding reference ID.

    Returns:
        The buffered earliest time as a string, or None if extraction fails.
    """
    notable_time = extract_notable_time(ref_id)
    if notable_time is None:
        return None
    return str(int(notable_time) - _EARLIEST_BUFFER_SECONDS)


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
