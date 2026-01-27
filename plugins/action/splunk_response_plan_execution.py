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
The action module for splunk_response_plan_execution
"""

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

from ansible_collections.splunk.es.plugins.module_utils.response_plan_execution import (
    map_applied_response_plan_from_api,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    check_argspec,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    is_uuid,
)
from ansible_collections.splunk.es.plugins.modules.splunk_response_plan_execution import (
    DOCUMENTATION,
)


# Initialize display for debug output
display = Display()

# Task status mappings: module value -> API value (for sending to API)
TASK_STATUS_TO_API = {
    "started": "Started",
    "ended": "Ended",
    "reopened": "Reopened",
    "pending": "Pending",
}


class ActionModule(ActionBase):
    """Action module for managing Splunk ES response plan execution."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result: dict[str, Any] = {}
        self.module_name = "response_plan_execution"
        self.api_namespace = DEFAULT_API_NAMESPACE
        self.api_user = DEFAULT_API_USER
        self.api_app = DEFAULT_API_APP

    def fail_json(self, msg: str) -> None:
        """Raise an AnsibleActionFail with a cleaned up message.

        Args:
            msg: The message for the failure.

        Raises:
            AnsibleActionFail: Always raised with the provided message.
        """
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def _configure_api(self) -> None:
        """Configure API path components from task arguments."""
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)
        display.vv(
            f"splunk_response_plan_execution: API config - "
            f"namespace={self.api_namespace}, user={self.api_user}, app={self.api_app}",
        )

    def _build_response_plans_path(self, investigation_id: str) -> str:
        """Build the API path for incident response plans.

        Args:
            investigation_id: The investigation/incident UUID.

        Returns:
            The complete API path for incident response plans.
        """
        return (
            f"{self.api_namespace}/{self.api_user}/{self.api_app}"
            f"/v1/incidents/{investigation_id}/responseplans"
        )

    def _build_response_plan_path(self, investigation_id: str, applied_plan_id: str) -> str:
        """Build the API path for a specific applied response plan.

        Args:
            investigation_id: The investigation/incident UUID.
            applied_plan_id: The applied response plan instance ID.

        Returns:
            The API path for the specific applied response plan.
        """
        return f"{self._build_response_plans_path(investigation_id)}/{applied_plan_id}"

    def _build_task_path(
        self,
        investigation_id: str,
        applied_plan_id: str,
        phase_id: str,
        task_id: str,
    ) -> str:
        """Build the API path for a specific task within an applied response plan.

        Args:
            investigation_id: The investigation/incident UUID.
            applied_plan_id: The applied response plan instance ID.
            phase_id: The phase ID containing the task.
            task_id: The task ID.

        Returns:
            The API path for the specific task.
        """
        plan_path = self._build_response_plan_path(investigation_id, applied_plan_id)
        return f"{plan_path}/phase/{phase_id}/tasks/{task_id}"

    def _build_templates_path(self) -> str:
        """Build the API path for response templates (for name-to-ID lookup).

        Returns:
            The complete API path for response templates.
        """
        return f"{self.api_namespace}/{self.api_user}/{self.api_app}/v1/responsetemplates"

    def _find_phase_by_name(
        self,
        phases: list[dict[str, Any]],
        phase_name: str,
    ) -> dict[str, Any] | None:
        """Find a phase by name within a list of phases.

        Args:
            phases: List of phase dictionaries.
            phase_name: The phase name to search for.

        Returns:
            The matching phase dictionary, or None if not found.
        """
        for phase in phases:
            if phase.get("name") == phase_name:
                return phase
        return None

    def _find_task_by_name(
        self,
        tasks: list[dict[str, Any]],
        task_name: str,
    ) -> dict[str, Any] | None:
        """Find a task by name within a list of tasks.

        Args:
            tasks: List of task dictionaries.
            task_name: The task name to search for.

        Returns:
            The matching task dictionary, or None if not found.
        """
        for task in tasks:
            if task.get("name") == task_name:
                return task
        return None

    def _get_response_templates(
        self,
        conn_request: SplunkRequest,
    ) -> list[dict[str, Any]]:
        """Fetch all response plan templates from the API.

        Args:
            conn_request: The SplunkRequest instance.

        Returns:
            List of response plan templates.
        """
        templates_path = self._build_templates_path()
        response = conn_request.get_by_path(templates_path)
        if not response or "items" not in response:
            return []
        return response.get("items", [])

    def _get_template_name_by_id(
        self,
        templates: list[dict[str, Any]],
        template_id: str,
    ) -> str | None:
        """Look up a response plan template name by its ID.

        Args:
            templates: List of response plan templates.
            template_id: The template UUID to look up.

        Returns:
            The template name, or None if not found.
        """
        for template in templates:
            if template.get("id") == template_id:
                return template.get("name")
        return None

    def _get_template_id_by_name(
        self,
        templates: list[dict[str, Any]],
        template_name: str,
    ) -> str | None:
        """Look up a response plan template ID by its name.

        Args:
            templates: List of response plan templates.
            template_name: The template name to look up.

        Returns:
            The template ID, or None if not found.
        """
        for template in templates:
            if template.get("name") == template_name:
                return template.get("id")
        return None

    def _get_applied_response_plans(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
    ) -> list[dict[str, Any]]:
        """Get all response plans applied to an investigation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.

        Returns:
            List of applied response plans.
        """
        api_path = (
            f"{self.api_namespace}/{self.api_user}/{self.api_app}"
            f"/v1/incidents/{investigation_id}"
        )
        display.vvv(f"splunk_response_plan_execution: GET {api_path}")

        response = conn_request.get_by_path(api_path)
        if not response:
            return []

        # Extract response_plans from the incident details
        response_plans = response.get("response_plans")
        if response_plans is None:
            return []
        return response_plans

    def _find_applied_plan_by_name(
        self,
        applied_plans: list[dict[str, Any]],
        plan_name: str,
    ) -> dict[str, Any] | None:
        """Find an applied response plan by its name.

        Note: The GET /v1/incidents/{id} response doesn't include source_template_id
        in the applied plans, so we match by name instead.

        Args:
            applied_plans: List of applied response plans.
            plan_name: The response plan name to match.

        Returns:
            The matching applied plan, or None if not found.
        """
        for plan in applied_plans:
            if plan.get("name") == plan_name:
                return plan
        return None

    def _apply_response_plan(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        template_id: str,
    ) -> dict[str, Any]:
        """Apply a response plan to an investigation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            template_id: The response plan template ID to apply.

        Returns:
            The applied response plan from API response.
        """
        api_path = self._build_response_plans_path(investigation_id)

        payload = {
            "response_template_id": template_id,
            "incidentType": "default",
        }

        display.vvv(f"splunk_response_plan_execution: POST {api_path}")
        display.vvv(f"splunk_response_plan_execution: payload: {payload}")

        response = conn_request.create_update(api_path, data=payload, json_payload=True)
        display.vvv(f"splunk_response_plan_execution: apply response: {response}")

        return response or {}

    def _remove_response_plan(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        applied_plan_id: str,
    ) -> None:
        """Remove an applied response plan from an investigation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            applied_plan_id: The applied response plan instance ID.
        """
        api_path = self._build_response_plan_path(investigation_id, applied_plan_id)

        display.vvv(f"splunk_response_plan_execution: DELETE {api_path}")
        conn_request.delete_by_path(api_path)

    def _update_task(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        applied_plan_id: str,
        phase_id: str,
        task_id: str,
        status: str | None,
        owner: str | None,
    ) -> dict[str, Any]:
        """Update a task's status and/or owner.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            applied_plan_id: The applied response plan instance ID.
            phase_id: The phase ID.
            task_id: The task ID.
            status: The new task status (started/ended), or None to skip.
            owner: The new task owner, or None to skip.

        Returns:
            The API response.
        """
        api_path = self._build_task_path(investigation_id, applied_plan_id, phase_id, task_id)

        payload: dict[str, Any] = {}
        if status:
            payload["status"] = TASK_STATUS_TO_API.get(status, status)
        if owner:
            payload["owner"] = owner

        display.vvv(f"splunk_response_plan_execution: POST {api_path}")
        display.vvv(f"splunk_response_plan_execution: task payload: {payload}")

        response = conn_request.create_update(api_path, data=payload, json_payload=True)
        display.vvv(f"splunk_response_plan_execution: task update response: {response}")

        return response or {}

    def _build_task_error_result(
        self,
        phase_name: str,
        task_name: str,
        error_msg: str,
    ) -> dict[str, Any]:
        """Build an error result for a task operation.

        Args:
            phase_name: The phase name.
            task_name: The task name.
            error_msg: The error message.

        Returns:
            A task result dictionary with error information.
        """
        return {
            "phase_name": phase_name,
            "task_name": task_name,
            "error": error_msg,
            "changed": False,
        }

    def _build_task_result(
        self,
        phase_name: str,
        task_name: str,
        status: str,
        owner: str,
        changed: bool,
    ) -> dict[str, Any]:
        """Build a result dictionary for a task operation.

        Args:
            phase_name: The phase name.
            task_name: The task name.
            status: The task status.
            owner: The task owner.
            changed: Whether the task was changed.

        Returns:
            A task result dictionary.
        """
        return {
            "phase_name": phase_name,
            "task_name": task_name,
            "status": status,
            "owner": owner,
            "changed": changed,
        }

    def _process_single_task(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        applied_plan_id: str,
        phases: list[dict[str, Any]],
        task_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Process a single task update.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            applied_plan_id: The applied plan ID.
            phases: List of phases in the applied plan.
            task_config: The task configuration from module parameters.

        Returns:
            A task result dictionary.
        """
        phase_name = task_config.get("phase_name", "")
        task_name = task_config.get("task_name", "")
        desired_status = task_config.get("status")
        desired_owner = task_config.get("owner")

        # Find the phase
        phase = self._find_phase_by_name(phases, phase_name)
        if not phase:
            display.warning(
                f"splunk_response_plan_execution: phase '{phase_name}' not found, skipping task",
            )
            return self._build_task_error_result(
                phase_name,
                task_name,
                f"Phase '{phase_name}' not found",
            )

        # Find the task
        task = self._find_task_by_name(phase.get("tasks", []), task_name)
        if not task:
            display.warning(
                f"splunk_response_plan_execution: task '{task_name}' not found in phase "
                f"'{phase_name}', skipping",
            )
            return self._build_task_error_result(
                phase_name,
                task_name,
                f"Task '{task_name}' not found in phase '{phase_name}'",
            )

        current_status = task.get("status", "")
        current_owner = task.get("owner", "")
        status_needs_update = desired_status and desired_status != current_status
        owner_needs_update = desired_owner and desired_owner != current_owner

        # No update needed - already in desired state
        if not status_needs_update and not owner_needs_update:
            display.vv(
                f"splunk_response_plan_execution: task '{task_name}' already in desired state",
            )
            return self._build_task_result(
                phase_name,
                task_name,
                current_status,
                current_owner,
                changed=False,
            )

        final_status = desired_status or current_status
        final_owner = desired_owner or current_owner

        # Check mode - don't make actual changes
        if self._task.check_mode:
            display.v(
                f"splunk_response_plan_execution: check mode - would update task '{task_name}'",
            )
            return self._build_task_result(
                phase_name,
                task_name,
                final_status,
                final_owner,
                changed=True,
            )

        # Perform the update
        self._update_task(
            conn_request,
            investigation_id,
            applied_plan_id,
            phase.get("id", ""),
            task.get("id", ""),
            desired_status if status_needs_update else None,
            desired_owner if owner_needs_update else None,
        )

        return self._build_task_result(
            phase_name,
            task_name,
            final_status,
            final_owner,
            changed=True,
        )

    def _process_tasks(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        applied_plan: dict[str, Any],
        tasks_config: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], bool]:
        """Process task updates for an applied response plan.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            applied_plan: The applied response plan (with phases/tasks).
            tasks_config: List of task configurations from module parameters.

        Returns:
            Tuple of (tasks_updated list, any_changed boolean).
        """
        applied_plan_id = applied_plan.get("id", "")
        phases = applied_plan.get("phases", [])

        tasks_updated = []
        for task_config in tasks_config:
            result = self._process_single_task(
                conn_request,
                investigation_id,
                applied_plan_id,
                phases,
                task_config,
            )
            tasks_updated.append(result)

        any_changed = any(task.get("changed", False) for task in tasks_updated)
        return tasks_updated, any_changed

    def _build_before_state(
        self,
        existing_plan: dict[str, Any] | None,
        template_id: str,
    ) -> dict[str, Any]:
        """Build the before state for result output.

        Args:
            existing_plan: The existing applied plan, if any.
            template_id: The response plan template ID.

        Returns:
            The before state dictionary.
        """
        before_state: dict[str, Any] = {"applied": existing_plan is not None}
        if existing_plan:
            before_state["applied_plan_id"] = existing_plan.get("id")
            before_state["response_plan_id"] = template_id
        return before_state

    def _get_result_message(self, plan_changed: bool, tasks_changed: bool) -> str:
        """Get the result message based on what changed.

        Args:
            plan_changed: Whether the plan was applied/changed.
            tasks_changed: Whether any tasks were updated.

        Returns:
            The appropriate result message.
        """
        if plan_changed and tasks_changed:
            return "Response plan applied and tasks updated successfully"
        if plan_changed:
            return "Response plan applied successfully"
        if tasks_changed:
            return "Tasks updated successfully"
        return "No changes required"

    def _process_tasks_if_configured(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        template_name: str,
        tasks_config: list[dict[str, Any]] | None,
        plan_changed: bool,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Process task updates if task configuration is provided.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            template_name: The response plan template name.
            tasks_config: Optional list of task configurations.
            plan_changed: Whether the plan was just applied.

        Returns:
            Tuple of (tasks_updated list, tasks_changed boolean).
        """
        if not tasks_config:
            return [], False

        # Re-fetch to get the full structure with phases/tasks
        applied_plans = self._get_applied_response_plans(conn_request, investigation_id)
        applied_plan = self._find_applied_plan_by_name(applied_plans, template_name)

        if not applied_plan:
            return [], False

        mapped_plan = map_applied_response_plan_from_api(applied_plan)
        return self._process_tasks(
            conn_request,
            investigation_id,
            mapped_plan,
            tasks_config,
        )

    def _handle_present(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        template_id: str,
        template_name: str,
        tasks_config: list[dict[str, Any]] | None,
    ) -> None:
        """Handle state=present operation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            template_id: The response plan template ID.
            template_name: The response plan template name.
            tasks_config: Optional list of task configurations.
        """
        display.v(f"splunk_response_plan_execution: applying response plan to {investigation_id}")

        # Get current applied plans
        applied_plans = self._get_applied_response_plans(conn_request, investigation_id)
        display.vv(f"splunk_response_plan_execution: found {len(applied_plans)} applied plans")
        existing_plan = self._find_applied_plan_by_name(applied_plans, template_name)
        display.vv(
            f"splunk_response_plan_execution: existing plan found: {existing_plan is not None}",
        )

        before_state = self._build_before_state(existing_plan, template_id)

        # Handle check mode for applying a new plan
        if not existing_plan and self._task.check_mode:
            display.v("splunk_response_plan_execution: check mode - would apply response plan")
            self._result[self.module_name] = {
                "before": before_state,
                "after": {"applied": True, "response_plan_id": template_id},
            }
            self._result["changed"] = True
            self._result["msg"] = "Check mode: would apply response plan"
            return

        # Apply or use existing plan
        if existing_plan:
            display.v("splunk_response_plan_execution: response plan already applied")
            applied_plan = existing_plan
            plan_changed = False
        else:
            applied_plan = self._apply_response_plan(conn_request, investigation_id, template_id)
            plan_changed = True
            display.v("splunk_response_plan_execution: response plan applied successfully")

        # Process tasks if configured
        tasks_updated, tasks_changed = self._process_tasks_if_configured(
            conn_request,
            investigation_id,
            template_name,
            tasks_config,
            plan_changed,
        )

        # Build result
        after_state = {
            "applied": True,
            "applied_plan_id": applied_plan.get("id", ""),
            "response_plan_id": template_id,
        }

        self._result[self.module_name] = {"before": before_state, "after": after_state}
        if tasks_updated:
            self._result[self.module_name]["tasks_updated"] = tasks_updated

        self._result["changed"] = plan_changed or tasks_changed
        self._result["msg"] = self._get_result_message(plan_changed, tasks_changed)

    def _handle_absent(
        self,
        conn_request: SplunkRequest,
        investigation_id: str,
        template_id: str,
        template_name: str,
    ) -> None:
        """Handle state=absent operation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_id: The investigation UUID.
            template_id: The response plan template ID.
            template_name: The response plan template name.
        """
        display.v(
            f"splunk_response_plan_execution: removing response plan from {investigation_id}",
        )

        # Get current applied plans
        applied_plans = self._get_applied_response_plans(conn_request, investigation_id)
        existing_plan = self._find_applied_plan_by_name(applied_plans, template_name)

        before_state = {
            "applied": existing_plan is not None,
        }
        if existing_plan:
            before_state["applied_plan_id"] = existing_plan.get("id")
            before_state["response_plan_id"] = template_id

        after_state = {
            "applied": False,
        }

        if not existing_plan:
            display.v(
                "splunk_response_plan_execution: response plan not applied, nothing to remove",
            )
            self._result[self.module_name] = {
                "before": before_state,
                "after": after_state,
            }
            self._result["changed"] = False
            self._result["msg"] = "Response plan not applied, already absent"
            return

        if self._task.check_mode:
            display.v("splunk_response_plan_execution: check mode - would remove response plan")
            self._result[self.module_name] = {
                "before": before_state,
                "after": after_state,
            }
            self._result["changed"] = True
            self._result["msg"] = "Check mode: would remove response plan"
            return

        # Remove the response plan
        applied_plan_id = existing_plan.get("id", "")
        self._remove_response_plan(conn_request, investigation_id, applied_plan_id)

        self._result[self.module_name] = {
            "before": before_state,
            "after": after_state,
        }
        self._result["changed"] = True
        self._result["msg"] = "Response plan removed successfully"
        display.v("splunk_response_plan_execution: response plan removed successfully")

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_response_plan_execution: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_response_plan_execution: argument validation failed: "
                f"{self._result.get('msg')}",
            )
            return self._result

        # Initialize result structure
        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        # Extract parameters
        investigation_id = self._task.args.get("investigation_ref_id")
        response_plan = self._task.args.get("response_plan")
        state = self._task.args.get("state", "present")
        tasks_config = self._task.args.get("tasks")

        display.vv(f"splunk_response_plan_execution: investigation_ref_id: {investigation_id}")
        display.vv(f"splunk_response_plan_execution: response_plan: {response_plan}")
        display.vv(f"splunk_response_plan_execution: state: {state}")
        display.vvv(f"splunk_response_plan_execution: tasks: {tasks_config}")

        # Validate required parameters
        if not investigation_id:
            self._result["failed"] = True
            self._result["msg"] = "Missing required parameter: investigation_ref_id"
            return self._result

        if not response_plan:
            self._result["failed"] = True
            self._result["msg"] = "Missing required parameter: response_plan"
            return self._result

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "investigation_ref_id",
                "response_plan",
                "state",
                "tasks",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        # Resolve response plan to template ID and name
        templates = self._get_response_templates(conn_request)
        if not templates:
            self._result["failed"] = True
            self._result["msg"] = "No response plan templates found"
            return self._result

        if is_uuid(response_plan):
            template_id = response_plan
            template_name = self._get_template_name_by_id(templates, template_id)
            display.vv(f"splunk_response_plan_execution: looking up name for ID: {template_id}")
        else:
            template_name = response_plan
            template_id = self._get_template_id_by_name(templates, template_name)
            display.vv(f"splunk_response_plan_execution: looking up ID for name: {template_name}")

        if not template_id or not template_name:
            self._result["failed"] = True
            self._result["msg"] = f"Response plan not found: {response_plan}"
            return self._result

        display.vv(f"splunk_response_plan_execution: resolved template_id: {template_id}")
        display.vv(f"splunk_response_plan_execution: resolved template_name: {template_name}")

        # Route based on state
        if state == "absent":
            self._handle_absent(conn_request, investigation_id, template_id, template_name)
        else:
            self._handle_present(
                conn_request,
                investigation_id,
                template_id,
                template_name,
                tasks_config,
            )

        display.v(
            f"splunk_response_plan_execution: completed with changed={self._result['changed']}",
        )
        return self._result
