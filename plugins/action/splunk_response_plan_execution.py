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
        tasks_updated = []
        any_changed = False

        applied_plan_id = applied_plan.get("id", "")
        phases = applied_plan.get("phases", [])

        for task_config in tasks_config:
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
                tasks_updated.append(
                    {
                        "phase_name": phase_name,
                        "task_name": task_name,
                        "error": f"Phase '{phase_name}' not found",
                        "changed": False,
                    },
                )
                continue

            # Find the task
            task = self._find_task_by_name(phase.get("tasks", []), task_name)
            if not task:
                display.warning(
                    f"splunk_response_plan_execution: task '{task_name}' not found in phase "
                    f"'{phase_name}', skipping",
                )
                tasks_updated.append(
                    {
                        "phase_name": phase_name,
                        "task_name": task_name,
                        "error": f"Task '{task_name}' not found in phase '{phase_name}'",
                        "changed": False,
                    },
                )
                continue

            phase_id = phase.get("id", "")
            task_id = task.get("id", "")

            # Check if update is needed (idempotency)
            current_status = task.get("status", "")
            current_owner = task.get("owner", "")

            status_needs_update = desired_status and desired_status != current_status
            owner_needs_update = desired_owner and desired_owner != current_owner

            if not status_needs_update and not owner_needs_update:
                display.vv(
                    f"splunk_response_plan_execution: task '{task_name}' already in desired state",
                )
                tasks_updated.append(
                    {
                        "phase_name": phase_name,
                        "task_name": task_name,
                        "status": current_status,
                        "owner": current_owner,
                        "changed": False,
                    },
                )
                continue

            # Update the task
            if self._task.check_mode:
                display.v(
                    f"splunk_response_plan_execution: check mode - would update task '{task_name}'",
                )
                tasks_updated.append(
                    {
                        "phase_name": phase_name,
                        "task_name": task_name,
                        "status": desired_status or current_status,
                        "owner": desired_owner or current_owner,
                        "changed": True,
                    },
                )
                any_changed = True
                continue

            self._update_task(
                conn_request,
                investigation_id,
                applied_plan_id,
                phase_id,
                task_id,
                desired_status if status_needs_update else None,
                desired_owner if owner_needs_update else None,
            )

            tasks_updated.append(
                {
                    "phase_name": phase_name,
                    "task_name": task_name,
                    "status": desired_status or current_status,
                    "owner": desired_owner or current_owner,
                    "changed": True,
                },
            )
            any_changed = True

        return tasks_updated, any_changed

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

        before_state = {
            "applied": existing_plan is not None,
        }
        if existing_plan:
            before_state["applied_plan_id"] = existing_plan.get("id")
            before_state["response_plan_id"] = template_id

        # Apply if not already applied
        if existing_plan:
            display.v("splunk_response_plan_execution: response plan already applied")
            applied_plan = existing_plan
            plan_changed = False
        else:
            if self._task.check_mode:
                display.v("splunk_response_plan_execution: check mode - would apply response plan")
                self._result[self.module_name] = {
                    "before": before_state,
                    "after": {
                        "applied": True,
                        "response_plan_id": template_id,
                    },
                }
                self._result["changed"] = True
                self._result["msg"] = "Check mode: would apply response plan"
                return

            applied_plan_response = self._apply_response_plan(
                conn_request,
                investigation_id,
                template_id,
            )
            applied_plan = applied_plan_response
            plan_changed = True
            display.v("splunk_response_plan_execution: response plan applied successfully")

        # Build after state
        after_state = {
            "applied": True,
            "applied_plan_id": applied_plan.get("id", ""),
            "response_plan_id": template_id,
        }

        # Process tasks if provided
        tasks_updated = []
        tasks_changed = False

        if tasks_config:
            # Need to get fresh applied plan data with phases/tasks
            if plan_changed or not existing_plan:
                # Re-fetch to get the full structure
                applied_plans = self._get_applied_response_plans(conn_request, investigation_id)
                applied_plan = self._find_applied_plan_by_name(applied_plans, template_name)

            if applied_plan:
                # Map to module format for task processing
                mapped_plan = map_applied_response_plan_from_api(applied_plan)
                tasks_updated, tasks_changed = self._process_tasks(
                    conn_request,
                    investigation_id,
                    mapped_plan,
                    tasks_config,
                )

        # Set result
        self._result[self.module_name] = {
            "before": before_state,
            "after": after_state,
        }
        if tasks_updated:
            self._result[self.module_name]["tasks_updated"] = tasks_updated

        self._result["changed"] = plan_changed or tasks_changed

        if plan_changed and tasks_changed:
            self._result["msg"] = "Response plan applied and tasks updated successfully"
        elif plan_changed:
            self._result["msg"] = "Response plan applied successfully"
        elif tasks_changed:
            self._result["msg"] = "Tasks updated successfully"
        else:
            self._result["msg"] = "No changes required"

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
