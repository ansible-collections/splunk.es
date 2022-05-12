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

import unittest
import tempfile
from ansible.playbook.task import Task
from ansible.template import Templar
from ansible_collections.splunk.es.plugins.action.data_inputs_monitors import (
    ActionModule,
)
from ansible_collections.ansible.utils.tests.unit.compat.mock import (
    MagicMock,
    patch,
)

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
        }
    ]
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
    # {
    #     "name": "test_firewallrule_2",
    #     "description": "incoming firewall 2 rule description",
    #     "action": "deny",
    #     "priority": 0,
    #     "source_iptype": "any",
    #     "source_ipnot": False,
    #     "source_port_type": "any",
    #     "destination_iptype": "any",
    #     "direction": "incoming",
    #     "protocol": "tcp",
    # },
]


class TestSplunkEsDataInputsMonitorsRules(unittest.TestCase):
    def setUp(self):
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
        self._plugin.conn_request = patch("ansible_collections.splunk.es.plugins.module_utils.splunk.SplunkRequest")
        self._plugin._task.action = "data_inputs_monitors"
        self._plugin._task.async_val = False
        self._task_vars = {}

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_merged(self, connection):
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = {}
        self._plugin._connection._socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin._task.args = {
            "state": "merged",
            "config": REQUEST_PAYLOAD,
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertTrue(result["changed"])

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_merged_idempotent(self, connection):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = RESPONSE_PAYLOAD
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
                }
            ],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertFalse(result["changed"])

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_replaced(self, connection):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = RESPONSE_PAYLOAD
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
                }
            ],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertTrue(result["changed"])

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_replaced_idempotent(self, connection):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        connection.get_by_path = MagicMock()
        connection.get_by_path.return_value = {
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
                }
            ]
        }
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
                }
            ],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertFalse(result["changed"])

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_deleted(self, connection):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.conn_request._httpapi_error_handle = MagicMock()
        self._plugin.conn_request._httpapi_error_handle.return_value = RESPONSE_PAYLOAD
        self._plugin._task.args = {
            "state": "deleted",
            "config": [{"name": "/var/log"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertTrue(result["changed"])

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_deleted_idempotent(self, connection):
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = {}
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin._task.args = {
            "state": "deleted",
            "config": [{"name": "/var/log"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertFalse(result["changed"])

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_es_data_inputs_monitors_gathered(self, connection):
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()
        self._plugin.search_for_resource_name = MagicMock()
        self._plugin.search_for_resource_name.return_value = RESPONSE_PAYLOAD
        self._plugin._task.args = {
            "state": "gathered",
            "config": [{"name": "/var/log"}],
        }
        result = self._plugin.run(task_vars=self._task_vars)
        self.assertFalse(result["changed"])
