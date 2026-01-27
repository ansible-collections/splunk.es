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
Unit tests for the splunk_response_plan_execution action plugin.
"""


import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_response_plan_execution import (
    TASK_STATUS_TO_API,
    ActionModule,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


def _get_msg_str(result: dict) -> str:
    """Get message from result as a lowercase string.

    Handles both string and list message formats that Ansible can return.

    Args:
        result: The result dictionary from module execution.

    Returns:
        The message as a lowercase string.
    """
    msg = result.get("msg", "")
    if isinstance(msg, list):
        return " ".join(str(m) for m in msg).lower()
    return str(msg).lower()


# Test data: API Response Payloads
TEMPLATE_001_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567001"
TEMPLATE_002_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567002"
INVESTIGATION_UUID = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
APPLIED_PLAN_UUID = "c3d4e5f6-a7b8-9012-cdef-123456789012"
PHASE_001_UUID = "d4e5f6a7-b8c9-0123-defa-234567890123"
TASK_001_UUID = "e5f6a7b8-c9d0-1234-efab-345678901234"

# Response plan templates returned by GET /v1/responsetemplates
RESPONSE_TEMPLATES = {
    "items": [
        {
            "id": TEMPLATE_001_UUID,
            "name": "Incident Response Plan",
            "description": "Standard incident response",
            "template_status": "published",
            "phases": [
                {
                    "id": PHASE_001_UUID,
                    "name": "Investigation",
                    "tasks": [
                        {
                            "id": TASK_001_UUID,
                            "name": "Initial Triage",
                            "description": "Perform initial assessment",
                            "status": "Pending",
                            "owner": "admin",
                            "is_note_required": True,
                        },
                    ],
                },
            ],
        },
        {
            "id": TEMPLATE_002_UUID,
            "name": "Data Breach Response",
            "description": "Data breach handling",
            "template_status": "published",
            "phases": [],
        },
    ],
}

# Investigation with no applied response plans
INVESTIGATION_NO_PLANS = {
    "id": INVESTIGATION_UUID,
    "name": "Test Investigation",
    "status": "1",
    "response_plans": [],
}

# Investigation with an applied response plan
INVESTIGATION_WITH_PLAN = {
    "id": INVESTIGATION_UUID,
    "name": "Test Investigation",
    "status": "1",
    "response_plans": [
        {
            "id": APPLIED_PLAN_UUID,
            "name": "Incident Response Plan",
            "template_id": TEMPLATE_001_UUID,
            "phases": [
                {
                    "id": PHASE_001_UUID,
                    "name": "Investigation",
                    "tasks": [
                        {
                            "id": TASK_001_UUID,
                            "name": "Initial Triage",
                            "description": "Perform initial assessment",
                            "status": "Pending",
                            "owner": "admin",
                            "is_note_required": True,
                        },
                    ],
                },
            ],
        },
    ],
}

# Applied response plan returned from POST
APPLIED_RESPONSE_PLAN = {
    "id": APPLIED_PLAN_UUID,
    "name": "Incident Response Plan",
    "source_template_id": TEMPLATE_001_UUID,
    "phases": [
        {
            "id": PHASE_001_UUID,
            "name": "Investigation",
            "tasks": [
                {
                    "id": TASK_001_UUID,
                    "name": "Initial Triage",
                    "description": "Perform initial assessment",
                    "status": "Pending",
                    "owner": "admin",
                    "is_note_required": True,
                },
            ],
        },
    ],
}


class TestSplunkResponsePlanExecution:
    """Test class for the splunk_response_plan_execution action plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock Task object
        task = MagicMock(Task)
        task.check_mode = False

        # Create mock play context
        play_context = MagicMock()
        play_context.check_mode = False

        # Create a mock connection
        connection = patch(
            "ansible_collections.splunk.es.plugins.module_utils.splunk.Connection",
        )

        # Ansible's template engine
        fake_loader = {}
        templar = Templar(loader=fake_loader)

        # Create the action plugin instance
        self._plugin = ActionModule(
            task=task,
            connection=connection,
            play_context=play_context,
            loader=fake_loader,
            templar=templar,
            shared_loader_obj=None,
        )

        # Set required task attributes
        self._plugin._task.action = "splunk_response_plan_execution"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Apply Response Plan Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_apply_response_plan_by_name_success(self, connection, monkeypatch):
        """Test successful application of a response plan by name."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_NO_PLANS)
            return {}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(APPLIED_RESPONSE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "response_plan_execution" in result
        assert result["response_plan_execution"]["after"]["applied"] is True
        assert "applied" in _get_msg_str(result) or "success" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_apply_response_plan_by_uuid_success(self, connection, monkeypatch):
        """Test successful application of a response plan by UUID."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_NO_PLANS)
            return {}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(APPLIED_RESPONSE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": TEMPLATE_001_UUID,  # Using UUID
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert result["response_plan_execution"]["after"]["applied"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_apply_response_plan_idempotent(self, connection, monkeypatch):
        """Test that applying an already applied plan returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "no change" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_apply_response_plan_not_found(self, connection, monkeypatch):
        """Test that applying a non-existent response plan returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Non-Existent Plan",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "not found" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_apply_response_plan_check_mode(self, connection, monkeypatch):
        """Test check mode for applying a response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_NO_PLANS)
            return {}

        create_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            create_called.append(True)
            return copy.deepcopy(APPLIED_RESPONSE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(create_called) == 0  # API should not be called
        assert "check mode" in _get_msg_str(result)

    # Remove Response Plan Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_remove_response_plan_success(self, connection, monkeypatch):
        """Test successful removal of an applied response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        delete_called = []

        def delete_by_path(self, path):
            delete_called.append(path)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(delete_called) == 1
        assert APPLIED_PLAN_UUID in delete_called[0]
        assert result["response_plan_execution"]["after"]["applied"] is False

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_remove_response_plan_not_applied(self, connection, monkeypatch):
        """Test removing a response plan that isn't applied returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_NO_PLANS)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "already absent" in _get_msg_str(result) or "not applied" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_remove_response_plan_check_mode(self, connection, monkeypatch):
        """Test check mode for removing a response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        delete_called = []

        def delete_by_path(self, path):
            delete_called.append(True)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(delete_called) == 0  # DELETE should not be called
        assert "check mode" in _get_msg_str(result)

    # Task Management Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_update_status_success(self, connection, monkeypatch):
        """Test successfully updating a task's status."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        task_updates = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            if "tasks" in rest_path:
                task_updates.append({"path": rest_path, "data": data})
                return {"status": "Started", "owner": "admin"}
            return copy.deepcopy(APPLIED_RESPONSE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "tasks": [
                {
                    "phase_name": "Investigation",
                    "task_name": "Initial Triage",
                    "status": "started",
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(task_updates) == 1
        assert task_updates[0]["data"]["status"] == "Started"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_update_owner_success(self, connection, monkeypatch):
        """Test successfully updating a task's owner."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        task_updates = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            if "tasks" in rest_path:
                task_updates.append({"path": rest_path, "data": data})
                return {"status": "Pending", "owner": "unassigned"}
            return copy.deepcopy(APPLIED_RESPONSE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "tasks": [
                {
                    "phase_name": "Investigation",
                    "task_name": "Initial Triage",
                    "owner": "unassigned",
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(task_updates) == 1
        assert task_updates[0]["data"]["owner"] == "unassigned"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_update_idempotent(self, connection, monkeypatch):
        """Test that task update is idempotent when already in desired state."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Investigation with task already in desired state
        investigation = copy.deepcopy(INVESTIGATION_WITH_PLAN)
        investigation["response_plans"][0]["phases"][0]["tasks"][0]["status"] = "Started"

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return investigation
            return {}

        task_updates = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            if "tasks" in rest_path:
                task_updates.append(True)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "tasks": [
                {
                    "phase_name": "Investigation",
                    "task_name": "Initial Triage",
                    "status": "started",
                    "owner": "admin",  # Same as current
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(task_updates) == 0  # No API call should be made

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_update_phase_not_found(self, connection, monkeypatch):
        """Test task update with non-existent phase."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "tasks": [
                {
                    "phase_name": "Non-Existent Phase",
                    "task_name": "Some Task",
                    "status": "started",
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should not fail, but task should report error in results
        assert result.get("failed") is not True
        assert result["changed"] is False
        tasks_updated = result.get("response_plan_execution", {}).get("tasks_updated", [])
        assert len(tasks_updated) == 1
        assert "error" in tasks_updated[0]

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_update_task_not_found(self, connection, monkeypatch):
        """Test task update with non-existent task."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "tasks": [
                {
                    "phase_name": "Investigation",
                    "task_name": "Non-Existent Task",
                    "status": "started",
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should not fail, but task should report error in results
        assert result.get("failed") is not True
        assert result["changed"] is False
        tasks_updated = result.get("response_plan_execution", {}).get("tasks_updated", [])
        assert len(tasks_updated) == 1
        assert "error" in tasks_updated[0]

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_update_check_mode(self, connection, monkeypatch):
        """Test check mode for task updates."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_WITH_PLAN)
            return {}

        task_updates = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            if "tasks" in rest_path:
                task_updates.append(True)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "tasks": [
                {
                    "phase_name": "Investigation",
                    "task_name": "Initial Triage",
                    "status": "started",
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(task_updates) == 0  # No API call should be made

    # Validation Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_investigation_ref_id(self, connection):
        """Test that missing investigation_ref_id returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "response_plan": "Incident Response Plan",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "investigation_ref_id" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_response_plan(self, connection):
        """Test that missing response_plan returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "response_plan" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_no_templates_found(self, connection, monkeypatch):
        """Test handling when no response templates exist."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "responsetemplates" in path:
                return {"items": []}
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Some Plan",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "no response plan templates" in _get_msg_str(result)

    # Custom API Path Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            if "responsetemplates" in path:
                return copy.deepcopy(RESPONSE_TEMPLATES)
            if "incidents" in path and "responseplans" not in path:
                return copy.deepcopy(INVESTIGATION_NO_PLANS)
            return {}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_paths.append(rest_path)
            return copy.deepcopy(APPLIED_RESPONSE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan": "Incident Response Plan",
            "state": "present",
            "api_namespace": "customNS",
            "api_user": "customuser",
            "api_app": "CustomApp",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        # Verify custom path was used in all API calls
        for path in captured_paths:
            assert "customNS" in path
            assert "customuser" in path
            assert "CustomApp" in path


class TestResponsePlanExecutionHelperMethods:
    """Tests for the helper methods in the response plan execution action plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        task = MagicMock(Task)
        task.check_mode = False

        play_context = MagicMock()
        connection = patch(
            "ansible_collections.splunk.es.plugins.module_utils.splunk.Connection",
        )

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

        self._plugin._task.action = "splunk_response_plan_execution"
        self._plugin._task.async_val = False

    # API Path Building Tests
    def test_build_response_plans_path(self):
        """Test building the response plans API path."""
        self._plugin.api_namespace = "servicesNS"
        self._plugin.api_user = "nobody"
        self._plugin.api_app = "missioncontrol"

        result = self._plugin._build_response_plans_path("inv-001-uuid")

        assert result == "servicesNS/nobody/missioncontrol/v1/incidents/inv-001-uuid/responseplans"

    def test_build_response_plan_path(self):
        """Test building a specific response plan API path."""
        self._plugin.api_namespace = "servicesNS"
        self._plugin.api_user = "nobody"
        self._plugin.api_app = "missioncontrol"

        result = self._plugin._build_response_plan_path("inv-001-uuid", "plan-001-uuid")

        expected = (
            "servicesNS/nobody/missioncontrol/v1/incidents/inv-001-uuid/responseplans/plan-001-uuid"
        )
        assert result == expected

    def test_build_task_path(self):
        """Test building a task API path."""
        self._plugin.api_namespace = "servicesNS"
        self._plugin.api_user = "nobody"
        self._plugin.api_app = "missioncontrol"

        result = self._plugin._build_task_path(
            "inv-001-uuid",
            "plan-001-uuid",
            "phase-001-uuid",
            "task-001-uuid",
        )

        expected = (
            "servicesNS/nobody/missioncontrol/v1/incidents/inv-001-uuid/"
            "responseplans/plan-001-uuid/phase/phase-001-uuid/tasks/task-001-uuid"
        )
        assert result == expected

    def test_build_templates_path(self):
        """Test building the templates API path."""
        self._plugin.api_namespace = "servicesNS"
        self._plugin.api_user = "nobody"
        self._plugin.api_app = "missioncontrol"

        result = self._plugin._build_templates_path()

        assert result == "servicesNS/nobody/missioncontrol/v1/responsetemplates"

    def test_build_templates_path_custom(self):
        """Test building the templates API path with custom values."""
        self._plugin.api_namespace = "customNS"
        self._plugin.api_user = "customuser"
        self._plugin.api_app = "CustomApp"

        result = self._plugin._build_templates_path()

        assert result == "customNS/customuser/CustomApp/v1/responsetemplates"

    # Phase/Task Finding Tests
    def test_find_phase_by_name_found(self):
        """Test finding a phase by name."""
        phases = [
            {"id": "phase-001", "name": "Investigation"},
            {"id": "phase-002", "name": "Containment"},
        ]

        result = self._plugin._find_phase_by_name(phases, "Investigation")

        assert result is not None
        assert result["id"] == "phase-001"

    def test_find_phase_by_name_not_found(self):
        """Test finding a non-existent phase."""
        phases = [
            {"id": "phase-001", "name": "Investigation"},
        ]

        result = self._plugin._find_phase_by_name(phases, "Containment")

        assert result is None

    def test_find_phase_by_name_empty_list(self):
        """Test finding phase in empty list."""
        result = self._plugin._find_phase_by_name([], "Investigation")

        assert result is None

    def test_find_task_by_name_found(self):
        """Test finding a task by name."""
        tasks = [
            {"id": "task-001", "name": "Initial Triage"},
            {"id": "task-002", "name": "Gather Evidence"},
        ]

        result = self._plugin._find_task_by_name(tasks, "Initial Triage")

        assert result is not None
        assert result["id"] == "task-001"

    def test_find_task_by_name_not_found(self):
        """Test finding a non-existent task."""
        tasks = [
            {"id": "task-001", "name": "Initial Triage"},
        ]

        result = self._plugin._find_task_by_name(tasks, "Non-Existent Task")

        assert result is None

    def test_find_task_by_name_empty_list(self):
        """Test finding task in empty list."""
        result = self._plugin._find_task_by_name([], "Some Task")

        assert result is None

    # Template Lookup Tests
    def test_get_template_name_by_id_found(self):
        """Test looking up template name by ID."""
        templates = [
            {"id": "template-001", "name": "Incident Response"},
            {"id": "template-002", "name": "Data Breach"},
        ]

        result = self._plugin._get_template_name_by_id(templates, "template-001")

        assert result == "Incident Response"

    def test_get_template_name_by_id_not_found(self):
        """Test looking up non-existent template ID."""
        templates = [
            {"id": "template-001", "name": "Incident Response"},
        ]

        result = self._plugin._get_template_name_by_id(templates, "template-999")

        assert result is None

    def test_get_template_id_by_name_found(self):
        """Test looking up template ID by name."""
        templates = [
            {"id": "template-001", "name": "Incident Response"},
            {"id": "template-002", "name": "Data Breach"},
        ]

        result = self._plugin._get_template_id_by_name(templates, "Data Breach")

        assert result == "template-002"

    def test_get_template_id_by_name_not_found(self):
        """Test looking up non-existent template name."""
        templates = [
            {"id": "template-001", "name": "Incident Response"},
        ]

        result = self._plugin._get_template_id_by_name(templates, "Non-Existent")

        assert result is None

    # Applied Plan Finding Tests
    def test_find_applied_plan_by_name_found(self):
        """Test finding an applied plan by name."""
        applied_plans = [
            {"id": "applied-001", "name": "Incident Response"},
            {"id": "applied-002", "name": "Data Breach"},
        ]

        result = self._plugin._find_applied_plan_by_name(applied_plans, "Incident Response")

        assert result is not None
        assert result["id"] == "applied-001"

    def test_find_applied_plan_by_name_not_found(self):
        """Test finding a non-existent applied plan."""
        applied_plans = [
            {"id": "applied-001", "name": "Incident Response"},
        ]

        result = self._plugin._find_applied_plan_by_name(applied_plans, "Data Breach")

        assert result is None

    def test_find_applied_plan_by_name_empty_list(self):
        """Test finding applied plan in empty list."""
        result = self._plugin._find_applied_plan_by_name([], "Any Plan")

        assert result is None


class TestTaskStatusMapping:
    """Tests for the task status mapping constants."""

    def test_task_status_to_api_started(self):
        """Test started status maps correctly."""
        assert TASK_STATUS_TO_API["started"] == "Started"

    def test_task_status_to_api_ended(self):
        """Test ended status maps correctly."""
        assert TASK_STATUS_TO_API["ended"] == "Ended"

    def test_task_status_to_api_reopened(self):
        """Test reopened status maps correctly."""
        assert TASK_STATUS_TO_API["reopened"] == "Reopened"

    def test_task_status_to_api_pending(self):
        """Test pending status maps correctly."""
        assert TASK_STATUS_TO_API["pending"] == "Pending"
