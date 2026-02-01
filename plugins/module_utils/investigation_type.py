# -*- coding: utf-8 -*-
"""Splunk Investigation Type module utilities for Ansible."""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from typing import Any

from ansible.module_utils.six.moves.urllib.parse import quote

from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
)


def build_investigation_type_api_path(
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the investigation types API path from components.

    Args:
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The complete investigation types API path.
    """
    return f"{namespace}/{user}/{app}/v1/incidenttypes"


def build_investigation_type_path_by_name(
    name: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the investigation type API path for a specific type by name.

    Used for GET (single), PUT, and other operations on a specific investigation type.

    Args:
        name: The investigation type name.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The investigation type API path with name appended.
    """
    encoded_name = quote(name)
    return f"{build_investigation_type_api_path(namespace, user, app)}/{encoded_name}"


def map_investigation_type_from_api(config: dict[str, Any]) -> dict[str, Any]:
    """Convert API response to module params format.

    Args:
        config: The API response config dictionary.

    Returns:
        Dictionary with module parameter names and normalized values.
    """
    response_plan_ids = config.get("response_template_ids") or []

    return {
        "name": config.get("incident_type", ""),
        "description": config.get("description", ""),
        "response_plan_ids": response_plan_ids,
    }


def map_investigation_type_to_api_create(params: dict[str, Any]) -> dict[str, Any]:
    """Convert module params to API payload format for creation.

    Args:
        params: User-provided investigation type parameters.

    Returns:
        Dictionary formatted for the Splunk incident types API (POST).
    """
    return {
        "incident_type": params.get("name", ""),
        "description": params.get("description", ""),
    }


def map_investigation_type_to_api_update(params: dict[str, Any]) -> dict[str, Any]:
    """Convert module params to API payload format for update.

    Args:
        params: User-provided investigation type parameters.

    Returns:
        Dictionary formatted for the Splunk incident types API (PUT).
    """
    return {
        "incident_type": params.get("name", ""),
        "description": params.get("description", ""),
        "response_template_ids": params.get("response_plan_ids") or [],
    }
