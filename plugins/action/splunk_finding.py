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
The action module for splunk_finding
"""

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils

from ansible_collections.splunk.es.plugins.module_utils.finding import (
    FINDING_KEY_TRANSFORM,
    build_finding_api_path,
    extract_notable_time,
    map_finding_from_api,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    check_argspec,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_APP_SECURITY_SUITE,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    DISPOSITION_TO_API,
    STATUS_TO_API,
)
from ansible_collections.splunk.es.plugins.modules.splunk_finding import DOCUMENTATION


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for managing Splunk ES findings."""

    # Key transformation for update API: module param -> API param
    UPDATE_KEY_TRANSFORM = {
        "owner": "assignee",
        "status": "status",
        "urgency": "urgency",
        "disposition": "disposition",
    }

    @staticmethod
    def build_update_api_path(
        ref_id: str,
        namespace: str = DEFAULT_API_NAMESPACE,
        user: str = DEFAULT_API_USER,
    ) -> str:
        """Build the investigations update API path.

        The update API uses a fixed app (missioncontrol).

        Args:
            ref_id: The finding reference ID (e.g., 'uuid@@notable@@time{timestamp}').
            namespace: The namespace portion of the path. Defaults to 'servicesNS'.
            user: The user portion of the path. Defaults to 'nobody'.

        Returns:
            The investigations update API path (without query parameters).
        """
        return f"{namespace}/{user}/{DEFAULT_API_APP}/v1/investigations/{ref_id}"

    @classmethod
    def map_finding_to_api(
        cls,
        finding: dict[str, Any],
        key_transform: dict[str, str] = None,
    ) -> dict[str, Any]:
        """Convert module params to API payload format.

        Args:
            finding: The finding parameters dictionary.
            key_transform: Optional key transformation dict. Defaults to FINDING_KEY_TRANSFORM.

        Returns:
            Dictionary formatted for the Splunk findings API.
        """
        from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
            map_obj_to_params,
        )

        if key_transform is None:
            key_transform = FINDING_KEY_TRANSFORM

        # Use the helper from module_utils
        res = map_obj_to_params(finding.copy(), key_transform)

        # Add default values for API
        res["app"] = DEFAULT_API_APP_SECURITY_SUITE
        res["creator"] = "admin"

        # Handle status conversion
        if "status" in res and res["status"]:
            res["status"] = STATUS_TO_API.get(res["status"], res["status"])

        # Handle disposition conversion
        if "disposition" in res and res["disposition"]:
            res["disposition"] = DISPOSITION_TO_API.get(res["disposition"], res["disposition"])

        # Handle custom fields - flatten them into the payload
        if "fields" in finding and finding["fields"]:
            for field in finding["fields"]:
                if "name" in field and "value" in field:
                    res[field["name"]] = field["value"]

        return res

    @classmethod
    def map_update_to_api(cls, finding: dict[str, Any]) -> dict[str, Any]:
        """Convert module params to API payload format for updating findings.

        Args:
            finding: The finding parameters dictionary.

        Returns:
            Dictionary formatted for the Splunk investigations update API.
        """
        res = {}

        for module_key, api_key in cls.UPDATE_KEY_TRANSFORM.items():
            if module_key in finding and finding[module_key] is not None:
                value = finding[module_key]

                # Handle status conversion
                if module_key == "status":
                    value = STATUS_TO_API.get(value, value)

                # Handle disposition conversion
                if module_key == "disposition":
                    value = DISPOSITION_TO_API.get(value, value)

                res[api_key] = value

        return res

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.module_name = "finding"
        self.key_transform = FINDING_KEY_TRANSFORM
        self.api_namespace = DEFAULT_API_NAMESPACE
        self.api_user = DEFAULT_API_USER
        self.api_app = DEFAULT_API_APP_SECURITY_SUITE
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
        """Build the findings API path from configured components.

        Returns:
            The complete findings API path.
        """
        return build_finding_api_path(self.api_namespace, self.api_user, self.api_app)

    def _configure_api(self) -> None:
        """Configure API path components from task arguments."""
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP_SECURITY_SUITE)
        self.api_object = self._build_api_path()
        display.vv(f"splunk_finding: using API path: {self.api_object}")

    def _build_finding_params(self) -> dict[str, Any]:
        """Build finding dictionary from task arguments.

        Returns:
            Dictionary containing finding parameters from task args.
        """
        finding = {}
        title = self._task.args.get("title")
        if title:
            finding["title"] = title

        param_keys = [
            "description",
            "security_domain",
            "entity",
            "entity_type",
            "finding_score",
            "owner",
            "status",
            "urgency",
            "disposition",
            "fields",
        ]
        for key in param_keys:
            if value := self._task.args.get(key):
                finding[key] = value

        return finding

    def _validate_create_params(self, finding: dict[str, Any]) -> str:
        """Validate required parameters for creating a new finding.

        Args:
            finding: The finding parameters dictionary.

        Returns:
            Error message if validation fails, empty string if valid.
        """
        if "title" not in finding:
            return "Missing required parameter: title"

        required_fields = [
            "description",
            "security_domain",
            "entity",
            "entity_type",
            "finding_score",
        ]
        missing = [f for f in required_fields if f not in finding]
        if missing:
            return f"Missing required parameters for creating finding: {', '.join(missing)}"

        return ""

    def _set_result_message(self, changed: bool) -> None:
        """Set the appropriate result message based on check mode and changed status.

        Args:
            changed: Whether the operation resulted in changes.
        """
        if self._task.check_mode:
            self._result["msg"] = (
                "Check mode: would create/update finding"
                if changed
                else "Check mode: no changes required"
            )
        else:
            self._result["msg"] = (
                "Finding created/updated successfully" if changed else "No changes required"
            )

    def get_finding_by_id(self, conn_request: SplunkRequest, ref_id: str) -> dict[str, Any]:
        """Get an existing finding by its reference ID.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID (finding ID) to search for.

        Returns:
            The existing finding if found, empty dict otherwise.
        """
        display.vv(f"splunk_finding: getting finding by ref_id: {ref_id}")

        # Extract timestamp from ref_id to set earliest time filter
        # This allows querying findings older than 24 hours
        query_params = {}
        notable_time = extract_notable_time(ref_id)
        if notable_time:
            query_params["earliest"] = notable_time
            display.vvv(f"splunk_finding: using earliest={notable_time} from ref_id")

        query_dict = conn_request.get_by_path(
            f"{self.api_object}/{quote(ref_id)}",
            query_params=query_params if query_params else None,
        )

        search_result = {}

        if query_dict:
            display.vvv(f"splunk_finding: raw API response: {query_dict}")
            search_result = map_finding_from_api(query_dict, self.key_transform)
            search_result["ref_id"] = ref_id
            display.vv(f"splunk_finding: found existing finding: {search_result}")
        else:
            display.vv(f"splunk_finding: no finding found with ref_id: {ref_id}")

        return search_result

    def _post_finding(
        self,
        conn_request: SplunkRequest,
        finding: dict[str, Any],
    ) -> dict[str, Any]:
        """Send finding payload to API for creating a new finding.

        Args:
            conn_request: The SplunkRequest instance.
            finding: The finding parameters.

        Returns:
            Parsed finding from API response.
        """
        payload = self.map_finding_to_api(finding, self.key_transform)

        display.vvv(f"splunk_finding: posting to {self.api_object}")
        display.vvv(f"splunk_finding: payload: {payload}")
        api_response = conn_request.create_update(self.api_object, data=payload, json_payload=True)

        after = {}
        if api_response:
            display.vvv(f"splunk_finding: API response: {api_response}")
            after = map_finding_from_api(api_response, self.key_transform)

        return after

    def _post_update(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        finding: dict[str, Any],
    ) -> dict[str, Any]:
        """Send finding payload to API and return parsed response.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the finding to update.
            finding: The finding parameters to update.

        Returns:
            The updated finding parameters.
        """
        # Build the update API path
        update_url = self.build_update_api_path(ref_id, self.api_namespace, self.api_user)

        # Extract notable_time from ref_id for query param
        notable_time = extract_notable_time(ref_id)
        if not notable_time:
            self.fail_json(
                msg=f"Cannot extract notable_time from ref_id '{ref_id}'. "
                "Expected format: uuid@@notable@@time{{timestamp}}",
            )

        query_params = {"notable_time": notable_time}

        # Map to update API payload format (owner -> assignee, etc.)
        payload = self.map_update_to_api(finding)

        display.vvv(f"splunk_finding: posting update to {update_url}")
        display.vvv(f"splunk_finding: query_params: {query_params}")
        display.vvv(f"splunk_finding: update payload: {payload}")

        api_response = conn_request.create_update(
            update_url,
            data=payload,
            query_params=query_params,
            json_payload=True,
        )

        display.vvv(f"splunk_finding: update API response: {api_response}")

        # Return the expected state after update
        # The investigations API may not return full finding data
        return finding

    def create_finding(
        self,
        conn_request: SplunkRequest,
        finding: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Create a new finding.

        Args:
            conn_request: The SplunkRequest instance.
            finding: The finding parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        title = finding.get("title", "")
        display.v(f"splunk_finding: creating new finding with title: {title}")

        if self._task.check_mode:
            display.v("splunk_finding: check mode - would create finding")
            return {"before": None, "after": finding}, True

        want_conf = utils.remove_empties(finding)
        after = self._post_finding(conn_request, want_conf)

        display.v("splunk_finding: created finding successfully")
        return {"before": None, "after": after}, True

    def update_finding(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        finding: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Update an existing finding by reference ID.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the finding to update.
            finding: The finding parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        display.v(f"splunk_finding: updating finding with ref_id: {ref_id}")

        # Validate that only updatable fields are provided
        non_updatable = [k for k in finding if k not in self.UPDATE_KEY_TRANSFORM]
        if non_updatable:
            display.vv(f"splunk_finding: ignoring non-updatable fields: {non_updatable}")
            # Filter to only updatable fields
            finding = {k: v for k, v in finding.items() if k in self.UPDATE_KEY_TRANSFORM}

        if not finding:
            display.v("splunk_finding: no updatable fields provided")
            return {
                "before": None,
                "after": None,
                "error": "No updatable fields provided. Only owner, status, urgency, and disposition can be updated.",
            }, False

        # Get existing finding to verify it exists
        have_conf = self.get_finding_by_id(conn_request, ref_id)

        if not have_conf:
            display.v(f"splunk_finding: finding with ref_id {ref_id} not found")
            return {
                "before": None,
                "after": None,
                "error": f"Finding with ref_id '{ref_id}' not found",
            }, False

        display.vv(f"splunk_finding: existing finding found: {have_conf}")

        # Compare to detect changes (only for updatable fields)
        want_conf = utils.remove_empties(finding)
        have_updatable = {k: have_conf.get(k) for k in self.UPDATE_KEY_TRANSFORM if k in have_conf}
        diff = utils.dict_diff(have_updatable, want_conf)

        if diff:
            display.vv(f"splunk_finding: changes detected: {diff}")

            # Check mode - don't make actual changes
            if self._task.check_mode:
                display.v("splunk_finding: check mode - would update finding")
                after_conf = have_conf.copy()
                after_conf.update(want_conf)
                return {"before": have_conf, "after": after_conf}, True

            # Use the investigations API for updates
            self._post_update(conn_request, ref_id, want_conf)

            # Build expected after state
            after_conf = have_conf.copy()
            after_conf.update(want_conf)

            display.v("splunk_finding: updated finding successfully")
            return {"before": have_conf, "after": after_conf}, True
        else:
            display.v("splunk_finding: no changes needed")
            return {"before": have_conf, "after": have_conf}, False

    def _handle_update(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        finding: dict[str, Any],
    ) -> bool:
        """Handle update operation for an existing finding.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the finding to update.
            finding: The finding parameters.

        Returns:
            True if operation completed successfully, False if error occurred.
        """
        display.v("splunk_finding: ref_id provided, will update existing finding")
        finding_result, changed = self.update_finding(conn_request, ref_id, finding)

        if "error" in finding_result:
            self._result["failed"] = True
            self._result["msg"] = finding_result["error"]
            return False

        self._result[self.module_name] = finding_result
        self._result["changed"] = changed
        return True

    def _handle_create(self, conn_request: SplunkRequest, finding: dict[str, Any]) -> bool:
        """Handle create operation for a new finding.

        Args:
            conn_request: The SplunkRequest instance.
            finding: The finding parameters.

        Returns:
            True if operation completed successfully, False if validation failed.
        """
        display.v("splunk_finding: no ref_id provided, will create new finding")

        error_msg = self._validate_create_params(finding)
        if error_msg:
            self._result["failed"] = True
            self._result["msg"] = error_msg
            display.v(f"splunk_finding: {error_msg}")
            return False

        finding_result, changed = self.create_finding(conn_request, finding)
        self._result[self.module_name] = finding_result
        self._result["changed"] = changed
        return True

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_finding: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(f"splunk_finding: argument validation failed: {self._result.get('msg')}")
            return self._result

        # Initialize result structure
        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        ref_id = self._task.args.get("ref_id")
        finding = self._build_finding_params()

        display.vv(f"splunk_finding: finding parameters: {finding}")
        display.vv(f"splunk_finding: ref_id: {ref_id}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=["ref_id", "api_namespace", "api_user", "api_app"],
        )

        if ref_id:
            if not self._handle_update(conn_request, ref_id, finding):
                return self._result
        else:
            if not self._handle_create(conn_request, finding):
                return self._result

        self._set_result_message(self._result["changed"])
        display.v(f"splunk_finding: module completed with changed={self._result['changed']}")
        return self._result
