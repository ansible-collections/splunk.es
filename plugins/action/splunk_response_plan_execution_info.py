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
The action plugin file for splunk_response_plan_execution_info
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
)
from ansible_collections.splunk.es.plugins.modules.splunk_response_plan_execution_info import (
    DOCUMENTATION,
)


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for querying applied response plans on an investigation."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result: dict[str, Any] = {}
        # API path components - will be set in run() from task args
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
            List of applied response plans from the API.
        """
        api_path = (
            f"{self.api_namespace}/{self.api_user}/{self.api_app}"
            f"/v1/incidents/{investigation_id}"
        )
        display.vvv(f"splunk_response_plan_execution_info: GET {api_path}")

        response = conn_request.get_by_path(api_path)
        if not response:
            return []

        # Extract response_plans from the incident details
        response_plans = response.get("response_plans")
        if response_plans is None:
            return []
        return response_plans

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_response_plan_execution_info: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_response_plan_execution_info: argument validation failed: "
                f"{self._result.get('msg')}",
            )
            return self._result

        # Get API path configuration from task args
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)

        display.vv(
            f"splunk_response_plan_execution_info: API config - "
            f"namespace={self.api_namespace}, user={self.api_user}, app={self.api_app}",
        )

        # Get required parameter
        investigation_id = self._task.args.get("investigation_ref_id")

        if not investigation_id:
            self._result["failed"] = True
            self._result["msg"] = "Missing required parameter: investigation_ref_id"
            return self._result

        display.vv(
            f"splunk_response_plan_execution_info: investigation_ref_id: {investigation_id}",
        )

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "investigation_ref_id",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        try:
            # Fetch applied response plans
            display.v(
                f"splunk_response_plan_execution_info: fetching applied plans for "
                f"{investigation_id}",
            )
            raw_plans = self._get_applied_response_plans(conn_request, investigation_id)

            # Map each plan to module format using existing utility
            applied_plans = []
            for plan in raw_plans:
                mapped_plan = map_applied_response_plan_from_api(plan)
                applied_plans.append(mapped_plan)

            self._result["applied_response_plans"] = applied_plans
            self._result["changed"] = False

            display.v(
                f"splunk_response_plan_execution_info: found {len(applied_plans)} "
                f"applied response plan(s)",
            )

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                # Handle 404 gracefully - investigation not found
                self._result["failed"] = True
                self._result["msg"] = f"Investigation not found: {investigation_id}"
            else:
                self.fail_json(
                    msg=f"Failed to query applied response plans: {error_msg}",
                )

        return self._result
