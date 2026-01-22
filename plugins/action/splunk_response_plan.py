#
# Copyright 2026 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

"""
The action module for splunk_response_plan
"""

import uuid

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    check_argspec,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
)
from ansible_collections.splunk.es.plugins.modules.splunk_response_plan import DOCUMENTATION


# Initialize display for debug output
display = Display()


def _generate_uuid() -> str:
    """Generate a new UUID string.

    Returns:
        A new UUID4 string.
    """
    return str(uuid.uuid4())


def _build_response_plan_api_path(
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the response plans API path from components.

    Args:
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The complete response plans API path.
    """
    return f"{namespace}/{user}/{app}/v1/responsetemplates"


def _build_response_plan_update_path(
    ref_id: str,
    namespace: str = DEFAULT_API_NAMESPACE,
    user: str = DEFAULT_API_USER,
    app: str = DEFAULT_API_APP,
) -> str:
    """Build the response plan update/delete API path.

    Args:
        ref_id: The response plan reference ID.
        namespace: The namespace portion of the path. Defaults to 'servicesNS'.
        user: The user portion of the path. Defaults to 'nobody'.
        app: The app portion of the path. Defaults to 'missioncontrol'.

    Returns:
        The response plan update API path with ref_id.
    """
    return f"{_build_response_plan_api_path(namespace, user, app)}/{ref_id}"


def _find_task_id_by_name(
    existing_tasks: list[dict[str, Any]],
    task_name: str,
) -> str | None:
    """Find existing task ID by name within a phase.

    Args:
        existing_tasks: List of existing task dictionaries from a phase.
        task_name: The task name to search for.

    Returns:
        The task ID if found, None otherwise.
    """
    for task in existing_tasks:
        if task.get("name") == task_name:
            return task.get("id")
    return None


def _build_search_payload(search: dict[str, Any]) -> dict[str, Any]:
    """Build search entry payload from user input.

    Args:
        search: User-provided search dictionary with name, description, spl.

    Returns:
        Search payload dictionary for API.
    """
    return {
        "name": search.get("name", ""),
        "description": search.get("description", ""),
        "spl": search.get("spl", ""),
    }


def _build_task_payload(
    task: dict[str, Any],
    order: int,
    existing_id: str | None = None,
) -> dict[str, Any]:
    """Build single task payload for API.

    Args:
        task: User-provided task dictionary.
        order: The order/position of the task within the phase.
        existing_id: Existing task ID if updating, None for new task.

    Returns:
        Task payload dictionary for API.
    """
    is_new_task = existing_id is None
    task_id = existing_id if existing_id else _generate_uuid()

    # Build searches list
    searches = []
    for search in task.get("searches", []) or []:
        searches.append(_build_search_payload(search))

    return {
        "task_id": "",
        "phase_id": "",
        "id": task_id,
        "name": task.get("name", ""),
        "description": task.get("description", ""),
        "sla": None,
        "sla_type": "minutes",
        "order": order,
        "status": "Pending",
        "is_note_required": task.get("is_note_required", False),
        "owner": task.get("owner", "unassigned"),
        "isNewTask": is_new_task,
        "files": [],
        "notes": [],
        "suggestions": {
            "actions": [],
            "playbooks": [],
            "searches": searches,
        },
    }


def _build_phase_payload(
    phase: dict[str, Any],
    order: int,
    existing_phase: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build single phase payload for API.

    Args:
        phase: User-provided phase dictionary.
        order: The order/position of the phase.
        existing_phase: Existing phase data if updating, None for new phase.

    Returns:
        Phase payload dictionary for API.
    """
    existing_id = existing_phase.get("id") if existing_phase else None
    phase_id = existing_id if existing_id else _generate_uuid()

    # Get existing tasks for ID matching
    existing_tasks = existing_phase.get("tasks", []) if existing_phase else []

    # Build tasks list
    tasks = []
    for task_order, task in enumerate(phase.get("tasks", []) or [], start=1):
        existing_task_id = _find_task_id_by_name(existing_tasks, task.get("name", ""))
        tasks.append(_build_task_payload(task, task_order, existing_task_id))

    return {
        "template_id": "",
        "id": phase_id,
        "name": phase.get("name", ""),
        "sla": None,
        "sla_type": "minutes",
        "create_time": "",
        "order": order,
        "tasks": tasks,
    }


def _map_response_plan_to_api(
    response_plan: dict[str, Any],
    existing_response_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert module params to API payload format.

    Handles both creation (no existing data) and update (with ID matching).

    Args:
        response_plan: User-provided response plan parameters.
        existing_response_plan: Existing response plan from API if updating.

    Returns:
        Dictionary formatted for the Splunk response templates API.
    """
    # Get existing phases for ID matching
    existing_phases = existing_response_plan.get("phases", []) if existing_response_plan else []

    # Build phases list with ID matching
    phases = []
    for phase_order, phase in enumerate(response_plan.get("phases", []) or [], start=1):
        # Find existing phase by name
        existing_phase = None
        for ep in existing_phases:
            if ep.get("name") == phase.get("name"):
                existing_phase = ep
                break
        phases.append(_build_phase_payload(phase, phase_order, existing_phase))

    payload = {
        "name": response_plan.get("name", ""),
        "description": response_plan.get("description", ""),
        "template_status": response_plan.get("template_status", "draft"),
        "incident_types": [],
        "phases": phases,
    }

    # Add response plan ID if updating
    if existing_response_plan and existing_response_plan.get("id"):
        payload["id"] = existing_response_plan["id"]

    return payload


def _map_task_from_api(task: dict[str, Any]) -> dict[str, Any]:
    """Convert single task from API format to module format.

    Args:
        task: Task dictionary from API response.

    Returns:
        Task in module format.
    """
    # Extract searches from suggestions
    searches = []
    suggestions = task.get("suggestions", {}) or {}
    for search in suggestions.get("searches", []) or []:
        searches.append(
            {
                "name": search.get("name", ""),
                "description": search.get("description", ""),
                "spl": search.get("spl", ""),
            },
        )

    return {
        "name": task.get("name", ""),
        "description": task.get("description", ""),
        "is_note_required": task.get("is_note_required", False),
        "owner": task.get("owner", "unassigned"),
        "searches": searches,
    }


def _map_phase_from_api(phase: dict[str, Any]) -> dict[str, Any]:
    """Convert single phase from API format to module format.

    Args:
        phase: Phase dictionary from API response.

    Returns:
        Phase in module format.
    """
    tasks = []
    for task in phase.get("tasks", []) or []:
        tasks.append(_map_task_from_api(task))

    return {
        "name": phase.get("name", ""),
        "tasks": tasks,
    }


def _map_response_plan_from_api(config: dict[str, Any]) -> dict[str, Any]:
    """Convert API response to module params format.

    Args:
        config: The API response config dictionary.

    Returns:
        Dictionary with module parameter names and normalized values.
    """
    phases = []
    for phase in config.get("phases", []) or []:
        phases.append(_map_phase_from_api(phase))

    return {
        "name": config.get("name", ""),
        "description": config.get("description", ""),
        "template_status": config.get("template_status", "draft"),
        "phases": phases,
    }


class ActionModule(ActionBase):
    """Action module for managing Splunk ES response plans."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.module_name = "response_plan"
        self.api_namespace = DEFAULT_API_NAMESPACE
        self.api_user = DEFAULT_API_USER
        self.api_app = DEFAULT_API_APP
        self.api_object = None  # Will be built dynamically

    def fail_json(self, msg: str) -> None:
        """Raise an AnsibleActionFail with a cleaned up message.

        Args:
            msg: The message for the failure.

        Raises:
            AnsibleActionFail: Always raised with the provided message.
        """
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def _build_api_path(self) -> str:
        """Build the response plans API path from configured components.

        Returns:
            The complete response plans API path.
        """
        return _build_response_plan_api_path(self.api_namespace, self.api_user, self.api_app)

    def _configure_api(self) -> None:
        """Configure API path components from task arguments."""
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)
        self.api_object = self._build_api_path()
        display.vv(f"splunk_response_plan: using API path: {self.api_object}")

    def _build_response_plan_params(self) -> dict[str, Any]:
        """Build response plan dictionary from task arguments.

        Returns:
            Dictionary containing response plan parameters from task args.
        """
        response_plan = {}

        name = self._task.args.get("name")
        if name:
            response_plan["name"] = name

        param_keys = [
            "description",
            "template_status",
            "phases",
        ]
        for key in param_keys:
            value = self._task.args.get(key)
            if value is not None:
                response_plan[key] = value

        return response_plan

    def _set_result_message(self, action: str, changed: bool) -> None:
        """Set the appropriate result message based on check mode and action.

        Args:
            action: The action performed (created, updated, deleted).
            changed: Whether the operation resulted in changes.
        """
        if self._task.check_mode:
            if changed:
                self._result["msg"] = f"Check mode: would {action.rstrip('ed')}e response plan"
            else:
                self._result["msg"] = "Check mode: no changes required"
        else:
            if changed:
                self._result["msg"] = f"Response plan {action} successfully"
            else:
                self._result["msg"] = "No changes required"

    def _validate_unique_phase_names(
        self,
        phases: list[dict[str, Any]],
    ) -> list[str]:
        """Validate that all phase names are unique within the response plan.

        Args:
            phases: List of phase dictionaries.

        Returns:
            List of error messages for any duplicate phase names found.
        """
        errors = []
        phase_names: dict[str, int] = {}

        for phase in phases or []:
            phase_name = phase.get("name", "")
            if phase_name in phase_names:
                errors.append(f"Duplicate phase name '{phase_name}' found in response plan")
            else:
                phase_names[phase_name] = 1

        return errors

    def _validate_unique_task_names(
        self,
        phases: list[dict[str, Any]],
    ) -> list[str]:
        """Validate that all task names are unique within each phase.

        Args:
            phases: List of phase dictionaries containing tasks.

        Returns:
            List of error messages for any duplicate task names found.
        """
        errors = []

        for phase in phases or []:
            phase_name = phase.get("name", "")
            task_names: dict[str, int] = {}

            for task in phase.get("tasks", []) or []:
                task_name = task.get("name", "")
                if task_name in task_names:
                    errors.append(
                        f"Duplicate task name '{task_name}' found in phase '{phase_name}'",
                    )
                else:
                    task_names[task_name] = 1

        return errors

    def _validate_response_plan(
        self,
        response_plan: dict[str, Any],
    ) -> list[str]:
        """Validate response plan structure for uniqueness constraints.

        Checks for:
        - Duplicate phase names within the response plan
        - Duplicate task names within each phase

        Args:
            response_plan: The response plan parameters to validate.

        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors = []
        phases = response_plan.get("phases", [])

        errors.extend(self._validate_unique_phase_names(phases))
        errors.extend(self._validate_unique_task_names(phases))

        return errors

    def get_response_plan_by_name(
        self,
        conn_request: SplunkRequest,
        name: str,
    ) -> dict[str, Any] | None:
        """Get an existing response plan by its name.

        Args:
            conn_request: The SplunkRequest instance.
            name: The response plan name to search for.

        Returns:
            The existing response plan if found, None otherwise.
        """
        display.vv(f"splunk_response_plan: looking up response plan by name: {name}")

        response = conn_request.get_by_path(self.api_object)

        if not response or "items" not in response:
            display.vv("splunk_response_plan: no response plans found")
            return None

        plans = response.get("items", [])

        # Find response plan by name
        for plan in plans:
            if plan.get("name") == name:
                display.vv(f"splunk_response_plan: found response plan with id: {plan.get('id')}")
                return plan

        display.vv(f"splunk_response_plan: no response plan found with name: {name}")
        return None

    def _post_response_plan(
        self,
        conn_request: SplunkRequest,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send response plan payload to API for creation.

        Args:
            conn_request: The SplunkRequest instance.
            payload: The response plan API payload.

        Returns:
            Parsed response plan from API response.
        """
        display.vvv(f"splunk_response_plan: posting to {self.api_object}")
        display.vvv(f"splunk_response_plan: payload: {payload}")
        api_response = conn_request.create_update(self.api_object, data=payload, json_payload=True)

        after = {}
        if api_response:
            display.vvv(f"splunk_response_plan: API response: {api_response}")
            after = _map_response_plan_from_api(api_response)

        return after

    def _post_update(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send response plan payload to API for update.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the response plan to update.
            payload: The response plan API payload.

        Returns:
            Parsed response plan from API response.
        """
        update_url = _build_response_plan_update_path(
            ref_id,
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

        display.vvv(f"splunk_response_plan: posting update to {update_url}")
        display.vvv(f"splunk_response_plan: update payload: {payload}")

        api_response = conn_request.create_update(
            update_url,
            data=payload,
            json_payload=True,
        )

        after = {}
        if api_response:
            display.vvv(f"splunk_response_plan: update API response: {api_response}")
            after = _map_response_plan_from_api(api_response)

        return after

    def create_response_plan(
        self,
        conn_request: SplunkRequest,
        response_plan: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Create a new response plan.

        Args:
            conn_request: The SplunkRequest instance.
            response_plan: The response plan parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        name = response_plan.get("name", "")
        display.v(f"splunk_response_plan: creating new response plan: {name}")

        # Build API payload (no existing data for create)
        payload = _map_response_plan_to_api(response_plan)

        if self._task.check_mode:
            display.v("splunk_response_plan: check mode - would create response plan")
            after = _map_response_plan_from_api(payload)
            return {"before": None, "after": after}, True

        after = self._post_response_plan(conn_request, payload)

        display.v("splunk_response_plan: created response plan successfully")
        return {"before": None, "after": after}, True

    def update_response_plan(
        self,
        conn_request: SplunkRequest,
        existing: dict[str, Any],
        response_plan: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Update an existing response plan.

        Args:
            conn_request: The SplunkRequest instance.
            existing: The existing response plan from API.
            response_plan: The desired response plan parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        ref_id = existing.get("id")
        name = response_plan.get("name", "")
        display.v(f"splunk_response_plan: updating response plan: {name} (id: {ref_id})")

        # Map existing to module format for before state
        before = _map_response_plan_from_api(existing)

        # Build API payload with ID matching from existing data
        payload = _map_response_plan_to_api(response_plan, existing)

        # Map payload back to module format for comparison
        desired = _map_response_plan_from_api(payload)

        # Check if there are any differences
        if before == desired:
            display.v("splunk_response_plan: no changes needed")
            return {"before": before, "after": before}, False

        if self._task.check_mode:
            display.v("splunk_response_plan: check mode - would update response plan")
            return {"before": before, "after": desired}, True

        after = self._post_update(conn_request, ref_id, payload)

        display.v("splunk_response_plan: updated response plan successfully")
        return {"before": before, "after": after}, True

    def delete_response_plan(
        self,
        conn_request: SplunkRequest,
        existing: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Delete an existing response plan.

        Args:
            conn_request: The SplunkRequest instance.
            existing: The existing response plan from API.

        Returns:
            Tuple of (result_dict, changed).
        """
        ref_id = existing.get("id")
        name = existing.get("name", "")
        display.v(f"splunk_response_plan: deleting response plan: {name} (id: {ref_id})")

        # Map existing to module format for before state
        before = _map_response_plan_from_api(existing)

        if self._task.check_mode:
            display.v("splunk_response_plan: check mode - would delete response plan")
            return {"before": before, "after": None}, True

        delete_url = _build_response_plan_update_path(
            ref_id,
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

        display.vvv(f"splunk_response_plan: deleting at {delete_url}")
        conn_request.delete_by_path(delete_url)

        display.v("splunk_response_plan: deleted response plan successfully")
        return {"before": before, "after": None}, True

    def _handle_present(
        self,
        conn_request: SplunkRequest,
        existing: dict[str, Any] | None,
        response_plan: dict[str, Any],
    ) -> bool:
        """Handle state=present operation.

        Args:
            conn_request: The SplunkRequest instance.
            existing: The existing response plan if found, None otherwise.
            response_plan: The desired response plan parameters.

        Returns:
            True if operation completed successfully, False if error occurred.
        """
        # Validate phases required for present state
        if not response_plan.get("phases"):
            self._result["failed"] = True
            self._result["msg"] = "Missing required parameter: phases (required when state=present)"
            return False

        # Validate uniqueness of phase and task names
        validation_errors = self._validate_response_plan(response_plan)
        if validation_errors:
            self._result["failed"] = True
            self._result["msg"] = "Validation failed: " + "; ".join(validation_errors)
            display.v(f"splunk_response_plan: validation failed: {validation_errors}")
            return False

        if existing:
            # Update existing response plan
            result, changed = self.update_response_plan(conn_request, existing, response_plan)
            self._result[self.module_name] = result
            self._result["changed"] = changed
            self._set_result_message("updated", changed)
        else:
            # Create new response plan
            result, changed = self.create_response_plan(conn_request, response_plan)
            self._result[self.module_name] = result
            self._result["changed"] = changed
            self._set_result_message("created", changed)

        return True

    def _handle_absent(
        self,
        conn_request: SplunkRequest,
        existing: dict[str, Any] | None,
    ) -> None:
        """Handle state=absent operation.

        Args:
            conn_request: The SplunkRequest instance.
            existing: The existing response plan if found, None otherwise.
        """
        if not existing:
            # Already absent, nothing to do
            display.v("splunk_response_plan: response plan not found, already absent")
            self._result[self.module_name] = {"before": None, "after": None}
            self._result["changed"] = False
            self._result["msg"] = "Response plan not found, already absent"
            return

        # Delete existing response plan
        result, changed = self.delete_response_plan(conn_request, existing)
        self._result[self.module_name] = result
        self._result["changed"] = changed
        self._set_result_message("deleted", changed)

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_response_plan: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_response_plan: argument validation failed: {self._result.get('msg')}",
            )
            return self._result

        # Initialize result structure
        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        # Extract parameters
        name = self._task.args.get("name")
        state = self._task.args.get("state", "present")
        response_plan = self._build_response_plan_params()

        display.vv(f"splunk_response_plan: name: {name}")
        display.vv(f"splunk_response_plan: state: {state}")
        display.vvv(f"splunk_response_plan: response_plan parameters: {response_plan}")

        # Validate name is provided
        if not name:
            self._result["failed"] = True
            self._result["msg"] = "Missing required parameter: name"
            return self._result

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=["state", "api_namespace", "api_user", "api_app"],
        )

        # Lookup existing response plan by name
        existing = self.get_response_plan_by_name(conn_request, name)

        # Route based on state
        if state == "absent":
            self._handle_absent(conn_request, existing)
        elif not self._handle_present(conn_request, existing, response_plan):
            # _handle_present returns False on validation failure
            return self._result

        display.v(f"splunk_response_plan: completed with changed={self._result['changed']}")
        return self._result
