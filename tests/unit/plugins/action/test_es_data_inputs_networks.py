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
from ansible.playbook.task import Task
from ansible.template import Templar
from ansible_collections.splunk.es.plugins.action.data_inputs_networks import (
    ActionModule,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
)
from ansible_collections.ansible.utils.tests.unit.compat.mock import (
    MagicMock,
    patch,
)

RESPONSE_PAYLOAD = {
    "tcp_cooked": {
        "entry": [
            {
                "name": "8100",
                "content": {
                    "connection_host": "ip",
                    "disabled": False,
                    "host": "$decideOnStartup",
                    "restrictToHost": "default",
                },
            }
        ],
    },
    "tcp_raw": {
        "entry": [
            {
                "name": "8101",
                "content": {
                    "connection_host": "ip",
                    "disabled": True,
                    "host": "$decideOnStartup",
                    "index": "default",
                    "queue": "parsingQueue",
                    "rawTcpDoneTimeout": 9,
                    "restrictToHost": "default",
                    "source": "test_source",
                    "sourcetype": "test_source_type",
                },
            }
        ],
    },
    "udp": {
        "entry": [
            {
                "name": "7890",
                "content": {
                    "connection_host": "ip",
                    "disabled": True,
                    "host": "$decideOnStartup",
                    "index": "default",
                    "no_appending_timestamp": True,
                    "no_priority_stripping": True,
                    "queue": "parsingQueue",
                    "restrictToHost": "default",
                    "source": "test_source",
                    "sourcetype": "test_source_type",
                },
            }
        ],
    },
    "splunktcptoken": {
        "entry": [
            {
                "name": "test_token",
                "content": {
                    "token": "01234567-0123-0123-0123-012345678901",
                },
            }
        ],
    },
    "ssl": {
        "entry": [
            {
                "name": "test_host",
                "content": {},
            }
        ],
    },
}

REQUEST_PAYLOAD = {
    "tcp_cooked": {
        "protocol": "tcp",
        "datatype": "cooked",
        "name": 8101,
        "connection_host": "ip",
        "disabled": False,
        "host": "$decideOnStartup",
        "restrict_to_host": "default",
    },
    "tcp_raw": {
        "protocol": "tcp",
        "datatype": "raw",
        "name": 8100,
        "connection_host": "ip",
        "disabled": True,
        "host": "$decideOnStartup",
        "index": "default",
        "queue": "parsingQueue",
        "raw_tcp_done_timeout": 9,
        "restrict_to_host": "default",
        "source": "test_source",
        "sourcetype": "test_source_type",
    },
    "udp": {
        "protocol": "udp",
        "name": 7890,
        "connection_host": "ip",
        "disabled": True,
        "host": "$decideOnStartup",
        "index": "default",
        "no_appending_timestamp": True,
        "no_priority_stripping": True,
        "queue": "parsingQueue",
        "restrict_to_host": "default",
        "source": "test_source",
        "sourcetype": "test_source_type",
    },
    "splunktcptoken": {
        "protocol": "tcp",
        "datatype": "splunktcptoken",
        "name": "test_token",
        "token": "01234567-0123-0123-0123-012345678901",
    },
    "ssl": {
        "protocol": "tcp",
        "datatype": "ssl",
        "name": "test_host",
    },
}


class TestSplunkEsDataInputsMetworksRules:
    def setup(self):
        task = MagicMock(Task)
        # Ansible > 2.13 looks for check_mode in task
        task.check_mode = False
        play_context = MagicMock()
        # Ansible <= 2.13 looks for check_mode in play_context
        play_context.check_mode = False
        connection = patch("ansible_collections.splunk.es.plugins.module_utils.splunk.Connection")
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
        self._plugin._task.action = "data_inputs_networks"
        self._plugin._task.async_val = False
        self._task_vars = {}

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_networks_merged(self, connection, monkeypatch):
        self._plugin.api_response = RESPONSE_PAYLOAD

        def create_update(self, rest_path, data=None, mock=None, mock_data=None):
            return RESPONSE_PAYLOAD

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # tcp_cooked
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # tcp_raw
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # udp
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # splunktcptoken
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # ssl
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["ssl"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    # @patch("ansible.module_utils.connection.Connection.__rpc__")
    # def test_es_data_inputs_networks_merged_idempotent(self, conn, monkeypatch):
    #     self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
    #     self._plugin._connection._shell = MagicMock()

    #     def create_update(self, rest_path, data=None, mock=None, mock_data=None):
    #         return RESPONSE_PAYLOAD

    #     def get_by_path(self, path):
    #         return RESPONSE_PAYLOAD

    #     monkeypatch.setattr(SplunkRequest, "create_update", create_update)
    #     monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

    #     self._plugin._task.args = {
    #         "state": "merged",
    #         "config": [
    #             {
    #                 "blacklist": "//var/log/[a-z]/gm",
    #                 "crc_salt": "<SOURCE>",
    #                 "disabled": False,
    #                 "follow_tail": False,
    #                 "host": "$decideOnStartup",
    #                 "host_regex": "/(test_host)/gm",
    #                 "host_segment": 3,
    #                 "index": "default",
    #                 "name": "/var/log",
    #                 "recursive": True,
    #                 "sourcetype": "test_source_type",
    #                 "whitelist": "//var/log/[0-9]/gm",
    #             }
    #         ],
    #     }
    #     result = self._plugin.run(task_vars=self._task_vars)
    #     assert result["changed"] is False

    # @patch("ansible.module_utils.connection.Connection.__rpc__")
    # def test_es_data_inputs_networks_replaced(self, conn, monkeypatch):
    #     self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
    #     self._plugin._connection._shell = MagicMock()

    #     def create_update(self, rest_path, data=None, mock=None, mock_data=None):
    #         return RESPONSE_PAYLOAD

    #     def get_by_path(self, path):
    #         return RESPONSE_PAYLOAD

    #     monkeypatch.setattr(SplunkRequest, "create_update", create_update)
    #     monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

    #     self._plugin._task.args = {
    #         "state": "replaced",
    #         "config": [
    #             {
    #                 "blacklist": "//var/log/[a-z0-9]/gm",
    #                 "crc_salt": "<SOURCE>",
    #                 "disabled": False,
    #                 "follow_tail": False,
    #                 "host": "$decideOnStartup",
    #                 "index": "default",
    #                 "name": "/var/log",
    #                 "recursive": True,
    #             }
    #         ],
    #     }
    #     result = self._plugin.run(task_vars=self._task_vars)
    #     assert result["changed"] is True

    # @patch("ansible.module_utils.connection.Connection.__rpc__")
    # def test_es_data_inputs_networks_replaced_idempotent(self, conn, monkeypatch):
    #     self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
    #     self._plugin._connection._shell = MagicMock()

    #     def create_update(self, rest_path, data=None, mock=None, mock_data=None):
    #         return RESPONSE_PAYLOAD

    #     def get_by_path(self, path):
    #         return {
    #             "entry": [
    #                 {
    #                     "content": {
    #                         "_rcvbuf": 1572864,
    #                         "blacklist": "//var/log/[a-z]/gm",
    #                         "check-index": None,
    #                         "crcSalt": "<SOURCE>",
    #                         "disabled": False,
    #                         "eai:acl": None,
    #                         "filecount": 74,
    #                         "filestatecount": 82,
    #                         "followTail": False,
    #                         "host": "$decideOnStartup",
    #                         "host_regex": "/(test_host)/gm",
    #                         "host_resolved": "ip-172-31-52-131.us-west-2.compute.internal",
    #                         "host_segment": 3,
    #                         "ignoreOlderThan": "5d",
    #                         "index": "default",
    #                         "recursive": True,
    #                         "source": "test",
    #                         "sourcetype": "test_source_type",
    #                         "time_before_close": 4,
    #                         "whitelist": "//var/log/[0-9]/gm",
    #                     },
    #                     "name": "/var/log",
    #                 }
    #             ]
    #         }

    #     monkeypatch.setattr(SplunkRequest, "create_update", create_update)
    #     monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

    #     self._plugin._task.args = {
    #         "state": "replaced",
    #         "config": [
    #             {
    #                 "blacklist": "//var/log/[a-z]/gm",
    #                 "crc_salt": "<SOURCE>",
    #                 "disabled": False,
    #                 "follow_tail": False,
    #                 "host": "$decideOnStartup",
    #                 "host_regex": "/(test_host)/gm",
    #                 "host_segment": 3,
    #                 "index": "default",
    #                 "name": "/var/log",
    #                 "recursive": True,
    #                 "sourcetype": "test_source_type",
    #                 "whitelist": "//var/log/[0-9]/gm",
    #             }
    #         ],
    #     }
    #     result = self._plugin.run(task_vars=self._task_vars)
    #     assert result["changed"] is False

    # @patch("ansible.module_utils.connection.Connection.__rpc__")
    # def test_es_data_inputs_networks_deleted(self, conn, monkeypatch):
    #     self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
    #     self._plugin._connection._shell = MagicMock()

    #     def create_update(self, rest_path, data=None, mock=None, mock_data=None):
    #         return RESPONSE_PAYLOAD

    #     def get_by_path(self, path):
    #         return RESPONSE_PAYLOAD

    #     monkeypatch.setattr(SplunkRequest, "create_update", create_update)
    #     monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

    #     self._plugin._task.args = {
    #         "state": "deleted",
    #         "config": [{"name": "/var/log"}],
    #     }
    #     result = self._plugin.run(task_vars=self._task_vars)
    #     assert result["changed"] is True

    # @patch("ansible.module_utils.connection.Connection.__rpc__")
    # def test_es_data_inputs_networks_deleted_idempotent(self, connection):
    #     self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
    #     self._plugin._connection._shell = MagicMock()
    #     self._plugin._task.args = {
    #         "state": "deleted",
    #         "config": [{"name": "/var/log"}],
    #     }
    #     result = self._plugin.run(task_vars=self._task_vars)
    #     assert result["changed"] is False

    # @patch("ansible.module_utils.connection.Connection.__rpc__")
    # def test_es_data_inputs_networks_gathered(self, conn, monkeypatch):
    #     self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
    #     self._plugin._connection._shell = MagicMock()

    #     def get_by_path(self, path):
    #         return RESPONSE_PAYLOAD

    #     monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

    #     self._plugin._task.args = {
    #         "state": "gathered",
    #         "config": [{"name": "/var/log"}],
    #     }
    #     result = self._plugin.run(task_vars=self._task_vars)
    #     assert result["changed"] is False