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
The action module for splunk_ai_metrics_index
"""

from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

from ansible_collections.splunk.es.plugins.module_utils import dict_utils as utils
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    check_argspec,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
)
from ansible_collections.splunk.es.plugins.modules.splunk_ai_metrics_index import DOCUMENTATION


display = Display()


class ActionModule(ActionBase):
    """Action module for managing Splunk AI Factory metrics indexes."""

    INDEX_API_OBJECT = "data/indexes"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.module_name = "index"
        self.api_namespace = DEFAULT_API_NAMESPACE
        self.api_user = DEFAULT_API_USER

    def fail_json(self, msg: str) -> None:
        """Raise an AnsibleActionFail with a cleaned up message."""
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def _build_api_path(self) -> str:
        """Build the index API path."""
        return f"{self.api_namespace}/{self.api_user}/search/{self.INDEX_API_OBJECT}"

    def _configure_api(self) -> None:
        """Configure API path components from task arguments."""
        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)
        self.api_object = self._build_api_path()
        display.vv(f"splunk_ai_metrics_index: using API path: {self.api_object}")

    def _build_index_params(self) -> dict[str, Any]:
        """Build index configuration from task arguments."""
        params = {}
        for key in ["name", "datatype", "frozen_time_period_in_secs", "max_data_size"]:
            value = self._task.args.get(key)
            if value is not None:
                params[key] = value
        return params

    def _get_existing_index(self, conn_request: SplunkRequest, name: str) -> dict[str, Any]:
        """Check if an index already exists."""
        display.vv(f"splunk_ai_metrics_index: checking for existing index: {name}")
        try:
            result = conn_request.get_by_path(f"{self.api_object}/{name}")
            if result:
                return result
        except Exception:
            pass
        return {}

    def _create_index(
        self,
        conn_request: SplunkRequest,
        params: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Create a new Splunk index."""
        display.v(f"splunk_ai_metrics_index: creating index: {params.get('name')}")

        if self._task.check_mode:
            return {"before": None, "after": params}, True

        payload = utils.remove_empties(params)
        api_response = conn_request.create_update(self.api_object, data=payload)

        after = api_response if api_response else params
        return {"before": None, "after": after}, True

    def _delete_index(
        self,
        conn_request: SplunkRequest,
        name: str,
        existing: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Delete a Splunk index."""
        if not existing:
            return {"before": None, "after": None}, False

        display.v(f"splunk_ai_metrics_index: deleting index: {name}")
        if self._task.check_mode:
            return {"before": existing, "after": None}, True

        conn_request.delete_by_path(f"{self.api_object}/{name}")
        return {"before": existing, "after": None}, True

    def _configure_transforms(
        self,
        conn_request: SplunkRequest,
        transforms: list[dict[str, Any]],
    ) -> None:
        """Configure metric transforms for the index."""
        if not transforms:
            return

        transforms_api = (
            f"{self.api_namespace}/{self.api_user}/search/data/transforms/metric-schema"
        )
        for transform in transforms:
            payload = {
                "name": transform["name"],
                "METRIC-SCHEMA-MEASURES": transform.get("metric_value_field", "_value"),
                "METRIC-SCHEMA-MEASURES-METRIC-NAME": transform.get(
                    "metric_name_field",
                    "metric_name",
                ),
            }
            dimensions = transform.get("dimensions", [])
            if dimensions:
                payload["METRIC-SCHEMA-BLACKLIST-DIMS"] = ""
                payload["METRIC-SCHEMA-WHITELIST-DIMS"] = ",".join(dimensions)

            display.vv(f"splunk_ai_metrics_index: configuring transform: {transform['name']}")
            if not self._task.check_mode:
                conn_request.create_update(transforms_api, data=payload)

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_ai_metrics_index: starting module execution")

        if not check_argspec(self, self._result, DOCUMENTATION):
            return self._result

        self._result[self.module_name] = {}
        self._result["changed"] = False

        self._configure_api()

        name = self._task.args.get("name")
        state = self._task.args.get("state", "present")
        params = self._build_index_params()
        transforms = self._task.args.get("metric_transforms", [])

        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=["state", "api_namespace", "api_user", "metric_transforms"],
        )

        existing = self._get_existing_index(conn_request, name)

        if state == "present":
            if existing:
                display.v(f"splunk_ai_metrics_index: index {name} already exists, updating")
            index_result, changed = self._create_index(conn_request, params)
            if transforms:
                self._configure_transforms(conn_request, transforms)
        else:
            index_result, changed = self._delete_index(conn_request, name, existing)

        self._result[self.module_name] = index_result
        self._result["changed"] = changed

        if self._task.check_mode:
            self._result["msg"] = (
                "Check mode: would modify index" if changed else "Check mode: no changes required"
            )
        else:
            self._result["msg"] = (
                "Index created/updated successfully" if changed else "No changes required"
            )

        display.v(f"splunk_ai_metrics_index: completed with changed={changed}")
        return self._result
