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
The action plugin file for splunk_response_plan_info
"""

from typing import Any, Optional

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import unquote
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
from ansible_collections.splunk.es.plugins.modules.splunk_response_plan_info import (
    DOCUMENTATION,
)


# Initialize display for debug output
display = Display()


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


def _map_task_info_from_api(task: dict[str, Any]) -> dict[str, Any]:
    """Convert single task from API format to info module format with ID.

    Args:
        task: Task dictionary from API response.

    Returns:
        Task in info module format including ID.
    """
    # Extract searches from suggestions
    searches = []
    suggestions = task.get("suggestions", {}) or {}
    for search in suggestions.get("searches", []) or []:
        searches.append(
            {
                "name": unquote(search.get("name", "")),
                "description": unquote(search.get("description", "")),
                "spl": unquote(search.get("spl", "")),
            },
        )

    return {
        "id": task.get("id", ""),
        "name": unquote(task.get("name", "")),
        "description": unquote(task.get("description", "")),
        "is_note_required": task.get("is_note_required", False),
        "owner": task.get("owner", "unassigned"),
        "searches": searches,
    }


def _map_phase_info_from_api(phase: dict[str, Any]) -> dict[str, Any]:
    """Convert single phase from API format to info module format with ID.

    Args:
        phase: Phase dictionary from API response.

    Returns:
        Phase in info module format including ID.
    """
    tasks = []
    for task in phase.get("tasks", []) or []:
        tasks.append(_map_task_info_from_api(task))

    return {
        "id": phase.get("id", ""),
        "name": unquote(phase.get("name", "")),
        "tasks": tasks,
    }


def _map_response_plan_info_from_api(config: dict[str, Any]) -> dict[str, Any]:
    """Convert API response to info module format with all IDs.

    Args:
        config: The API response config dictionary.

    Returns:
        Dictionary with all fields including IDs for display purposes.
    """
    phases = []
    for phase in config.get("phases", []) or []:
        phases.append(_map_phase_info_from_api(phase))

    return {
        "id": config.get("id", ""),
        "template_id": config.get("template_id", ""),
        "name": unquote(config.get("name", "")),
        "description": unquote(config.get("description", "")),
        "template_status": config.get("template_status", "draft"),
        "phases": phases,
    }


class ActionModule(ActionBase):
    """Action module for querying Splunk ES response plans."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        # API path components - will be set in run() from task args
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

    def _build_query_params(self) -> Optional[dict[str, Any]]:
        """Build query params dict with limit if provided.

        Returns:
            Dict with query params if any are set, None otherwise.
        """
        query_params: dict[str, Any] = {}

        limit = self._task.args.get("limit")
        if limit:
            query_params["limit"] = limit

        return query_params if query_params else None

    def get_all_response_plans(self, conn_request: SplunkRequest) -> list[dict[str, Any]]:
        """Get all response plans from the API.

        Args:
            conn_request: The SplunkRequest instance.

        Returns:
            List of all response plans with IDs included.
        """
        display.vv("splunk_response_plan_info: fetching all response plans")

        query_params = self._build_query_params()
        display.vv(f"splunk_response_plan_info: query_params={query_params}")

        response = conn_request.get_by_path(self.api_object, query_params=query_params)

        response_plans = []
        if response and "items" in response:
            display.vvv(f"splunk_response_plan_info: raw API response type: {type(response)}")

            for plan in response.get("items", []):
                if plan:
                    mapped = _map_response_plan_info_from_api(plan)
                    if mapped:
                        response_plans.append(mapped)

            display.vv(f"splunk_response_plan_info: found {len(response_plans)} response plans")

        return response_plans

    def filter_response_plans_by_name(
        self,
        response_plans: list[dict[str, Any]],
        name: str,
    ) -> list[dict[str, Any]]:
        """Filter response plans by exact name match.

        Args:
            response_plans: List of response plans to filter.
            name: The name to match.

        Returns:
            Filtered list of response plans.
        """
        display.vv(f"splunk_response_plan_info: filtering response plans by name: {name}")

        filtered = [plan for plan in response_plans if plan.get("name") == name]

        display.vv(
            f"splunk_response_plan_info: found {len(filtered)} response plans with matching name",
        )
        return filtered

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_response_plan_info: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_response_plan_info: argument validation failed: "
                f"{self._result.get('msg')}",
            )
            return self._result

        # Get API path configuration from task args
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)

        # Build the API path
        self.api_object = self._build_api_path()
        display.vv(f"splunk_response_plan_info: using API path: {self.api_object}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "name",
                "limit",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        # Get query parameters
        name = self._task.args.get("name")

        try:
            if name:
                # Query all response plans and filter by name
                display.v(f"splunk_response_plan_info: querying by name: {name}")
                all_response_plans = self.get_all_response_plans(conn_request)
                self._result["response_plans"] = self.filter_response_plans_by_name(
                    all_response_plans,
                    name,
                )

            else:
                # Return all response plans
                display.v("splunk_response_plan_info: querying all response plans")
                self._result["response_plans"] = self.get_all_response_plans(conn_request)

            self._result["changed"] = False
            display.v(
                f"splunk_response_plan_info: returning {len(self._result['response_plans'])} "
                "response plan(s)",
            )

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                # Handle 404 gracefully - return empty list
                self._result["changed"] = False
                self._result["response_plans"] = []
                display.v("splunk_response_plan_info: no response plans found (404)")
            else:
                self.fail_json(
                    msg=f"Failed to query response plan(s): {error_msg}",
                )

        return self._result
