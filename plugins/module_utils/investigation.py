# -*- coding: utf-8 -*-
"""Splunk Investigation module utilities for Ansible."""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from typing import Any, Optional

from ansible_collections.splunk.es.plugins.module_utils.finding import (
    DISPOSITION_FROM_API,
    DISPOSITION_TO_API,
    STATUS_FROM_API,
    STATUS_TO_API,
)


# Default API path components
DEFAULT_API_NAMESPACE = "servicesNS"
DEFAULT_API_USER = "nobody"
DEFAULT_API_APP = "missioncontrol"

# API path for investigations API
INVESTIGATION_API_PATH = (
    f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations"
)

# Fields that can be updated via the main update endpoint (name cannot be updated)
UPDATABLE_FIELDS = [
    "description",
    "status",
    "disposition",
    "owner",
    "urgency",
    "sensitivity",
]

# finding_ids requires a separate API endpoint
FINDING_IDS_FIELD = "finding_ids"

# Urgency choices
URGENCY_CHOICES = [
    "informational",
    "low",
    "medium",
    "high",
    "critical",
    "unknown",
]

# Sensitivity choices (lowercase for user input)
SENSITIVITY_CHOICES = [
    "white",
    "green",
    "amber",
    "red",
    "unassigned",
]

# Sensitivity mapping: module value (lowercase) -> API value (capitalized)
SENSITIVITY_TO_API = {
    "white": "White",
    "green": "Green",
    "amber": "Amber",
    "red": "Red",
    "unassigned": "Unassigned",
}

# Sensitivity mapping: API value -> module value
SENSITIVITY_FROM_API = {v: k for k, v in SENSITIVITY_TO_API.items()}


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


def build_investigation_update_path(
    ref_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the investigations update API path.

    Args:
        ref_id: The investigation reference ID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The investigations update API path with ref_id.
    """
    return f"{build_investigation_api_path(namespace, user, app)}/{ref_id}"


def build_investigation_findings_path(
    ref_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the API path for adding findings to an investigation.

    Args:
        ref_id: The investigation reference ID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The API path for adding findings to the investigation.
    """
    return f"{build_investigation_update_path(ref_id, namespace, user, app)}/findings"


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


def map_investigation_to_api(investigation: dict[str, Any]) -> dict[str, Any]:
    """Convert module params to API payload format.

    Args:
        investigation: The investigation parameters dictionary.

    Returns:
        Dictionary formatted for the Splunk investigations API.
    """
    res = investigation.copy()

    # Handle status conversion to API numeric value
    if "status" in res and res["status"]:
        res["status"] = STATUS_TO_API.get(res["status"], res["status"])

    # Handle disposition conversion to API format
    if "disposition" in res and res["disposition"]:
        res["disposition"] = DISPOSITION_TO_API.get(
            res["disposition"].lower(),
            res["disposition"],
        )

    # Handle sensitivity conversion to API format (capitalized)
    if "sensitivity" in res and res["sensitivity"]:
        res["sensitivity"] = SENSITIVITY_TO_API.get(
            res["sensitivity"].lower(),
            res["sensitivity"],
        )

    return res


def map_investigation_update_to_api(investigation: dict[str, Any]) -> dict[str, Any]:
    """Convert module params to API payload format for updating investigations.

    Only includes fields that are allowed to be updated.

    Args:
        investigation: The investigation parameters dictionary.

    Returns:
        Dictionary formatted for the Splunk investigations update API.
    """
    res = {}

    for field in UPDATABLE_FIELDS:
        if field in investigation and investigation[field] is not None:
            value = investigation[field]

            # Handle status conversion
            if field == "status":
                value = STATUS_TO_API.get(value, value)

            # Handle disposition conversion
            if field == "disposition":
                value = DISPOSITION_TO_API.get(value.lower(), value)

            # Handle sensitivity conversion
            if field == "sensitivity":
                value = SENSITIVITY_TO_API.get(value.lower(), value)

            res[field] = value

    return res
