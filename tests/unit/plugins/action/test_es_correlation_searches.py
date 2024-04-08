# Copyright (c) 2022 Red Hat
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

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible.module_utils.six import PY2


builtin_import = "builtins.__import__"
if PY2:
    builtin_import = "__builtin__.__import__"

import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_correlation_searches import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


RESPONSE_PAYLOAD = {
    "entry": [
        {
            "acl": {"app": "DA-ESS-EndpointProtection"},
            "content": {
                "action.correlationsearch.annotations": '{"cis20": ["test1"], "mitre_attack": ["test2"], "kill_chain_phases": ["test3"], '
                '"nist": ["test4"], "test_framework": ["test5"]}',
                "action.correlationsearch.enabled": "1",
                "action.correlationsearch.label": "Ansible Test",
                "alert.digest_mode": True,
                "alert.suppress": False,
                "alert.suppress.fields": "test_field1",
                "alert.suppress.period": "5s",
                "alert_comparator": "greater than",
                "alert_threshold": "10",
                "alert_type": "number of events",
                "cron_schedule": "*/5 * * * *",
                "description": "test description",
                "disabled": False,
                "dispatch.earliest_time": "-24h",
                "dispatch.latest_time": "now",
                "dispatch.rt_backfill": True,
                "is_scheduled": True,
                "realtime_schedule": True,
                "request.ui_dispatch_app": "SplunkEnterpriseSecuritySuite",
                "schedule_priority": "default",
                "schedule_window": "0",
                "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
                'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
                'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
                'n.src" as "src" | where "count">=6',
            },
            "name": "Ansible Test",
        },
    ],
}

REQUEST_PAYLOAD = [
    {
        "name": "Ansible Test",
        "disabled": False,
        "description": "test description",
        "app": "DA-ESS-EndpointProtection",
        "annotations": {
            "cis20": ["test1"],
            "mitre_attack": ["test2"],
            "kill_chain_phases": ["test3"],
            "nist": ["test4"],
            "custom": [
                {
                    "framework": "test_framework",
                    "custom_annotations": ["test5"],
                },
            ],
        },
        "ui_dispatch_context": "SplunkEnterpriseSecuritySuite",
        "time_earliest": "-24h",
        "time_latest": "now",
        "cron_schedule": "*/5 * * * *",
        "scheduling": "realtime",
        "schedule_window": "0",
        "schedule_priority": "default",
        "trigger_alert": "once",
        "trigger_alert_when": "number of events",
        "trigger_alert_when_condition": "greater than",
        "trigger_alert_when_value": "10",
        "throttle_window_duration": "5s",
        "throttle_fields_to_group_by": ["test_field1"],
        "suppress_alerts": False,
        "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
        'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
        'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
        'n.src" as "src" | where "count">=6',
    },
    {
        "name": "Ansible Test",
        "disabled": False,
        "description": "test description",
        "app": "SplunkEnterpriseSecuritySuite",
        "annotations": {
            "cis20": ["test1", "test2"],
            "mitre_attack": ["test3", "test4"],
            "kill_chain_phases": ["test5", "test6"],
            "nist": ["test7", "test8"],
            "custom": [
                {
                    "framework": "test_framework2",
                    "custom_annotations": ["test9", "test10"],
                },
            ],
        },
        "ui_dispatch_context": "SplunkEnterpriseSecuritySuite",
        "time_earliest": "-24h",
        "time_latest": "now",
        "cron_schedule": "*/5 * * * *",
        "scheduling": "continuous",
        "schedule_window": "auto",
        "schedule_priority": "default",
        "trigger_alert": "once",
        "trigger_alert_when": "number of events",
        "trigger_alert_when_condition": "greater than",
        "trigger_alert_when_value": "10",
        "throttle_window_duration": "5s",
        "throttle_fields_to_group_by": ["test_field1", "test_field2"],
        "suppress_alerts": True,
        "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
        'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
        'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
        'n.src" as "src" | where "count">=6',
    },
]


class TestSplunkEsCorrelationSearches:
    def setup_method(self):
        task = MagicMock(Task)
        # Ansible > 2.13 looks for check_mode in task
        task.check_mode = False
        play_context = MagicMock()
        # Ansible <= 2.13 looks for check_mode in play_context
        play_context.check_mode = False
        connection = patch(
            "ansible_collections.splunk.es.plugins.module_utils.splunk.Connection",
        )
        # connection._socket_path = tempfile.NamedTemporaryFile().name
        fake_loader = {}
        templar = Templar(loader=fake_loader)
        self._plugin = ActionModule(
            task=task,
            connection=connection,
            play_context=play_context,
            loader=fake_loader,
            templar=templar,
            shared_loader_obj=None,
        )
        self._plugin._task.action = "correlation_searches"
        self._plugin._task.async_val = False
        self._task_vars = {}

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_merged(self, connection, monkeypatch):
        self._plugin.api_response = RESPONSE_PAYLOAD
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = {}

        def create_update(self, rest_path, data=None):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD[0]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_merged_idempotent(
        self,
        conn,
        monkeypatch,
    ):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD[0]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        # recheck with module
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_replaced_01(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = RESPONSE_PAYLOAD

        def create_update(self, rest_path, data=None):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        def delete_by_path(self, path):
            return {}

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "state": "replaced",
            "config": [REQUEST_PAYLOAD[1]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_replaced_02(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = RESPONSE_PAYLOAD

        def create_update(self, rest_path, data=None):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        def delete_by_path(self, path):
            return {}

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "state": "replaced",
            "config": [REQUEST_PAYLOAD[1]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_replaced_idempotent(
        self,
        conn,
        monkeypatch,
    ):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        def delete_by_path(self, path):
            return {}

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "state": "replaced",
            "config": [REQUEST_PAYLOAD[0]],
        }
        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_deleted(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        def delete_by_path(self, path):
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "state": "deleted",
            "config": [{"name": "Ansible Test"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_deleted_idempotent(self, connection):
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = {}

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin._task.args = {
            "state": "deleted",
            "config": [{"name": "Ansible Test"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_correlation_searches_gathered(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "gathered",
            "config": [{"name": "Ansible Test"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False
