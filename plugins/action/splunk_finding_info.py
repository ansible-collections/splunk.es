# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The action plugin file for splunk_finding_info
"""

from typing import Any, Dict, List, Optional

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

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
    DEFAULT_API_APP_SECURITY_SUITE,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
)
from ansible_collections.splunk.es.plugins.modules.splunk_finding_info import (
    DOCUMENTATION,
)


# Initialize display for debug output
display = Display()


class ActionModule(ActionBase):
    """Action module for querying Splunk ES findings."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.key_transform = FINDING_KEY_TRANSFORM
        # API path components - will be set in run() from task args
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

    def _build_query_params(self) -> Optional[Dict[str, Any]]:
        """Build query params dict with earliest/latest/limit if provided.

        Returns:
            Dict with query params if any are set, None otherwise.
        """
        query_params: Dict[str, Any] = {}
        earliest = self._task.args.get("earliest")
        latest = self._task.args.get("latest")
        limit = self._task.args.get("limit")
        if earliest:
            query_params["earliest"] = earliest
        if latest:
            query_params["latest"] = latest
        if limit:
            query_params["limit"] = limit

        return query_params if query_params else None

    def get_finding_by_id(self, conn_request: SplunkRequest, ref_id: str) -> Dict[str, Any]:
        """Get an existing finding by its reference ID.

        The time is extracted from the ref_id itself (format: uuid@@notable@@time{timestamp}).
        User-provided earliest/latest parameters are ignored when querying by ref_id.

        Args:
            conn_request: The SplunkRequest instance.
            ref_id: The reference ID (finding ID) to search for.

        Returns:
            The existing finding if found, empty dict otherwise.
        """
        display.vv(f"splunk_finding_info: getting finding by ref_id: {ref_id}")

        # Extract timestamp from ref_id to set earliest time filter
        query_params = {}
        notable_time = extract_notable_time(ref_id)
        if notable_time:
            query_params["earliest"] = notable_time
            display.vvv(f"splunk_finding_info: using earliest={notable_time} from ref_id")

        query_dict = conn_request.get_by_path(
            f"{self.api_object}/{quote(ref_id)}",
            query_params=query_params if query_params else None,
        )

        if query_dict:
            display.vvv(f"splunk_finding_info: raw API response: {query_dict}")
            result = map_finding_from_api(query_dict, self.key_transform)
            result["ref_id"] = ref_id
            display.vv(f"splunk_finding_info: found finding: {result}")
            return result

        display.vv(f"splunk_finding_info: no finding found with ref_id: {ref_id}")
        return {}

    def get_all_findings(self, conn_request: SplunkRequest) -> List[Dict[str, Any]]:
        """Get all findings from the API.

        Args:
            conn_request: The SplunkRequest instance.

        Returns:
            List of all findings.
        """
        display.vv("splunk_finding_info: fetching all findings")

        query_params = self._build_query_params()
        display.vv(f"splunk_finding_info: query_params={query_params}")

        query_dict = conn_request.get_by_path(self.api_object, query_params=query_params)

        findings = []
        if query_dict:
            display.vvv(f"splunk_finding_info: raw API response type: {type(query_dict)}")

            # v2 findings API returns findings under "items" key
            raw_findings = query_dict.get("items", [])

            for finding in raw_findings:
                if finding:
                    mapped = map_finding_from_api(finding.copy(), self.key_transform)
                    if mapped:
                        findings.append(mapped)

            display.vv(f"splunk_finding_info: found {len(findings)} findings")

        return findings

    def filter_findings_by_title(
        self,
        findings: List[Dict[str, Any]],
        title: str,
    ) -> List[Dict[str, Any]]:
        """Filter findings by exact title match.

        Args:
            findings: List of findings to filter.
            title: The title to match.

        Returns:
            Filtered list of findings.
        """
        display.vv(f"splunk_finding_info: filtering findings by title: {title}")

        filtered = [f for f in findings if f.get("title") == title]

        display.vv(f"splunk_finding_info: found {len(filtered)} findings with matching title")
        return filtered

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_finding_info: starting module execution")

        # Validate arguments
        if not check_argspec(self, self._result, DOCUMENTATION):
            display.v(f"splunk_finding_info: argument validation failed: {self._result.get('msg')}")
            return self._result

        # Get API path configuration from task args
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_app = self._task.args.get("api_app", DEFAULT_API_APP_SECURITY_SUITE)

        # Build the API path
        self.api_object = self._build_api_path()
        display.vv(f"splunk_finding_info: using API path: {self.api_object}")

        # Setup connection
        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "ref_id",
                "title",
                "earliest",
                "latest",
                "limit",
                "api_namespace",
                "api_user",
                "api_app",
            ],
        )

        # Get query parameters
        ref_id = self._task.args.get("ref_id")
        title = self._task.args.get("title")

        try:
            if ref_id:
                # Query specific finding by ref_id
                display.v(f"splunk_finding_info: querying by ref_id: {ref_id}")
                finding = self.get_finding_by_id(conn_request, ref_id)
                # Return as list for consistency
                self._result["findings"] = [finding] if finding else []

            elif title:
                # Query all findings and filter by title
                display.v(f"splunk_finding_info: querying by title: {title}")
                all_findings = self.get_all_findings(conn_request)
                self._result["findings"] = self.filter_findings_by_title(all_findings, title)

            else:
                # Return all findings
                display.v("splunk_finding_info: querying all findings")
                self._result["findings"] = self.get_all_findings(conn_request)

            self._result["changed"] = False
            display.v(f"splunk_finding_info: returning {len(self._result['findings'])} finding(s)")

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                # Handle 404 gracefully - return empty list
                self._result["changed"] = False
                self._result["findings"] = []
                display.v("splunk_finding_info: no findings found (404)")
            else:
                self.fail_json(
                    msg=f"Failed to query finding(s): {error_msg}",
                )

        return self._result
