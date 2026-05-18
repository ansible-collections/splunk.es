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
The action module for splunk_ai_correlation_search
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
from ansible_collections.splunk.es.plugins.modules.splunk_ai_correlation_search import DOCUMENTATION


display = Display()

# Pre-built SPL search templates for AI Factory monitoring
SEARCH_TEMPLATES = {
    "gpu_thermal": (
        '| mstats avg(dcgm_gpu_temp) as gpu_temp '
        'WHERE index={index} by host gpu_id span=5m '
        '| where gpu_temp > {threshold}'
    ),
    "model_drift": (
        '| mstats avg(nim_inference_drift_score) as drift_score '
        'WHERE index={index} by model_name endpoint span=15m '
        '| where drift_score > {threshold}'
    ),
    "infiniband_errors": (
        '| mstats sum(ib_port_rcv_errors) as rcv_errors '
        'sum(ib_port_xmit_discards) as xmit_discards '
        'WHERE index={index} by host port_id span=5m '
        '| where rcv_errors > 0 OR xmit_discards > 0'
    ),
    "training_anomaly": (
        '| mstats avg(training_loss) as loss stdev(training_loss) as loss_std '
        'WHERE index={index} by job_id framework span=5m '
        '| where loss > (loss + 3 * loss_std) OR loss != loss'
    ),
    "gpu_utilization": (
        '| mstats avg(dcgm_gpu_utilization) as gpu_util '
        'WHERE index={index} by host gpu_id span=15m '
        '| where gpu_util < {threshold}'
    ),
}

DEFAULT_THRESHOLDS = {
    "gpu_thermal": 85,
    "model_drift": 0.15,
    "infiniband_errors": 0,
    "training_anomaly": 0,
    "gpu_utilization": 10,
}


class ActionModule(ActionBase):
    """Action module for managing AI Factory correlation searches in Splunk ES."""

    SAVED_SEARCHES_API = "saved/searches"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._result = None
        self.module_name = "correlation_search"
        self.api_namespace = DEFAULT_API_NAMESPACE
        self.api_user = DEFAULT_API_USER

    def fail_json(self, msg: str) -> None:
        """Raise an AnsibleActionFail with a cleaned up message."""
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def _build_api_path(self, app: str) -> str:
        """Build the saved searches API path."""
        return f"{self.api_namespace}/{self.api_user}/{app}/{self.SAVED_SEARCHES_API}"

    def _build_search_spl(self) -> str:
        """Build the SPL search string from the template and parameters."""
        search_type = self._task.args.get("search_type")
        metrics_index = self._task.args.get("metrics_index", "ai_factory_metrics")

        if search_type == "custom":
            search = self._task.args.get("search")
            if not search:
                self.fail_json(msg="'search' parameter is required when search_type is 'custom'")
            return search

        template = SEARCH_TEMPLATES.get(search_type)
        if not template:
            self.fail_json(msg=f"Unknown search_type: {search_type}")

        threshold = self._task.args.get("threshold", DEFAULT_THRESHOLDS.get(search_type, 0))
        return template.format(index=metrics_index, threshold=threshold)

    def _build_search_payload(self) -> dict[str, Any]:
        """Build the saved search payload."""
        name = self._task.args.get("name")
        search_spl = self._build_search_spl()
        severity = self._task.args.get("severity", "high")
        disabled = self._task.args.get("disabled", False)
        cron_schedule = self._task.args.get("cron_schedule", "*/5 * * * *")

        severity_map = {
            "informational": "1",
            "low": "2",
            "medium": "3",
            "high": "4",
            "critical": "5",
        }

        payload = {
            "name": name,
            "search": search_spl,
            "disabled": "1" if disabled else "0",
            "cron_schedule": cron_schedule,
            "is_scheduled": "1",
            "alert_type": "always",
            "alert.severity": severity_map.get(severity, "4"),
            "alert.suppress": "0",
            "action.correlationsearch.enabled": "1",
            "action.correlationsearch.label": name,
            "action.notable": "1",
            "action.notable.param.security_domain": "network",
            "action.notable.param.severity": severity,
            "action.notable.param.rule_title": name,
            "action.notable.param.rule_description": (
                f"AI Factory correlation search: {self._task.args.get('search_type')}"
            ),
        }

        return payload

    def run(self, tmp=None, task_vars=None):
        """Execute the action module."""
        self._supports_check_mode = True
        self._result = super().run(tmp, task_vars)

        display.v("splunk_ai_correlation_search: starting module execution")

        if not check_argspec(self, self._result, DOCUMENTATION):
            return self._result

        self._result[self.module_name] = {}
        self._result["changed"] = False

        self.api_namespace = self._task.args.get("api_namespace", DEFAULT_API_NAMESPACE)
        self.api_user = self._task.args.get("api_user", DEFAULT_API_USER)

        name = self._task.args.get("name")
        state = self._task.args.get("state", "present")
        app = self._task.args.get("app", "SplunkEnterpriseSecuritySuite")
        api_path = self._build_api_path(app)

        conn = Connection(self._connection.socket_path)
        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=[
                "state", "search_type", "threshold", "severity",
                "metrics_index", "api_namespace", "api_user",
            ],
        )

        # Check for existing search
        existing = {}
        try:
            existing = conn_request.get_by_path(f"{api_path}/{name}")
        except Exception:
            pass

        if state == "present":
            payload = self._build_search_payload()

            if self._task.check_mode:
                self._result[self.module_name] = {"before": existing or None, "after": payload}
                self._result["changed"] = True
                self._result["msg"] = "Check mode: would create/update correlation search"
                return self._result

            api_response = conn_request.create_update(api_path, data=payload)
            after = api_response if api_response else payload

            self._result[self.module_name] = {"before": existing or None, "after": after}
            self._result["changed"] = True
            self._result["msg"] = "Correlation search created/updated successfully"

        elif state == "absent":
            if not existing:
                self._result[self.module_name] = {"before": None, "after": None}
                self._result["changed"] = False
                self._result["msg"] = "Correlation search does not exist"
            else:
                if self._task.check_mode:
                    self._result[self.module_name] = {"before": existing, "after": None}
                    self._result["changed"] = True
                    self._result["msg"] = "Check mode: would delete correlation search"
                    return self._result

                conn_request.delete_by_path(f"{api_path}/{name}")
                self._result[self.module_name] = {"before": existing, "after": None}
                self._result["changed"] = True
                self._result["msg"] = "Correlation search deleted successfully"

        display.v(f"splunk_ai_correlation_search: completed with changed={self._result['changed']}")
        return self._result
