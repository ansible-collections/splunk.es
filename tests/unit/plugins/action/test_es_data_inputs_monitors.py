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

from ansible_collections.splunk.es.plugins.action.splunk_data_inputs_monitor import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


RESPONSE_PAYLOAD = {
    "entry": [
        {
            "content": {
                "_rcvbuf": 1572864,
                "blacklist": "//var/log/[a-z]/gm",
                "check-index": None,
                "crcSalt": "<SOURCE>",
                "disabled": False,
                "eai:acl": None,
                "filecount": 74,
                "filestatecount": 82,
                "followTail": False,
                "host": "$decideOnStartup",
                "host_regex": "/(test_host)/gm",
                "host_resolved": "ip-172-31-52-131.us-west-2.compute.internal",
                "host_segment": 3,
                "ignoreOlderThan": "5d",
                "index": "default",
                "recursive": True,
                "source": "test",
                "sourcetype": "test_source_type",
                "time_before_close": 4,
                "whitelist": "//var/log/[0-9]/gm",
            },
            "name": "/var/log",
        },
    ],
}

REQUEST_PAYLOAD = [
    {
        "blacklist": "//var/log/[a-z]/gm",
        "crc_salt": "<SOURCE>",
        "disabled": False,
        "follow_tail": False,
        "host": "$decideOnStartup",
        "host_regex": "/(test_host)/gm",
        "host_segment": 3,
        "index": "default",
        "name": "/var/log",
        "recursive": True,
        "sourcetype": "test_source_type",
        "whitelist": "//var/log/[0-9]/gm",
    },
    {
        "blacklist": "//var/log/[a-z0-9]/gm",
        "crc_salt": "<SOURCE>",
        "disabled": False,
        "follow_tail": False,
        "host": "$decideOnStartup",
        "index": "default",
        "name": "/var/log",
        "recursive": True,
    },
]


class TestSplunkEsDataInputsMonitorRules:
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
        connection._socket_path = tempfile.NamedTemporaryFile().name
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
        self._plugin._task.action = "data_inputs_monitor"
        self._plugin._task.async_val = False
        self._task_vars = {}

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitor_merged(self, connection, monkeypatch):
        self._plugin.api_response = RESPONSE_PAYLOAD
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = {}

        def create_update(
            self,
            rest_path,
            data=None,
            mock=None,
            mock_data=None,
        ):
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
    def test_es_data_inputs_monitor_merged_idempotent(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(
            self,
            rest_path,
            data=None,
            mock=None,
            mock_data=None,
        ):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "merged",
            "config": [
                {
                    "blacklist": "//var/log/[a-z]/gm",
                    "crc_salt": "<SOURCE>",
                    "disabled": False,
                    "follow_tail": False,
                    "host": "$decideOnStartup",
                    "host_regex": "/(test_host)/gm",
                    "host_segment": 3,
                    "index": "default",
                    "name": "/var/log",
                    "recursive": True,
                    "sourcetype": "test_source_type",
                    "whitelist": "//var/log/[0-9]/gm",
                },
            ],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["data_inputs_monitor"]["before"][0]["name"] == "/var/log"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitor_replaced(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = RESPONSE_PAYLOAD

        def create_update(
            self,
            rest_path,
            data=None,
            mock=None,
            mock_data=None,
        ):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "replaced",
            "config": [
                {
                    "blacklist": "//var/log/[a-z0-9]/gm",
                    "crc_salt": "<SOURCE>",
                    "disabled": False,
                    "follow_tail": False,
                    "host": "$decideOnStartup",
                    "index": "default",
                    "name": "/var/log",
                    "recursive": True,
                },
            ],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitor_replaced_idempotent(
        self,
        conn,
        monkeypatch,
    ):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(
            self,
            rest_path,
            data=None,
            mock=None,
            mock_data=None,
        ):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return {
                "entry": [
                    {
                        "content": {
                            "_rcvbuf": 1572864,
                            "blacklist": "//var/log/[a-z]/gm",
                            "check-index": None,
                            "crcSalt": "<SOURCE>",
                            "disabled": False,
                            "eai:acl": None,
                            "filecount": 74,
                            "filestatecount": 82,
                            "followTail": False,
                            "host": "$decideOnStartup",
                            "host_regex": "/(test_host)/gm",
                            "host_resolved": "ip-172-31-52-131.us-west-2.compute.internal",
                            "host_segment": 3,
                            "ignoreOlderThan": "5d",
                            "index": "default",
                            "recursive": True,
                            "source": "test",
                            "sourcetype": "test_source_type",
                            "time_before_close": 4,
                            "whitelist": "//var/log/[0-9]/gm",
                        },
                        "name": "/var/log",
                    },
                ],
            }

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "replaced",
            "config": [
                {
                    "blacklist": "//var/log/[a-z]/gm",
                    "crc_salt": "<SOURCE>",
                    "disabled": False,
                    "follow_tail": False,
                    "host": "$decideOnStartup",
                    "host_regex": "/(test_host)/gm",
                    "host_segment": 3,
                    "index": "default",
                    "name": "/var/log",
                    "recursive": True,
                    "sourcetype": "test_source_type",
                    "whitelist": "//var/log/[0-9]/gm",
                },
            ],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitor_deleted(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(
            self,
            rest_path,
            data=None,
            mock=None,
            mock_data=None,
        ):
            return RESPONSE_PAYLOAD

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "deleted",
            "config": [{"name": "/var/log"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitor_deleted_idempotent(self, connection):
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = {}

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin._task.args = {
            "state": "deleted",
            "config": [{"name": "/var/log"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitor_gathered(self, conn, monkeypatch):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "state": "gathered",
            "config": [{"name": "/var/log"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False
