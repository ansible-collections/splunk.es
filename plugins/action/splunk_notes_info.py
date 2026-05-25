# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The action plugin file for splunk_notes_info
"""

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

from ansible_collections.splunk.es.plugins.module_utils.finding import extract_notable_time
from ansible_collections.splunk.es.plugins.module_utils.notes import (
    TARGET_FINDING,
    TARGET_RESPONSE_PLAN_TASK,
    build_notes_api_path,
    build_task_note_api_path,
    build_task_notes_api_path,
    map_note_from_api,
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
from ansible_collections.splunk.es.plugins.modules.splunk_notes_info import DOCUMENTATION

# Initialize display for debug output
display = Display()

# Default limit for notes query
DEFAULT_NOTES_LIMIT = 100


class ActionModule(ActionBase):
    """Action module for querying Splunk ES notes."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result: dict[str, Any] = {}
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

    def _build_task_note_path(self, note_id: str) -> str:
        """Build the API path for a specific task note.

        Only used for response_plan_task target type which supports direct note lookup.

        Args:
            note_id: The note ID.

        Returns:
            The API path for the specific task note.
        """
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

    def _get_query_params(self, target_type: str) -> dict[str, Any]:
        """Get query parameters for API requests.

        For findings, extracts notable_time from finding_ref_id.
        Also includes limit parameter.

        Args:
            target_type: The target type.

        Returns:
            Query parameters dict.
        """
        query_params: dict[str, Any] = {}

        # Add notable_time for findings
        if target_type == TARGET_FINDING:
            finding_ref_id = self._task.args.get("finding_ref_id")
            notable_time = extract_notable_time(finding_ref_id)
            if notable_time:
                display.vvv(
                    f"splunk_notes_info: using notable_time={notable_time} from finding_ref_id",
                )
                query_params["notable_time"] = notable_time

        # Add limit parameter
        limit = self._task.args.get("limit", DEFAULT_NOTES_LIMIT)
        query_params["limit"] = limit

        # Sort by newest first
        query_params["sort"] = "create_time:-1"

        return query_params

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
            List of notes mapped to module format, or empty list if none found.
        """
        api_path = self._build_notes_path(target_type)
        query_params = self._get_query_params(target_type)

        display.vv(f"splunk_notes_info: GET {api_path}")
        display.vv(f"splunk_notes_info: query_params={query_params}")

        response = conn_request.get_by_path(api_path, query_params=query_params)

        display.vvv(f"splunk_notes_info: raw response: {response}")

        if not response:
            display.vv("splunk_notes_info: no notes found (empty response)")
            return []

        # Extract notes from response - API returns {"items": [...]}
        raw_notes = response.get("items", [])

        # Map notes to module format
        notes = [map_note_from_api(note) for note in raw_notes if note]

        display.vv(f"splunk_notes_info: found {len(notes)} notes")
        return notes

    def _get_note_by_id_filtered(
        self,
        conn_request: SplunkRequest,
        target_type: str,
        note_id: str,
    ) -> dict[str, Any]:
        """Get a note by ID by fetching all notes and filtering.

        Used for finding and investigation target types where the API
        doesn't support direct note lookup.

        Args:
            conn_request: The SplunkRequest instance.
            target_type: The target type.
            note_id: The note ID.

        Returns:
            The note if found, empty dict otherwise.
        """
        display.vv(f"splunk_notes_info: getting note by id (filtered): {note_id}")

        all_notes = self._get_all_notes(conn_request, target_type)

        for note in all_notes:
            if note.get("note_id") == note_id:
                display.vv(f"splunk_notes_info: found note: {note}")
                return note

        display.vv(f"splunk_notes_info: no note found with id: {note_id}")
        return {}

    def _get_task_note_direct(
        self,
        conn_request: SplunkRequest,
        note_id: str,
    ) -> dict[str, Any]:
        """Get a task note directly by API path.

        Used for response_plan_task target type which supports direct note lookup.

        Args:
            conn_request: The SplunkRequest instance.
            note_id: The note ID.

        Returns:
            The note if found, empty dict otherwise.
        """
        api_path = self._build_task_note_path(note_id)

        display.vv(f"splunk_notes_info: GET {api_path}")

        response = conn_request.get_by_path(api_path)

        display.vvv(f"splunk_notes_info: raw response: {response}")

        if response:
            return map_note_from_api(response)

        display.vv(f"splunk_notes_info: no note found with id: {note_id}")
        return {}

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_notes_info: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_notes_info: argument validation failed: {self._result.get('msg')}",
            )
            return self._result

        self._configure_api()

        # Extract parameters
        target_type = self._task.args.get("target_type")
        note_id = self._task.args.get("note_id")

        display.vv(f"splunk_notes_info: target_type: {target_type}")
        display.vv(f"splunk_notes_info: note_id: {note_id}")

        # Validate target-specific parameters
        error = validate_target_params(target_type, self._task.args)
        if error:
            self._result["failed"] = True
            self._result["msg"] = error
            display.v(f"splunk_notes_info: {error}")
            return self._result

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "target_type",
                "note_id",
                "finding_ref_id",
                "investigation_ref_id",
                "response_plan_id",
                "phase_id",
                "task_id",
                "limit",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        try:
            if note_id:
                # Query specific note by ID
                display.v(f"splunk_notes_info: querying note by id: {note_id}")

                if target_type == TARGET_RESPONSE_PLAN_TASK:
                    # Response plan tasks support direct note lookup
                    note = self._get_task_note_direct(conn_request, note_id)
                else:
                    # Finding/investigation require fetching all and filtering
                    note = self._get_note_by_id_filtered(conn_request, target_type, note_id)

                # Return as list for consistency
                self._result["notes"] = [note] if note else []

            else:
                # Return all notes
                display.v("splunk_notes_info: querying all notes")
                self._result["notes"] = self._get_all_notes(conn_request, target_type)

            self._result["changed"] = False
            display.v(f"splunk_notes_info: returning {len(self._result['notes'])} note(s)")

        except Exception as e:
            error_msg = str(e)
            # Handle resource not found gracefully - return empty list
            # Splunk may return 404, or 500 with MC_0050 for non-existent resources
            is_not_found = (
                "404" in error_msg or "not found" in error_msg.lower() or "MC_0050" in error_msg
            )
            if is_not_found:
                self._result["changed"] = False
                self._result["notes"] = []
                display.v("splunk_notes_info: no notes found (resource not found)")
            else:
                self.fail_json(msg=f"Failed to query note(s): {error_msg}")

        return self._result
