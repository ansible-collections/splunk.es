# -*- coding: utf-8 -*-
"""Splunk Investigation module utilities for Ansible."""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from typing import Any, Optional

from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    DISPOSITION_FROM_API,
    STATUS_FROM_API,
)


# API path for investigations API (uses missioncontrol app)
INVESTIGATION_API_PATH = (
    f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations"
)

# Sensitivity mapping: API value (capitalized) -> module value (lowercase)
# Used by map_investigation_from_api to convert API responses
SENSITIVITY_FROM_API = {
    "White": "white",
    "Green": "green",
    "Amber": "amber",
    "Red": "red",
    "Unassigned": "unassigned",
}


def build_investigation_api_path(
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the investigations API path from components.

    Args:
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The complete investigations API path.
    """
    return f"{namespace}/{user}/{app}/public/v2/investigations"


def _extract_finding_ids(config: dict[str, Any]) -> Optional[list[str]]:
    """Extract finding_ids from consolidated_findings in API response.

    Args:
        config: The API response config dictionary.

    Returns:
        List of finding IDs, or None if not present.
    """
    consolidated = config.get("consolidated_findings", {})
    if not consolidated:
        return None

    event_ids = consolidated.get("event_id")
    if not event_ids:
        return None

    # event_id can be a string (single) or list (multiple)
    return event_ids if isinstance(event_ids, list) else [event_ids]


def _convert_api_enum_value(
    result: dict[str, Any],
    field: str,
    mapping: dict[str, str],
    stringify_key: bool = False,
) -> None:
    """Convert an API enum value to module format in-place.

    Args:
        result: The result dictionary to modify in-place.
        field: The field name to convert.
        mapping: The mapping dictionary from API to module values.
        stringify_key: Whether to convert the key to string before lookup.
    """
    if field not in result or not result[field]:
        return

    value = result[field]
    lookup_key = str(value) if stringify_key else value
    fallback = value.lower() if isinstance(value, str) else value
    result[field] = mapping.get(lookup_key, fallback)


def map_investigation_from_api(config: dict[str, Any]) -> dict[str, Any]:
    """Convert investigation API response to module params format.

    Args:
        config: The API response config dictionary.

    Returns:
        Dictionary with module parameter names and normalized values.
    """
    res = {}

    # Extract ref_id from investigation_guid field
    if "investigation_guid" in config:
        res["investigation_ref_id"] = config["investigation_guid"]

    # Copy fields directly (no key transformation needed)
    field_names = [
        "name",
        "description",
        "status",
        "disposition",
        "owner",
        "urgency",
        "sensitivity",
    ]
    for field in field_names:
        if field in config and config[field] is not None:
            res[field] = config[field]

    # Extract finding_ids from consolidated_findings
    finding_ids = _extract_finding_ids(config)
    if finding_ids:
        res["finding_ids"] = finding_ids

    # Convert API enum values to human-readable module format
    _convert_api_enum_value(res, "status", STATUS_FROM_API, stringify_key=True)
    _convert_api_enum_value(res, "disposition", DISPOSITION_FROM_API, stringify_key=True)
    _convert_api_enum_value(res, "sensitivity", SENSITIVITY_FROM_API)

    return res
