# -*- coding: utf-8 -*-
"""Splunk Response Plan Execution module utilities for Ansible.

This module contains shared utilities for response plan execution modules:
- splunk_response_plan_execution (apply/remove/manage tasks)
- splunk_response_plan_execution_info (query applied plans/tasks/statuses)

Only include functions and constants that are reusable by both modules.
"""

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from typing import Any
from urllib.parse import unquote


# Task status mappings: API value -> module value (for reading from API)
TASK_STATUS_FROM_API = {
    "Started": "started",
    "Ended": "ended",
    "Reopened": "reopened",
    "Pending": "pending",
}


def map_task_from_api(task: dict[str, Any]) -> dict[str, Any]:
    """Convert a task from API format to module format.

    Args:
        task: Task dictionary from API response.

    Returns:
        Task in module format with normalized values.
    """
    # Decode URL-encoded strings from API
    result = {
        "id": task.get("id", ""),
        "name": unquote(task.get("name", "")),
        "description": unquote(task.get("description", "")),
        "owner": task.get("owner", "unassigned"),
        "is_note_required": task.get("is_note_required", False),
    }

    # Convert status from API format
    api_status = task.get("status", "")
    result["status"] = TASK_STATUS_FROM_API.get(
        api_status,
        api_status.lower() if api_status else "",
    )

    return result


def map_phase_from_api(phase: dict[str, Any]) -> dict[str, Any]:
    """Convert a phase from API format to module format.

    Args:
        phase: Phase dictionary from API response.

    Returns:
        Phase in module format with tasks converted.
    """
    tasks = []
    for task in phase.get("tasks", []) or []:
        tasks.append(map_task_from_api(task))

    # Decode URL-encoded strings from API
    return {
        "id": phase.get("id", ""),
        "name": unquote(phase.get("name", "")),
        "tasks": tasks,
    }


def map_applied_response_plan_from_api(plan: dict[str, Any]) -> dict[str, Any]:
    """Convert an applied response plan from API format to module format.

    Args:
        plan: Applied response plan dictionary from API response.

    Returns:
        Applied response plan in module format.
    """
    phases = []
    for phase in plan.get("phases", []) or []:
        phases.append(map_phase_from_api(phase))

    # API returns 'template_id' in GET response, 'source_template_id' in POST response
    template_id = plan.get("source_template_id") or plan.get("template_id", "")

    # Decode URL-encoded strings from API
    return {
        "id": plan.get("id", ""),
        "name": unquote(plan.get("name", "")),
        "description": unquote(plan.get("description", "")),
        "source_template_id": template_id,
        "phases": phases,
    }
