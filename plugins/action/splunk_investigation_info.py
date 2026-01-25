# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The action plugin file for splunk_investigation_info
"""

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

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
)
from ansible_collections.splunk.es.plugins.modules.splunk_investigation_info import (
    DOCUMENTATION,
)


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for querying Splunk ES investigations."""

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
        """Build the investigations API path from configured components.

        Returns:
            The complete investigations API path.
        """
        return build_investigation_api_path(self.api_namespace, self.api_user, self.api_app)

    def _build_query_params(self) -> dict[str, Any] | None:
        """Build query params dict with create_time_min/create_time_max/limit if provided.

        Returns:
            Dict with query params if any are set, None otherwise.
        """
        query_params: dict[str, Any] = {}
        create_time_min = self._task.args.get("create_time_min")
        create_time_max = self._task.args.get("create_time_max")
        limit = self._task.args.get("limit")

        if create_time_min:
            query_params["create_time_min"] = create_time_min
        if create_time_max:
            query_params["create_time_max"] = create_time_max
        if limit:
            query_params["limit"] = limit

        return query_params if query_params else None

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
        display.vv(f"splunk_investigation_info: getting investigation by ref_id: {ref_id}")

        # Use the ids query parameter to filter by investigation ID
        query_params = {"ids": ref_id}

        # Add time/limit filters if provided
        extra_params = self._build_query_params()
        if extra_params:
            query_params.update(extra_params)

        response = conn_request.get_by_path(self.api_object, query_params=query_params)

        search_result = {}

        # API returns a list, get the first matching investigation
        if response and isinstance(response, list) and len(response) > 0:
            display.vvv(f"splunk_investigation_info: raw API response: {response}")
            search_result = map_investigation_from_api(response[0])
            display.vv(f"splunk_investigation_info: found investigation: {search_result}")
        else:
            display.vv(f"splunk_investigation_info: no investigation found with ref_id: {ref_id}")

        return search_result

    def get_all_investigations(self, conn_request: SplunkRequest) -> list[dict[str, Any]]:
        """Get all investigations from the API.

        Args:
            conn_request: The SplunkRequest instance.

        Returns:
            List of all investigations.
        """
        display.vv("splunk_investigation_info: fetching all investigations")

        query_params = self._build_query_params()
        display.vv(f"splunk_investigation_info: query_params={query_params}")

        response = conn_request.get_by_path(self.api_object, query_params=query_params)

        investigations = []
        if response:
            display.vvv(f"splunk_investigation_info: raw API response type: {type(response)}")

            # API returns a list of investigations directly
            if isinstance(response, list):
                for investigation in response:
                    if investigation:
                        mapped = map_investigation_from_api(investigation)
                        if mapped:
                            investigations.append(mapped)

            display.vv(f"splunk_investigation_info: found {len(investigations)} investigations")

        return investigations

    def filter_investigations_by_name(
        self,
        investigations: list[dict[str, Any]],
        name: str,
    ) -> list[dict[str, Any]]:
        """Filter investigations by exact name match.

        Args:
            investigations: List of investigations to filter.
            name: The name to match.

        Returns:
            Filtered list of investigations.
        """
        display.vv(f"splunk_investigation_info: filtering investigations by name: {name}")

        filtered = [inv for inv in investigations if inv.get("name") == name]

        display.vv(
            f"splunk_investigation_info: found {len(filtered)} investigations with matching name",
        )
        return filtered

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_investigation_info: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(
                f"splunk_investigation_info: argument validation failed: {self._result.get('msg')}",
            )
            return self._result

        # Get API path configuration from task args
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP)

        # Build the API path
        self.api_object = self._build_api_path()
        display.vv(f"splunk_investigation_info: using API path: {self.api_object}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "investigation_ref_id",
                "name",
                "create_time_min",
                "create_time_max",
                "limit",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        # Get query parameters
        ref_id = self._task.args.get("investigation_ref_id")
        name = self._task.args.get("name")

        try:
            if ref_id:
                # Query specific investigation by ref_id
                display.v(f"splunk_investigation_info: querying by ref_id: {ref_id}")
                investigation = self.get_investigation_by_id(conn_request, ref_id)
                # Return as list for consistency
                self._result["investigations"] = [investigation] if investigation else []

            elif name:
                # Query all investigations and filter by name
                display.v(f"splunk_investigation_info: querying by name: {name}")
                all_investigations = self.get_all_investigations(conn_request)
                self._result["investigations"] = self.filter_investigations_by_name(
                    all_investigations,
                    name,
                )

            else:
                # Return all investigations
                display.v("splunk_investigation_info: querying all investigations")
                self._result["investigations"] = self.get_all_investigations(conn_request)

            self._result["changed"] = False
            display.v(
                f"splunk_investigation_info: returning {len(self._result['investigations'])} "
                "investigation(s)",
            )

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                # Handle 404 gracefully - return empty list
                self._result["changed"] = False
                self._result["investigations"] = []
                display.v("splunk_investigation_info: no investigations found (404)")
            else:
                self.fail_json(
                    msg=f"Failed to query investigation(s): {error_msg}",
                )

        return self._result
