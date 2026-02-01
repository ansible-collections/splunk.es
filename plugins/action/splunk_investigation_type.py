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
The action module for splunk_investigation_type
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
    map_investigation_type_to_api_create,
    map_investigation_type_to_api_update,
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
from ansible_collections.splunk.es.plugins.modules.splunk_investigation_type import DOCUMENTATION


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for managing Splunk ES investigation types."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.module_name = "investigation_type"
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

    def _configure_api(self) -> None:
        """Configure API path components from task arguments."""
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)
        self.api_object = self._build_api_path()
        display.vv(f"splunk_investigation_type: using API path: {self.api_object}")

    def _build_investigation_type_params(self) -> dict[str, Any]:
        """Build investigation type dictionary from task arguments.

        Returns:
            Dictionary containing investigation type parameters from task args.
        """
        investigation_type = {}

        param_keys = ["name", "description", "response_plan_ids"]
        for key in param_keys:
            if key in self._task.args:
                value = self._task.args[key]
                # Handle None values - treat as not provided unless it's response_plan_ids
                if value is not None:
                    investigation_type[key] = value
                elif key == "response_plan_ids":
                    investigation_type[key] = []

        return investigation_type

    def _set_result_message(self, action: str, changed: bool) -> None:
        """Set the appropriate result message based on check mode and action.

        Args:
            action: The action performed (created, updated).
            changed: Whether the operation resulted in changes.
        """
        if self._task.check_mode:
            if changed:
                self._result["msg"] = f"Check mode: would {action.rstrip('ed')}e investigation type"
            else:
                self._result["msg"] = "Check mode: no changes required"
        else:
            if changed:
                self._result["msg"] = f"Investigation type {action} successfully"
            else:
                self._result["msg"] = "No changes required"

    def get_investigation_type_by_name(
        self,
        conn_request: SplunkRequest,
        name: str,
    ) -> dict[str, Any] | None:
        """Get an existing investigation type by its name.

        Args:
            conn_request: The SplunkRequest instance.
            name: The investigation type name to search for.

        Returns:
            The existing investigation type if found, None otherwise.
        """
        display.vv(f"splunk_investigation_type: looking up investigation type by name: {name}")

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
                    f"splunk_investigation_type: found investigation type: "
                    f"{response.get('incident_type')}",
                )
                return response
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                display.vv(f"splunk_investigation_type: investigation type not found: {name}")
                return None
            raise

        display.vv(f"splunk_investigation_type: no investigation type found with name: {name}")
        return None

    def _post_investigation_type(
        self,
        conn_request: SplunkRequest,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send investigation type payload to API for creation.

        Args:
            conn_request: The SplunkRequest instance.
            payload: The investigation type API payload.

        Returns:
            Parsed investigation type from API response.
        """
        display.vvv(f"splunk_investigation_type: posting to {self.api_object}")
        display.vvv(f"splunk_investigation_type: payload: {payload}")
        api_response = conn_request.create_update(
            self.api_object,
            data=payload,
            json_payload=True,
        )

        after = {}
        if api_response:
            display.vvv(f"splunk_investigation_type: API response: {api_response}")
            after = map_investigation_type_from_api(api_response)

        return after

    def _put_investigation_type(
        self,
        conn_request: SplunkRequest,
        name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send investigation type payload to API for update.

        Args:
            conn_request: The SplunkRequest instance.
            name: The investigation type name.
            payload: The investigation type API payload.

        Returns:
            Parsed investigation type from API response.
        """
        update_url = build_investigation_type_path_by_name(
            name,
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

        display.vvv(f"splunk_investigation_type: putting update to {update_url}")
        display.vvv(f"splunk_investigation_type: update payload: {payload}")

        api_response = conn_request.update_by_path(update_url, data=payload, json_payload=True)

        after = {}
        if api_response:
            display.vvv(f"splunk_investigation_type: update API response: {api_response}")
            after = map_investigation_type_from_api(api_response)

        return after

    def create_investigation_type(
        self,
        conn_request: SplunkRequest,
        investigation_type: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Create a new investigation type.

        Args:
            conn_request: The SplunkRequest instance.
            investigation_type: The investigation type parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        name = investigation_type.get("name", "")
        display.v(f"splunk_investigation_type: creating new investigation type: {name}")

        # Build API payload for create
        create_payload = map_investigation_type_to_api_create(investigation_type)

        if self._task.check_mode:
            display.v("splunk_investigation_type: check mode - would create investigation type")
            after = map_investigation_type_from_api(
                {
                    "incident_type": investigation_type.get("name", ""),
                    "description": investigation_type.get("description", ""),
                    "response_template_ids": investigation_type.get("response_plan_ids") or [],
                },
            )
            return {"before": None, "after": after}, True

        # POST to create
        after = self._post_investigation_type(conn_request, create_payload)

        # If response_plan_ids provided, need to PUT to associate them
        response_plan_ids = investigation_type.get("response_plan_ids")
        if response_plan_ids:
            display.v(
                f"splunk_investigation_type: associating {len(response_plan_ids)} "
                "response plan(s)",
            )
            update_payload = map_investigation_type_to_api_update(investigation_type)
            after = self._put_investigation_type(conn_request, name, update_payload)

        display.v("splunk_investigation_type: created investigation type successfully")
        return {"before": None, "after": after}, True

    def update_investigation_type(
        self,
        conn_request: SplunkRequest,
        existing: dict[str, Any],
        investigation_type: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Update an existing investigation type.

        Args:
            conn_request: The SplunkRequest instance.
            existing: The existing investigation type from API.
            investigation_type: The desired investigation type parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        name = investigation_type.get("name", "")
        display.v(f"splunk_investigation_type: updating investigation type: {name}")

        # Map existing to module format for before state
        before = map_investigation_type_from_api(existing)

        # Build desired state from params (use existing values as defaults)
        desired = {
            "name": name,
            "description": investigation_type.get("description", before.get("description", "")),
            "response_plan_ids": investigation_type.get(
                "response_plan_ids",
                before.get("response_plan_ids", []),
            ),
        }

        # Normalize response_plan_ids for comparison (None -> [])
        before_ids = sorted(before.get("response_plan_ids") or [])
        desired_ids = sorted(desired.get("response_plan_ids") or [])

        # Check if there are any differences
        description_changed = before.get("description", "") != desired.get("description", "")
        ids_changed = before_ids != desired_ids

        if not description_changed and not ids_changed:
            display.v("splunk_investigation_type: no changes needed")
            return {"before": before, "after": before}, False

        if self._task.check_mode:
            display.v("splunk_investigation_type: check mode - would update investigation type")
            return {"before": before, "after": desired}, True

        # PUT to update
        update_payload = map_investigation_type_to_api_update(desired)
        after = self._put_investigation_type(conn_request, name, update_payload)

        display.v("splunk_investigation_type: updated investigation type successfully")
        return {"before": before, "after": after}, True

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_investigation_type: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_investigation_type: argument validation failed: "
                f"{self._result.get('msg')}",
            )
            return self._result

        # Initialize result structure
        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        # Extract parameters
        name = self._task.args.get("name")
        investigation_type = self._build_investigation_type_params()

        display.vv(f"splunk_investigation_type: name: {name}")
        display.vvv(
            f"splunk_investigation_type: investigation_type parameters: {investigation_type}",
        )

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
            not_rest_data_keys=["api_namespace", "api_user", "api_app"],
        )

        # Lookup existing investigation type by name
        existing = self.get_investigation_type_by_name(conn_request, name)

        # Create or update based on existence
        if existing:
            # Update existing investigation type
            result, changed = self.update_investigation_type(
                conn_request,
                existing,
                investigation_type,
            )
            self._result[self.module_name] = result
            self._result["changed"] = changed
            self._set_result_message("updated", changed)
        else:
            # Create new investigation type
            result, changed = self.create_investigation_type(conn_request, investigation_type)
            self._result[self.module_name] = result
            self._result["changed"] = changed
            self._set_result_message("created", changed)

        display.v(f"splunk_investigation_type: completed with changed={self._result['changed']}")
        return self._result
