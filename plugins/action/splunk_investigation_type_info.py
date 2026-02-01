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
The action plugin file for splunk_investigation_type_info
"""

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

from ansible_collections.splunk.es.plugins.module_utils.investigation_type import (
    build_investigation_type_api_path,
    build_investigation_type_path_by_name,
    map_investigation_type_from_api,
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
from ansible_collections.splunk.es.plugins.modules.splunk_investigation_type_info import (
    DOCUMENTATION,
)


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for querying Splunk ES investigation types."""

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
        """Build the investigation types API path from configured components.

        Returns:
            The complete investigation types API path.
        """
        return build_investigation_type_api_path(
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

    def get_all_investigation_types(
        self,
        conn_request: SplunkRequest,
    ) -> list[dict[str, Any]]:
        """Get all investigation types from the API.

        Args:
            conn_request: The SplunkRequest instance.

        Returns:
            List of all investigation types.
        """
        display.vv("splunk_investigation_type_info: fetching all investigation types")

        response = conn_request.get_by_path(self.api_object)

        investigation_types = []
        if response and "items" in response:
            display.vvv(
                f"splunk_investigation_type_info: raw API response type: {type(response)}",
            )

            for item in response.get("items", []):
                if item:
                    mapped = map_investigation_type_from_api(item)
                    if mapped:
                        investigation_types.append(mapped)

            display.vv(
                f"splunk_investigation_type_info: found {len(investigation_types)} "
                "investigation types",
            )

        return investigation_types

    def get_investigation_type_by_name(
        self,
        conn_request: SplunkRequest,
        name: str,
    ) -> dict[str, Any] | None:
        """Get a specific investigation type by name.

        Args:
            conn_request: The SplunkRequest instance.
            name: The investigation type name to query.

        Returns:
            The investigation type if found, None otherwise.
        """
        display.vv(f"splunk_investigation_type_info: fetching investigation type: {name}")

        get_path = build_investigation_type_path_by_name(
            name,
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

        try:
            response = conn_request.get_by_path(get_path)
            if response and response.get("incident_type"):
                display.vv(
                    f"splunk_investigation_type_info: found investigation type: "
                    f"{response.get('incident_type')}",
                )
                return map_investigation_type_from_api(response)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                display.vv(
                    f"splunk_investigation_type_info: investigation type not found: {name}",
                )
                return None
            raise

        return None

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_investigation_type_info: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_investigation_type_info: argument validation failed: "
                f"{self._result.get('msg')}",
            )
            return self._result

        # Get API path configuration from task args
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)

        # Build the API path
        self.api_object = self._build_api_path()
        display.vv(f"splunk_investigation_type_info: using API path: {self.api_object}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "name",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        # Get query parameters
        name = self._task.args.get("name")

        try:
            if name:
                # Query specific investigation type by name
                display.v(f"splunk_investigation_type_info: querying by name: {name}")
                investigation_type = self.get_investigation_type_by_name(conn_request, name)

                if investigation_type:
                    self._result["investigation_types"] = [investigation_type]
                else:
                    self._result["investigation_types"] = []

            else:
                # Return all investigation types
                display.v("splunk_investigation_type_info: querying all investigation types")
                self._result["investigation_types"] = self.get_all_investigation_types(
                    conn_request,
                )

            self._result["changed"] = False
            display.v(
                f"splunk_investigation_type_info: returning "
                f"{len(self._result['investigation_types'])} investigation type(s)",
            )

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                # Handle 404 gracefully - return empty list
                self._result["changed"] = False
                self._result["investigation_types"] = []
                display.v("splunk_investigation_type_info: no investigation types found (404)")
            else:
                self.fail_json(
                    msg=f"Failed to query investigation type(s): {error_msg}",
                )

        return self._result
