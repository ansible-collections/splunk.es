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
The action module for splunk_investigation
"""

from typing import Any, Optional

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils

from ansible_collections.splunk.es.plugins.module_utils.investigation import (
    build_investigation_api_path,
    map_investigation_from_api,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    check_argspec,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    DISPOSITION_TO_API,
    STATUS_TO_API,
)
from ansible_collections.splunk.es.plugins.modules.splunk_investigation import DOCUMENTATION


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for managing Splunk ES investigations."""

    # Fields that can be updated via the main update endpoint (name cannot be updated)
    UPDATABLE_FIELDS = [
        "description",
        "status",
        "disposition",
        "owner",
        "urgency",
        "sensitivity",
        "investigation_type",
    ]

    # finding_ids requires a separate API endpoint
    FINDING_IDS_FIELD = "finding_ids"

    # Sensitivity mapping: module value (lowercase) -> API value (capitalized)
    SENSITIVITY_TO_API = {
        "white": "White",
        "green": "Green",
        "amber": "Amber",
        "red": "Red",
        "unassigned": "Unassigned",
    }

    @staticmethod
    def build_update_path(
        ref_id: str,
        namespace: str = DEFAULT_API_NAMESPACE,
        user: str = DEFAULT_API_USER,
        app: str = DEFAULT_API_APP,
    ) -> str:
        """Build the investigations update API path.

        Args:
            ref_id: The investigation reference ID.
            namespace: The namespace portion of the path. Defaults to 'servicesNS'.
            user: The user portion of the path. Defaults to 'nobody'.
            app: The app portion of the path. Defaults to 'missioncontrol'.

        Returns:
            The investigations update API path with ref_id.
        """
        return f"{build_investigation_api_path(namespace, user, app)}/{ref_id}"

    @classmethod
    def build_findings_path(
        cls,
        ref_id: str,
        namespace: str = DEFAULT_API_NAMESPACE,
        user: str = DEFAULT_API_USER,
        app: str = DEFAULT_API_APP,
    ) -> str:
        """Build the API path for adding findings to an investigation.

        Args:
            ref_id: The investigation reference ID.
            namespace: The namespace portion of the path. Defaults to 'servicesNS'.
            user: The user portion of the path. Defaults to 'nobody'.
            app: The app portion of the path. Defaults to 'missioncontrol'.

        Returns:
            The API path for adding findings to the investigation.
        """
        return f"{cls.build_update_path(ref_id, namespace, user, app)}/findings"

    @classmethod
    def map_to_api(cls, investigation: dict[str, Any]) -> dict[str, Any]:
        """Convert module params to API payload format.

        Args:
            investigation: The investigation parameters dictionary.

        Returns:
            Dictionary formatted for the Splunk investigations API.
        """
        res = investigation.copy()

        # Handle status conversion to API numeric value
        if "status" in res and res["status"]:
            res["status"] = STATUS_TO_API.get(res["status"], res["status"])

        # Handle disposition conversion to API format
        if "disposition" in res and res["disposition"]:
            res["disposition"] = DISPOSITION_TO_API.get(
                res["disposition"].lower(),
                res["disposition"],
            )

        # Handle sensitivity conversion to API format (capitalized)
        if "sensitivity" in res and res["sensitivity"]:
            res["sensitivity"] = cls.SENSITIVITY_TO_API.get(
                res["sensitivity"].lower(),
                res["sensitivity"],
            )

        return res

    @classmethod
    def map_update_to_api(cls, investigation: dict[str, Any]) -> dict[str, Any]:
        """Convert module params to API payload format for updating investigations.

        Only includes fields that are allowed to be updated.

        Args:
            investigation: The investigation parameters dictionary.

        Returns:
            Dictionary formatted for the Splunk investigations update API.
        """
        res = {}

        for field in cls.UPDATABLE_FIELDS:
            if field in investigation and investigation[field] is not None:
                value = investigation[field]

                # Handle status conversion
                if field == "status":
                    value = STATUS_TO_API.get(value, value)

                # Handle disposition conversion
                if field == "disposition":
                    value = DISPOSITION_TO_API.get(value.lower(), value)

                # Handle sensitivity conversion
                if field == "sensitivity":
                    value = cls.SENSITIVITY_TO_API.get(value.lower(), value)

                res[field] = value

        return res

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.module_name = "investigation"
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
        """Build the investigations API path from configured components.

        Returns:
            The complete investigations API path.
        """
        return build_investigation_api_path(self.api_namespace, self.api_user, self.api_app)

    def _configure_api(self) -> None:
        """Configure API path components from task arguments."""
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)
        self.api_object = self._build_api_path()
        display.vv(f"splunk_investigation: using API path: {self.api_object}")

    def _build_investigation_params(self) -> dict[str, Any]:
        """Build investigation dictionary from task arguments.

        Returns:
            Dictionary containing investigation parameters from task args.
        """
        investigation = {}
        name = self._task.args.get("name")
        if name:
            investigation["name"] = name

        param_keys = [
            "description",
            "status",
            "disposition",
            "owner",
            "urgency",
            "sensitivity",
            "finding_ids",
            "investigation_type",
        ]
        for key in param_keys:
            value = self._task.args.get(key)
            if value is not None:
                investigation[key] = value

        return investigation

    def _validate_create_params(self, investigation: dict[str, Any]) -> str:
        """Validate required parameters for creating a new investigation.

        Args:
            investigation: The investigation parameters dictionary.

        Returns:
            Error message if validation fails, empty string if valid.
        """
        if "name" not in investigation:
            return "Missing required parameter: name"

        return ""

    def _set_result_message(self, changed: bool) -> None:
        """Set the appropriate result message based on check mode and changed status.

        Args:
            changed: Whether the operation resulted in changes.
        """
        if self._task.check_mode:
            self._result["msg"] = (
                "Check mode: would create/update investigation"
                if changed
                else "Check mode: no changes required"
            )
        else:
            self._result["msg"] = (
                "Investigation created/updated successfully" if changed else "No changes required"
            )

    def get_investigation_by_id(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
    ) -> dict[str, Any]:
        """Get an existing investigation by its reference ID.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID (investigation ID) to search for.

        Returns:
            The existing investigation if found, empty dict otherwise.
        """
        display.vv(f"splunk_investigation: getting investigation by ref_id: {ref_id}")

        # Use the ids query parameter to filter by investigation ID
        query_params = {"ids": ref_id}
        response = conn_request.get_by_path(self.api_object, query_params=query_params)

        search_result = {}

        # API returns a list, get the first matching investigation
        if response and isinstance(response, list) and len(response) > 0:
            display.vvv(f"splunk_investigation: raw API response: {response}")
            search_result = map_investigation_from_api(response[0])
            search_result["investigation_ref_id"] = ref_id
            display.vv(f"splunk_investigation: found existing investigation: {search_result}")
        else:
            display.vv(f"splunk_investigation: no investigation found with ref_id: {ref_id}")

        return search_result

    def _post_investigation(
        self,
        conn_request: SplunkRequest,
        investigation: dict[str, Any],
    ) -> dict[str, Any]:
        """Send investigation payload to API for creating a new investigation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation: The investigation parameters.

        Returns:
            Parsed investigation from API response.
        """
        payload = self.map_to_api(investigation)

        display.vvv(f"splunk_investigation: posting to {self.api_object}")
        display.vvv(f"splunk_investigation: payload: {payload}")
        api_response = conn_request.create_update(self.api_object, data=payload, json_payload=True)

        after = {}
        if api_response:
            display.vvv(f"splunk_investigation: API response: {api_response}")
            after = map_investigation_from_api(api_response)

        return after

    def _post_update(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        investigation: dict[str, Any],
    ) -> dict[str, Any]:
        """Send investigation payload to API and return parsed response.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the investigation to update.
            investigation: The investigation parameters to update.

        Returns:
            The updated investigation parameters.
        """
        # Build the update API path
        update_url = self.build_update_path(
            ref_id,
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

        # Map to update API payload format
        payload = self.map_update_to_api(investigation)

        display.vvv(f"splunk_investigation: posting update to {update_url}")
        display.vvv(f"splunk_investigation: update payload: {payload}")

        api_response = conn_request.create_update(
            update_url,
            data=payload,
            json_payload=True,
        )

        display.vvv(f"splunk_investigation: update API response: {api_response}")

        # Return the expected state after update
        return investigation

    def _add_findings_to_investigation(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        finding_ids: list[str],
    ) -> None:
        """Add findings to an existing investigation.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the investigation.
            finding_ids: List of finding IDs to add to the investigation.
        """
        findings_url = self.build_findings_path(
            ref_id,
            self.api_namespace,
            self.api_user,
            self.api_app,
        )

        # Send finding_ids as JSON body payload
        payload = {
            "finding_ids": finding_ids,
        }

        display.vvv(f"splunk_investigation: adding findings to {findings_url}")
        display.vvv(f"splunk_investigation: payload: {payload}")

        api_response = conn_request.create_update(
            findings_url,
            data=payload,
            json_payload=True,
        )

        display.vvv(f"splunk_investigation: add findings API response: {api_response}")

    def create_investigation(
        self,
        conn_request: SplunkRequest,
        investigation: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Create a new investigation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation: The investigation parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        name = investigation.get("name", "")
        display.v(f"splunk_investigation: creating new investigation with name: {name}")

        if self._task.check_mode:
            display.v("splunk_investigation: check mode - would create investigation")
            return {"before": None, "after": investigation}, True

        want_conf = utils.remove_empties(investigation)
        api_response = self._post_investigation(conn_request, want_conf)

        # API only returns the GUID on create, so merge input params with response
        # Input params provide the expected state, API response provides the ref_id
        after = want_conf.copy()
        after.update(api_response)

        display.v("splunk_investigation: created investigation successfully")
        return {"before": None, "after": after}, True

    def _filter_updatable_fields(
        self,
        investigation: dict[str, Any],
    ) -> tuple[dict[str, Any], Optional[list[str]]]:
        """Filter investigation params to only updatable fields.

        Args:
            investigation: The investigation parameters dictionary.

        Returns:
            Tuple of (filtered_fields, finding_ids).
        """
        # Extract finding_ids (handled separately via different API)
        finding_ids = investigation.pop(self.FINDING_IDS_FIELD, None)
        if finding_ids:
            display.vv(f"splunk_investigation: will add findings: {finding_ids}")

        # Remove name field (cannot be updated)
        if "name" in investigation:
            display.vv("splunk_investigation: ignoring 'name' field - cannot be updated")
            investigation = {k: v for k, v in investigation.items() if k != "name"}

        # Filter to only updatable fields
        non_updatable = [k for k in investigation if k not in self.UPDATABLE_FIELDS]
        if non_updatable:
            display.vv(f"splunk_investigation: ignoring non-updatable fields: {non_updatable}")
            investigation = {k: v for k, v in investigation.items() if k in self.UPDATABLE_FIELDS}

        return investigation, finding_ids

    def _process_field_updates(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        investigation: dict[str, Any],
        have_conf: dict[str, Any],
    ) -> tuple[bool, dict[str, Any]]:
        """Process regular field updates.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The investigation reference ID.
            investigation: The filtered investigation parameters.
            have_conf: The existing investigation configuration.

        Returns:
            Tuple of (changed, updated_fields).
        """
        want_conf = utils.remove_empties(investigation)
        have_updatable = {k: have_conf.get(k) for k in self.UPDATABLE_FIELDS if k in have_conf}
        diff = utils.dict_diff(have_updatable, want_conf)

        if not diff:
            return False, {}

        display.vv(f"splunk_investigation: field changes detected: {diff}")

        if not self._task.check_mode:
            self._post_update(conn_request, ref_id, want_conf)

        return True, want_conf

    def _process_findings_updates(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        finding_ids: list[str],
        existing_findings: list[str],
    ) -> tuple[bool, list[str]]:
        """Process finding_ids updates.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The investigation reference ID.
            finding_ids: The desired finding IDs to add.
            existing_findings: The existing finding IDs.

        Returns:
            Tuple of (changed, final_findings_list).
        """
        existing_set = set(existing_findings)
        new_findings = [fid for fid in finding_ids if fid not in existing_set]

        if not new_findings:
            display.vv("splunk_investigation: all findings already exist, skipping")
            return False, existing_findings

        skipped = [fid for fid in finding_ids if fid in existing_set]
        display.vv(f"splunk_investigation: adding new findings: {new_findings}")
        if skipped:
            display.vv(f"splunk_investigation: skipping existing findings: {skipped}")

        if not self._task.check_mode:
            self._add_findings_to_investigation(conn_request, ref_id, new_findings)

        return True, existing_findings + new_findings

    def update_investigation(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        investigation: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Update an existing investigation by reference ID.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the investigation to update.
            investigation: The investigation parameters.

        Returns:
            Tuple of (result_dict, changed).
        """
        display.v(f"splunk_investigation: updating investigation with ref_id: {ref_id}")

        # Filter to updatable fields and extract finding_ids
        fields, finding_ids = self._filter_updatable_fields(investigation)

        if not fields and not finding_ids:
            display.v("splunk_investigation: no updatable fields provided")
            return {
                "before": None,
                "after": None,
                "error": "No updatable fields provided. Name cannot be updated.",
            }, False

        # Get existing investigation
        have_conf = self.get_investigation_by_id(conn_request, ref_id)
        if not have_conf:
            display.v(f"splunk_investigation: investigation with ref_id {ref_id} not found")
            return {
                "before": None,
                "after": None,
                "error": f"Investigation with ref_id '{ref_id}' not found",
            }, False

        display.vv(f"splunk_investigation: existing investigation found: {have_conf}")

        changed = False
        after_conf = have_conf.copy()

        # Process field updates
        if fields:
            field_changed, updated = self._process_field_updates(
                conn_request,
                ref_id,
                fields,
                have_conf,
            )
            if field_changed:
                changed = True
                after_conf.update(updated)

        # Process findings updates
        if finding_ids:
            existing = have_conf.get(self.FINDING_IDS_FIELD, []) or []
            findings_changed, final_findings = self._process_findings_updates(
                conn_request,
                ref_id,
                finding_ids,
                existing,
            )
            if findings_changed:
                changed = True
            after_conf[self.FINDING_IDS_FIELD] = final_findings

        # Return result
        if changed:
            action = "would update" if self._task.check_mode else "updated"
            display.v(f"splunk_investigation: {action} investigation successfully")
            return {"before": have_conf, "after": after_conf}, True

        display.v("splunk_investigation: no changes needed")
        return {"before": have_conf, "after": have_conf}, False

    def _handle_update(
        self,
        conn_request: SplunkRequest,
        ref_id: str,
        investigation: dict[str, Any],
    ) -> bool:
        """Handle update operation for an existing investigation.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID of the investigation to update.
            investigation: The investigation parameters.

        Returns:
            True if operation completed successfully, False if error occurred.
        """
        display.v("splunk_investigation: ref_id provided, will update existing investigation")
        investigation_result, changed = self.update_investigation(
            conn_request,
            ref_id,
            investigation,
        )

        if "error" in investigation_result:
            self._result["failed"] = True
            self._result["msg"] = investigation_result["error"]
            return False

        self._result[self.module_name] = investigation_result
        self._result["changed"] = changed
        return True

    def _handle_create(self, conn_request: SplunkRequest, investigation: dict[str, Any]) -> bool:
        """Handle create operation for a new investigation.

        Args:
            conn_request: The SplunkRequest instance.
            investigation: The investigation parameters.

        Returns:
            True if operation completed successfully, False if validation failed.
        """
        display.v("splunk_investigation: no ref_id provided, will create new investigation")

        error_msg = self._validate_create_params(investigation)
        if error_msg:
            self._result["failed"] = True
            self._result["msg"] = error_msg
            display.v(f"splunk_investigation: {error_msg}")
            return False

        investigation_result, changed = self.create_investigation(conn_request, investigation)
        self._result[self.module_name] = investigation_result
        self._result["changed"] = changed
        return True

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_investigation: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_investigation: argument validation failed: {self._result.get('msg')}",
            )
            return self._result

        # Initialize result structure
        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        ref_id = self._task.args.get("investigation_ref_id")
        investigation = self._build_investigation_params()

        display.vv(f"splunk_investigation: investigation parameters: {investigation}")
        display.vv(f"splunk_investigation: investigation_ref_id: {ref_id}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=["investigation_ref_id", "api_namespace", "api_user", "api_app"],
        )

        if ref_id:
            if not self._handle_update(conn_request, ref_id, investigation):
                return self._result
        else:
            if not self._handle_create(conn_request, investigation):
                return self._result

        self._set_result_message(self._result["changed"])
        display.v(f"splunk_investigation: module completed with changed={self._result['changed']}")
        return self._result
