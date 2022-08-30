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
from ansible_collections.splunk.es.plugins.action.splunk_data_inputs_network import (
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
                "name": "default:8100",
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
                "name": "default:8101",
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
                "name": "default:7890",
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
                "name": "splunktcptoken://test_token",
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
        "name": 8100,
        "connection_host": "ip",
        "disabled": False,
        "host": "$decideOnStartup",
        "restrict_to_host": "default",
    },
    "tcp_raw": {
        "protocol": "tcp",
        "datatype": "raw",
        "name": 8101,
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

REPLACED_RESPONSE_PAYLOAD = {
    "tcp_cooked": {
        "entry": [
            {
                "name": "default:8100",
                "content": {
                    "connection_host": "ip",
                    "disabled": True,
                    "host": "$decideOnStartup",
                    "restrictToHost": "default",
                },
            }
        ],
    },
    "tcp_raw": {
        "entry": [
            {
                "name": "default:8101",
                "content": {
                    "connection_host": "ip",
                    "disabled": True,
                    "host": "$decideOnStartup",
                    "index": "default",
                    "queue": "parsingQueue",
                    "rawTcpDoneTimeout": 10,
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
                "name": "default:7890",
                "content": {
                    "connection_host": "ip",
                    "disabled": True,
                    "host": "$decideOnStartup",
                    "index": "default",
                    "no_appending_timestamp": False,
                    "no_priority_stripping": False,
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
                "name": "splunktcptoken://test_token",
                "content": {
                    "token": "01234567-0123-0123-0123-012345678900",
                },
            }
        ],
    },
}

REPLACED_REQUEST_PAYLOAD = {
    "tcp_cooked": {
        "protocol": "tcp",
        "datatype": "cooked",
        "name": "default:8100",
        "connection_host": "ip",
        "disabled": True,
        "host": "$decideOnStartup",
        "restrict_to_host": "default",
    },
    "tcp_raw": {
        "protocol": "tcp",
        "datatype": "raw",
        "name": "default:8101",
        "connection_host": "ip",
        "disabled": True,
        "host": "$decideOnStartup",
        "index": "default",
        "queue": "parsingQueue",
        "raw_tcp_done_timeout": 10,
        "restrict_to_host": "default",
        "source": "test_source",
        "sourcetype": "test_source_type",
    },
    "udp": {
        "protocol": "udp",
        "name": "default:7890",
        "connection_host": "ip",
        "disabled": True,
        "host": "$decideOnStartup",
        "index": "default",
        "no_appending_timestamp": False,
        "no_priority_stripping": False,
        "queue": "parsingQueue",
        "restrict_to_host": "default",
        "source": "test_source",
        "sourcetype": "test_source_type",
    },
    "splunktcptoken": {
        "protocol": "tcp",
        "datatype": "splunktcptoken",
        "name": "splunktcptoken://test_token",
        "token": "01234567-0123-0123-0123-012345678900",
    },
}


class TestSplunkEsDataInputsNetworksRules:
    def setup(self):
        task = MagicMock(Task)
        # Ansible > 2.13 looks for check_mode in task
        task.check_mode = False
        play_context = MagicMock()
        # Ansible <= 2.13 looks for check_mode in play_context
        play_context.check_mode = False
        connection = patch(
            "ansible_collections.splunk.es.plugins.module_utils.splunk.Connection"
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
        self._plugin._task.action = "data_inputs_network"
        self._plugin._task.async_val = False
        self._task_vars = {}

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_merged(self, connection, monkeypatch):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        # patch update operation
        update_response = RESPONSE_PAYLOAD["tcp_cooked"]

        def get_by_path(self, path):
            return {}

        def create_update(
            self, rest_path, data=None, mock=None, mock_data=None
        ):
            return update_response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # tcp_cooked
        update_response = RESPONSE_PAYLOAD["tcp_cooked"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # tcp_raw
        update_response = RESPONSE_PAYLOAD["tcp_raw"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # udp
        update_response = RESPONSE_PAYLOAD["udp"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # splunktcptoken
        update_response = RESPONSE_PAYLOAD["splunktcptoken"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # ssl
        update_response = RESPONSE_PAYLOAD["ssl"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["ssl"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_merged_idempotent(self, conn, monkeypatch):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        # patch get operation
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]

        def get_by_path(self, path):
            return get_response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # tcp_cooked
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # tcp_raw
        get_response = RESPONSE_PAYLOAD["tcp_raw"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # udp
        get_response = RESPONSE_PAYLOAD["udp"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # splunktcptoken
        get_response = RESPONSE_PAYLOAD["splunktcptoken"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # ssl
        get_response = RESPONSE_PAYLOAD["ssl"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["ssl"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_replaced(self, conn, monkeypatch):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        # patch get operation
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]
        # patch update operation
        update_response = REPLACED_RESPONSE_PAYLOAD["tcp_cooked"]

        get_response = RESPONSE_PAYLOAD["tcp_cooked"]

        def delete_by_path(
            self, rest_path, data=None, mock=None, mock_data=None
        ):
            return {}

        def create_update(
            self, rest_path, data=None, mock=None, mock_data=None
        ):
            return update_response

        def get_by_path(self, path):
            return get_response

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        # tcp_cooked
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]
        update_response = REPLACED_RESPONSE_PAYLOAD["tcp_cooked"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # tcp_raw
        get_response = RESPONSE_PAYLOAD["tcp_raw"]
        update_response = REPLACED_RESPONSE_PAYLOAD["tcp_raw"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # udp
        get_response = RESPONSE_PAYLOAD["udp"]
        update_response = REPLACED_RESPONSE_PAYLOAD["udp"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # splunktcptoken
        get_response = RESPONSE_PAYLOAD["splunktcptoken"]
        update_response = REPLACED_RESPONSE_PAYLOAD["splunktcptoken"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_replaced_idempotent(
        self, conn, monkeypatch
    ):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        # patch get operation
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]

        def get_by_path(self, path):
            return get_response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # tcp_cooked
        get_response = REPLACED_RESPONSE_PAYLOAD["tcp_cooked"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # tcp_raw
        get_response = REPLACED_RESPONSE_PAYLOAD["tcp_raw"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # udp
        get_response = REPLACED_RESPONSE_PAYLOAD["udp"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # splunktcptoken
        get_response = REPLACED_RESPONSE_PAYLOAD["splunktcptoken"]
        self._plugin._task.args = {
            "state": "replaced",
            "config": [REPLACED_REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_deleted(self, conn, monkeypatch):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        def delete_by_path(
            self, rest_path, data=None, mock=None, mock_data=None
        ):
            return {}

        get_response = RESPONSE_PAYLOAD["tcp_cooked"]

        def get_by_path(self, path):
            return get_response

        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)
        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # tcp_cooked
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # tcp_raw
        get_response = RESPONSE_PAYLOAD["tcp_raw"]
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # udp
        get_response = RESPONSE_PAYLOAD["udp"]
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

        # splunktcptoken
        get_response = RESPONSE_PAYLOAD["splunktcptoken"]
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_deleted_idempotent(
        self, conn, monkeypatch
    ):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path):
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # tcp_cooked
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # tcp_raw
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # udp
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # splunktcptoken
        self._plugin._task.args = {
            "state": "deleted",
            "config": [REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_network_gathered(self, conn, monkeypatch):
        self._plugin._connection.socket_path = (
            tempfile.NamedTemporaryFile().name
        )
        self._plugin._connection._shell = MagicMock()

        # patch get operation
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]

        def get_by_path(self, path):
            return get_response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # tcp_cooked
        get_response = RESPONSE_PAYLOAD["tcp_cooked"]
        self._plugin._task.args = {
            "state": "gathered",
            "config": [REQUEST_PAYLOAD["tcp_cooked"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # tcp_raw
        get_response = RESPONSE_PAYLOAD["tcp_raw"]
        self._plugin._task.args = {
            "state": "gathered",
            "config": [REQUEST_PAYLOAD["tcp_raw"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # udp
        get_response = RESPONSE_PAYLOAD["udp"]
        self._plugin._task.args = {
            "state": "gathered",
            "config": [REQUEST_PAYLOAD["udp"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # splunktcptoken
        get_response = RESPONSE_PAYLOAD["splunktcptoken"]
        self._plugin._task.args = {
            "state": "gathered",
            "config": [REQUEST_PAYLOAD["splunktcptoken"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False

        # ssl
        get_response = RESPONSE_PAYLOAD["ssl"]
        self._plugin._task.args = {
            "state": "merged",
            "config": [REQUEST_PAYLOAD["ssl"]],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        assert result["changed"] is False
