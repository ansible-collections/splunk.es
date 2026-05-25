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
The action module for splunk_notes
"""

from typing import Any, Optional

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

from ansible_collections.splunk.es.plugins.module_utils.finding import extract_notable_time
from ansible_collections.splunk.es.plugins.module_utils.notes import (
    TARGET_FINDING,
    TARGET_RESPONSE_PLAN_TASK,
    build_note_api_path,
    build_notes_api_path,
    build_task_note_api_path,
    build_task_notes_api_path,
    map_note_from_api,
    map_note_to_api,
    validate_target_params,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    check_argspec,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    get_api_config_from_args,
)
from ansible_collections.splunk.es.plugins.modules.splunk_notes import DOCUMENTATION

# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for managing Splunk ES notes."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result: dict[str, Any] = {}
        self.module_name = "note"
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
        self.api_namespace, self.api_user, self.api_app = get_api_config_from_args(
            self._task.args,
        )

    def _validate_state_params(self, state: str, note_id: Optional[str]) -> Optional[str]:
        """Validate parameters based on state.

        Args:
            state: The desired state (present or absent).
            note_id: The note ID (if provided).

        Returns:
            Error message if validation fails, None if valid.
        """
        if state == "absent":
            if not note_id:
                return "Missing required parameter 'note_id' for state 'absent'"
        elif state == "present":
            content = self._task.args.get("content")
            if not content:
                return "Missing required parameter 'content' for state 'present'"

        return None

    def _build_note_params(self) -> dict[str, Any]:
        """Build note dictionary from task arguments.

        Returns:
            Dictionary containing note parameters from task args.
        """
        note: dict[str, Any] = {}

        content = self._task.args.get("content")
        if content is not None:
            note["content"] = content

        return note

    def _build_notes_path(self, target_type: str) -> str:
        """Build the notes API path based on target type.

        Args:
            target_type: The target type.

        Returns:
            The API path for notes.
        """
        if target_type == TARGET_RESPONSE_PLAN_TASK:
            return build_task_notes_api_path(
                investigation_id=self._task.args.get("investigation_ref_id"),
                response_plan_id=self._task.args.get("response_plan_id"),
                phase_id=self._task.args.get("phase_id"),
                task_id=self._task.args.get("task_id"),
                namespace=self.api_namespace,
                user=self.api_user,
                app=self.api_app,
            )

        # For finding or investigation
        if target_type == TARGET_FINDING:
            investigation_id = quote(self._task.args.get("finding_ref_id"), safe="")
        else:
            investigation_id = self._task.args.get("investigation_ref_id")

        return build_notes_api_path(
            investigation_id=investigation_id,
            namespace=self.api_namespace,
            user=self.api_user,
            app=self.api_app,
        )

    def _build_note_path(self, target_type: str, note_id: str) -> str:
        """Build the API path for a specific note.

        Args:
            target_type: The target type.
            note_id: The note ID.

        Returns:
            The API path for the specific note.
        """
        if target_type == TARGET_RESPONSE_PLAN_TASK:
            return build_task_note_api_path(
                investigation_id=self._task.args.get("investigation_ref_id"),
                response_plan_id=self._task.args.get("response_plan_id"),
                phase_id=self._task.args.get("phase_id"),
                task_id=self._task.args.get("task_id"),
                note_id=note_id,
                namespace=self.api_namespace,
                user=self.api_user,
                app=self.api_app,
            )

        # For finding or investigation
        if target_type == TARGET_FINDING:
            investigation_id = quote(self._task.args.get("finding_ref_id"), safe="")
        else:
            investigation_id = self._task.args.get("investigation_ref_id")

        return build_note_api_path(
            investigation_id=investigation_id,
            note_id=note_id,
            namespace=self.api_namespace,
            user=self.api_user,
            app=self.api_app,
        )

    def _get_query_params(self, target_type: str) -> dict[str, str]:
        """Get query parameters for API requests.

        For findings, extracts notable_time from finding_ref_id.

        Args:
            target_type: The target type.

        Returns:
            Query parameters dict (empty if no params needed).
        """
        if target_type == TARGET_FINDING:
            finding_ref_id = self._task.args.get("finding_ref_id")
            notable_time = extract_notable_time(finding_ref_id)
            if notable_time:
                display.vvv(f"splunk_notes: using notable_time={notable_time} from finding_ref_id")
                return {"notable_time": notable_time}
        return {}

    def _get_all_notes(
        self,
        conn_request: SplunkRequest,
        target_type: str,
    ) -> list[dict[str, Any]]:
        """Get all notes for a target.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.

        Returns:
            List of notes, or empty list if none found.
        """
        api_path = self._build_notes_path(target_type)
        query_params = self._get_query_params(target_type)
        # Request maximum notes (100) sorted by newest first
        query_params["limit"] = 100
        query_params["sort"] = "create_time:-1"

        display.vvv(f"splunk_notes: GET {api_path}")
        response = conn_request.get_by_path(api_path, query_params=query_params)

        display.vvv(f"splunk_notes: list notes raw response: {response}")

        if not response:
            display.vv("splunk_notes: no notes found (empty response)")
            return []

        # Extract notes from response
        notes = response.get("items", [])

        if notes:
            display.vvv(f"splunk_notes: found {len(notes)} notes")
        else:
            display.vv("splunk_notes: no notes found in response")

        return notes

    def _get_note_by_id(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: str,
    ) -> dict[str, Any]:
        """Get an existing note by its ID.

        Fetches all notes for the target and filters by note_id,
        API doesn't support GET for a single note.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID.

        Returns:
            The existing note if found, empty dict otherwise.
        """
        display.vv(f"splunk_notes: getting note by id: {note_id}")

        # Fetch all notes and filter by ID
        all_notes = self._get_all_notes(conn_request, target_type)

        for note in all_notes:
            if note.get("id") == note_id:
                display.vvv(f"splunk_notes: found note: {note}")
                return map_note_from_api(note)

        display.vv(f"splunk_notes: no note found with id: {note_id}")
        return {}

    def _create_note(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new note.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note: The note parameters.

        Returns:
            The created note from API response.
        """
        api_path = self._build_notes_path(target_type)
        query_params = self._get_query_params(target_type)
        payload = map_note_to_api(note)

        display.vvv(f"splunk_notes: POST {api_path}")
        display.vvv(f"splunk_notes: payload: {payload}")

        response = conn_request.create_update(
            api_path,
            data=payload,
            query_params=query_params,
            json_payload=True,
        )

        if response:
            display.vvv(f"splunk_notes: create response: {response}")
            return map_note_from_api(response)

        return {}

    def _update_note(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: str,
        note: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing note.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID.
            note: The note parameters.

        Returns:
            The updated note from API response.
        """
        api_path = self._build_note_path(target_type, note_id)
        query_params = self._get_query_params(target_type)
        payload = map_note_to_api(note)

        display.vvv(f"splunk_notes: POST {api_path}")
        display.vvv(f"splunk_notes: payload: {payload}")

        response = conn_request.create_update(
            api_path,
            data=payload,
            query_params=query_params,
            json_payload=True,
        )

        if response:
            display.vvv(f"splunk_notes: update response: {response}")
            return map_note_from_api(response)

        # Return expected state if no response
        result = note.copy()
        result["note_id"] = note_id
        return result

    def _delete_note(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: str,
    ) -> None:
        """Delete a note.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID.
        """
        api_path = self._build_note_path(target_type, note_id)

        display.vvv(f"splunk_notes: DELETE {api_path}")
        conn_request.delete_by_path(api_path)

    def _compare_notes(
        self,
        existing: dict[str, Any],
        desired: dict[str, Any],
    ) -> bool:
        """Compare existing and desired note states.

        Args:
            existing: The existing note state.
            desired: The desired note state.

        Returns:
            True if notes are different, False if same.
        """
        # Compare content
        return existing.get("content") != desired.get("content")

    def _handle_present_create(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note: dict[str, Any],
    ) -> None:
        """Handle creating a new note.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note: The note parameters.
        """
        display.v("splunk_notes: creating new note")

        if self._task.check_mode:
            display.v("splunk_notes: check mode - would create note")
            self._result[self.module_name] = {"before": None, "after": note}
            self._result["changed"] = True
            self._result["msg"] = "Check mode: would create note"
            return

        after = self._create_note(conn_request, target_type, note)

        self._result[self.module_name] = {"before": None, "after": after}
        self._result["changed"] = True
        self._result["msg"] = "Note created successfully"
        display.v("splunk_notes: note created successfully")

    def _handle_present_update(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: str,
        note: dict[str, Any],
    ) -> None:
        """Handle updating an existing note.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID.
            note: The note parameters.
        """
        display.v(f"splunk_notes: updating note with id: {note_id}")

        # Get existing note
        existing = self._get_note_by_id(conn_request, target_type, note_id)

        if not existing:
            self._result["failed"] = True
            self._result["msg"] = f"Note with id '{note_id}' not found"
            return

        # Check if update is needed
        if not self._compare_notes(existing, note):
            display.v("splunk_notes: no changes needed")
            self._result[self.module_name] = {"before": existing, "after": existing}
            self._result["changed"] = False
            self._result["msg"] = "No changes required"
            return

        display.vv("splunk_notes: changes detected, updating note")

        if self._task.check_mode:
            display.v("splunk_notes: check mode - would update note")
            after = existing.copy()
            after.update(note)
            self._result[self.module_name] = {"before": existing, "after": after}
            self._result["changed"] = True
            self._result["msg"] = "Check mode: would update note"
            return

        after = self._update_note(conn_request, target_type, note_id, note)

        # Compare before and after to determine if API actually made changes
        actually_changed = self._compare_notes(existing, after)

        self._result[self.module_name] = {"before": existing, "after": after}
        self._result["changed"] = actually_changed
        if actually_changed:
            self._result["msg"] = "Note updated successfully"
            display.v("splunk_notes: note updated successfully")
        else:
            self._result["msg"] = "No changes required"
            display.v("splunk_notes: no actual changes made by API")

    def _handle_present(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: Optional[str],
        note: dict[str, Any],
    ) -> None:
        """Handle state=present operation.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID (if updating).
            note: The note parameters.
        """
        if note_id:
            self._handle_present_update(conn_request, target_type, note_id, note)
        else:
            self._handle_present_create(conn_request, target_type, note)

    def _handle_absent(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: str,
    ) -> None:
        """Handle state=absent operation.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID.
        """
        display.v(f"splunk_notes: deleting note with id: {note_id}")

        # Get existing note to verify it exists
        existing = self._get_note_by_id(conn_request, target_type, note_id)

        if not existing:
            display.v("splunk_notes: note not found, already absent")
            self._result[self.module_name] = {"before": None, "after": None}
            self._result["changed"] = False
            self._result["msg"] = "Note not found, already absent"
            return

        if self._task.check_mode:
            display.v("splunk_notes: check mode - would delete note")
            self._result[self.module_name] = {"before": existing, "after": None}
            self._result["changed"] = True
            self._result["msg"] = "Check mode: would delete note"
            return

        self._delete_note(conn_request, target_type, note_id)

        self._result[self.module_name] = {"before": existing, "after": None}
        self._result["changed"] = True
        self._result["msg"] = "Note deleted successfully"
        display.v("splunk_notes: note deleted successfully")

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_notes: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(f"splunk_notes: argument validation failed: {self._result.get('msg')}")
            return self._result

        # Initialize result structure
        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        # Extract parameters
        target_type = self._task.args.get("target_type")
        state = self._task.args.get("state", "present")
        note_id = self._task.args.get("note_id")

        display.vv(f"splunk_notes: target_type: {target_type}")
        display.vv(f"splunk_notes: state: {state}")
        display.vv(f"splunk_notes: note_id: {note_id}")

        # Validate target-specific parameters
        error = validate_target_params(target_type, self._task.args)
        if error:
            self._result["failed"] = True
            self._result["msg"] = error
            display.v(f"splunk_notes: {error}")
            return self._result

        # Validate state-specific parameters
        error = self._validate_state_params(state, note_id)
        if error:
            self._result["failed"] = True
            self._result["msg"] = error
            display.v(f"splunk_notes: {error}")
            return self._result

        # Build note parameters
        note = self._build_note_params()
        display.vvv(f"splunk_notes: note parameters: {note}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "target_type",
                "state",
                "note_id",
                "finding_ref_id",
                "investigation_ref_id",
                "response_plan_id",
                "phase_id",
                "task_id",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        # Route based on state
        if state == "absent":
            self._handle_absent(conn_request, target_type, note_id)
        else:
            self._handle_present(conn_request, target_type, note_id, note)

        display.v(f"splunk_notes: module completed with changed={self._result['changed']}")
        return self._result
