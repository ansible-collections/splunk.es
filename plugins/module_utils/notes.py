# -*- coding: utf-8 -*-
"""Splunk Notes module utilities for Ansible.

This module contains shared utilities for notes management:
- Path builders for finding/investigation notes and response plan task notes
- Mapping functions for API responses

Only include functions and constants that are reusable.
Pure Python functions with no Ansible dependencies for easy unit testing.
"""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from typing import Any, Optional

from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
)

# Target type constants
TARGET_FINDING = "finding"
TARGET_INVESTIGATION = "investigation"
TARGET_RESPONSE_PLAN_TASK = "response_plan_task"

# Required parameters for each target type
TARGET_REQUIRED_PARAMS: dict[str, list[str]] = {
    TARGET_FINDING: ["finding_ref_id"],
    TARGET_INVESTIGATION: ["investigation_ref_id"],
    TARGET_RESPONSE_PLAN_TASK: [
        "investigation_ref_id",
        "response_plan_id",
        "phase_id",
        "task_id",
    ],
}


def validate_target_params(target_type: str, args: dict[str, Any]) -> Optional[str]:
    """Validate required parameters based on target type.

    Args:
        target_type: The target type (finding, investigation, response_plan_task).
        args: The task arguments dictionary.

    Returns:
        Error message if validation fails, None if valid.
    """
    required_params = TARGET_REQUIRED_PARAMS.get(target_type, [])
    missing = [param for param in required_params if not args.get(param)]

    if not missing:
        return None

    return f"Missing required parameters for target_type '{target_type}': {', '.join(missing)}"


def build_notes_api_path(
    investigation_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the notes API path for findings or investigations.

    This path is used for both findings and investigations. The difference
    is in the investigation_id parameter:
    - For findings: use the ref_id (e.g., uuid@@notable@@time{timestamp})
    - For investigations: use the investigation UUID

    Args:
        investigation_id: The finding ref_id or investigation UUID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The complete notes API path.
    """
    return f"{namespace}/{user}/{app}/public/v2/investigations/{investigation_id}/notes"


def build_note_api_path(
    investigation_id: str,
    note_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the API path for a specific note.

    Args:
        investigation_id: The finding ref_id or investigation UUID.
        note_id: The note ID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The API path for the specific note.
    """
    base_path = build_notes_api_path(investigation_id, namespace, user, app)
    return f"{base_path}/{note_id}"


def build_task_notes_api_path(
    investigation_id: str,
    response_plan_id: str,
    phase_id: str,
    task_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the notes API path for response plan tasks.

    Args:
        investigation_id: The investigation UUID.
        response_plan_id: The applied response plan ID.
        phase_id: The phase ID.
        task_id: The task ID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The complete task notes API path.
    """
    return (
        f"{namespace}/{user}/{app}/public/v2/investigations/{investigation_id}"
        f"/responseplans/{response_plan_id}/phase/{phase_id}/tasks/{task_id}/notes"
    )


def build_task_note_api_path(
    investigation_id: str,
    response_plan_id: str,
    phase_id: str,
    task_id: str,
    note_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the API path for a specific task note.

    Args:
        investigation_id: The investigation UUID.
        response_plan_id: The applied response plan ID.
        phase_id: The phase ID.
        task_id: The task ID.
        note_id: The note ID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The API path for the specific task note.
    """
    base_path = build_task_notes_api_path(
        investigation_id,
        response_plan_id,
        phase_id,
        task_id,
        namespace,
        user,
        app,
    )
    return f"{base_path}/{note_id}"


def map_note_from_api(note: dict[str, Any]) -> dict[str, Any]:
    """Convert a note from API format to module format.

    Args:
        note: Note dictionary from API response.

    Returns:
        Note in module format with normalized values.
    """
    return {
        "note_id": note.get("id", ""),
        "content": note.get("content", ""),
    }


def map_note_to_api(note: dict[str, Any]) -> dict[str, Any]:
    """Convert a note from module format to API payload format.

    Args:
        note: Note dictionary with module parameters.

    Returns:
        Note payload formatted for the Splunk API.
    """
    payload: dict[str, Any] = {}

    if "content" in note and note["content"] is not None:
        payload["content"] = note["content"]

    return payload
