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
Unit tests for the splunk_response_plan action plugin.
"""


import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_response_plan import (
    ActionModule,
    _build_phase_payload,
    _build_response_plan_api_path,
    _build_response_plan_update_path,
    _build_search_payload,
    _build_task_payload,
    _find_task_id_by_name,
    _map_phase_from_api,
    _map_response_plan_from_api,
    _map_response_plan_to_api,
    _map_task_from_api,
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
# These represent what the Splunk API returns for response plans.
RESPONSE_PLAN_API_RESPONSE = {
    "id": "rp-001-uuid",
    "name": "Incident Response Plan",
    "description": "Standard incident response procedure",
    "template_status": "published",
    "incident_types": [],
    "phases": [
        {
            "id": "phase-001-uuid",
            "name": "Investigation",
            "template_id": "",
            "sla": None,
            "sla_type": "minutes",
            "create_time": "",
            "order": 1,
            "tasks": [
                {
                    "id": "task-001-uuid",
                    "task_id": "",
                    "phase_id": "",
                    "name": "Initial Triage",
                    "description": "Perform initial assessment of the incident",
                    "sla": None,
                    "sla_type": "minutes",
                    "order": 1,
                    "status": "Pending",
                    "is_note_required": True,
                    "owner": "admin",
                    "isNewTask": False,
                    "files": [],
                    "notes": [],
                    "suggestions": {
                        "actions": [],
                        "playbooks": [],
                        "searches": [
                            {
                                "name": "Access Over Time",
                                "description": "Check access patterns",
                                "spl": "| tstats count from datamodel=Authentication by _time span=10m",
                            },
                        ],
                    },
                },
            ],
        },
        {
            "id": "phase-002-uuid",
            "name": "Containment",
            "template_id": "",
            "sla": None,
            "sla_type": "minutes",
            "create_time": "",
            "order": 2,
            "tasks": [
                {
                    "id": "task-002-uuid",
                    "task_id": "",
                    "phase_id": "",
                    "name": "Isolate Affected Systems",
                    "description": "Isolate compromised hosts from network",
                    "sla": None,
                    "sla_type": "minutes",
                    "order": 1,
                    "status": "Pending",
                    "is_note_required": True,
                    "owner": "unassigned",
                    "isNewTask": False,
                    "files": [],
                    "notes": [],
                    "suggestions": {
                        "actions": [],
                        "playbooks": [],
                        "searches": [],
                    },
                },
            ],
        },
    ],
}

RESPONSE_PLAN_LIST_RESPONSE = {
    "items": [
        {
            "id": "rp-001-uuid",
            "name": "Incident Response Plan",
            "description": "Standard incident response procedure",
            "template_status": "published",
            "incident_types": [],
            "phases": [
                {
                    "id": "phase-001-uuid",
                    "name": "Investigation",
                    "tasks": [
                        {
                            "id": "task-001-uuid",
                            "name": "Initial Triage",
                            "description": "Perform initial assessment",
                            "is_note_required": True,
                            "owner": "admin",
                            "suggestions": {"actions": [], "playbooks": [], "searches": []},
                        },
                    ],
                },
            ],
        },
        {
            "id": "rp-002-uuid",
            "name": "Data Breach Response",
            "description": "Data breach handling procedure",
            "template_status": "draft",
            "incident_types": [],
            "phases": [],
        },
    ],
}

# Test data: Module Request Payloads
CREATE_RESPONSE_PLAN_PARAMS = {
    "name": "Incident Response Plan",
    "description": "Standard incident response procedure",
    "template_status": "published",
    "phases": [
        {
            "name": "Investigation",
            "tasks": [
                {
                    "name": "Initial Triage",
                    "description": "Perform initial assessment of the incident",
                    "is_note_required": True,
                    "owner": "admin",
                    "searches": [
                        {
                            "name": "Access Over Time",
                            "description": "Check access patterns",
                            "spl": "| tstats count from datamodel=Authentication by _time span=10m",
                        },
                    ],
                },
            ],
        },
        {
            "name": "Containment",
            "tasks": [
                {
                    "name": "Isolate Affected Systems",
                    "description": "Isolate compromised hosts from network",
                    "is_note_required": True,
                },
            ],
        },
    ],
}

MINIMAL_RESPONSE_PLAN_PARAMS = {
    "name": "Minimal Response Plan",
    "phases": [
        {
            "name": "Phase 1",
            "tasks": [
                {
                    "name": "Task 1",
                    "description": "First task",
                },
            ],
        },
    ],
}

UPDATE_RESPONSE_PLAN_PARAMS = {
    "name": "Incident Response Plan",
    "description": "Updated incident response procedure",
    "template_status": "published",
    "phases": [
        {
            "name": "Investigation",
            "tasks": [
                {
                    "name": "Initial Triage",
                    "description": "Updated: Perform thorough initial assessment",
                    "is_note_required": True,
                    "owner": "analyst",
                },
                {
                    "name": "New Analysis Task",
                    "description": "This task will be created",
                    "is_note_required": False,
                },
            ],
        },
        {
            "name": "Containment",
            "tasks": [
                {
                    "name": "Isolate Affected Systems",
                    "description": "Isolate compromised hosts from network",
                },
            ],
        },
    ],
}


class TestSplunkResponsePlan:
    """Test class for the splunk_response_plan action plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method.

        This creates the mock Ansible environment needed to test the action plugin:
        - task: Represents the Ansible task being executed
        - play_context: Contains playbook execution context (like check_mode)
        - connection: The connection to the target (mocked for unit tests)
        - templar: Ansible's template engine
        """
        # Create a mock Task object
        task = MagicMock(Task)
        task.check_mode = False

        # Create mock play context (controls check_mode behavior)
        play_context = MagicMock()
        play_context.check_mode = False

        # Create a mock connection
        connection = patch(
            "ansible_collections.splunk.es.plugins.module_utils.splunk.Connection",
        )

        # Ansible's template engine (not used much in these tests)
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
        self._plugin._task.action = "splunk_response_plan"
        self._plugin._task.async_val = False

        # Task variables (empty for most tests)
        self._task_vars = {}

    # Create Response Plan Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_create_success(self, connection, monkeypatch):
        """Test successful creation of a new response plan.

        When creating a response plan (name not found), the module should:
        1. Call the response templates API to create the resource
        2. Return changed=True
        3. Include the created response plan in the result
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return empty list (no existing response plans)
        def get_by_path(self, path, query_params=None):
            return {"items": []}

        # Mock create_update to return the created response plan
        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(CREATE_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert "response_plan" in result
        assert result["response_plan"]["after"] is not None
        assert result["response_plan"]["before"] is None
        assert result.get("failed") is not True
        assert "created" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_create_minimal(self, connection, monkeypatch):
        """Test creation with only required parameters.

        The module requires: name and phases for creating a new response plan.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return {
                "id": "new-rp-uuid",
                "name": "Minimal Response Plan",
                "description": "",
                "template_status": "draft",
                "phases": [
                    {
                        "id": "phase-uuid",
                        "name": "Phase 1",
                        "tasks": [
                            {
                                "id": "task-uuid",
                                "name": "Task 1",
                                "description": "First task",
                                "is_note_required": False,
                                "owner": "unassigned",
                                "suggestions": {"actions": [], "playbooks": [], "searches": []},
                            },
                        ],
                    },
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(MINIMAL_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_create_missing_name(self, connection):
        """Test that missing name returns an error.

        Name is a required field when creating a response plan.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "phases": [
                {
                    "name": "Phase 1",
                    "tasks": [{"name": "Task 1", "description": "First task"}],
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "name" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_create_missing_phases(self, connection, monkeypatch):
        """Test that missing phases returns an error when state=present.

        Phases are required when creating or updating a response plan.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Response Plan",
            "description": "A test response plan",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "phases" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_create_with_searches(self, connection, monkeypatch):
        """Test creation with searches in tasks."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(CREATE_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        # Verify searches are in the result
        after = result["response_plan"]["after"]
        assert len(after["phases"]) > 0
        assert len(after["phases"][0]["tasks"]) > 0
        assert len(after["phases"][0]["tasks"][0]["searches"]) > 0

    # Update Response Plan Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_update_success(self, connection, monkeypatch):
        """Test successful update of an existing response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return existing response plan
        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_LIST_RESPONSE)

        # Mock create_update for the update operation
        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            # Return updated response plan
            updated = copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)
            updated["description"] = "Updated incident response procedure"
            return updated

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(UPDATE_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "response_plan" in result
        # Should have both before and after states
        assert result["response_plan"]["before"] is not None
        assert result["response_plan"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_update_idempotent(self, connection, monkeypatch):
        """Test that updating with same values returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Create response plan that matches the request exactly
        existing_response = {
            "items": [
                {
                    "id": "rp-001-uuid",
                    "name": "Minimal Response Plan",
                    "description": "",
                    "template_status": "draft",
                    "phases": [
                        {
                            "id": "phase-uuid",
                            "name": "Phase 1",
                            "tasks": [
                                {
                                    "id": "task-uuid",
                                    "name": "Task 1",
                                    "description": "First task",
                                    "is_note_required": False,
                                    "owner": "unassigned",
                                    "suggestions": {
                                        "actions": [],
                                        "playbooks": [],
                                        "searches": [],
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(existing_response)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Request same values that already exist
        self._plugin._task.args = copy.deepcopy(MINIMAL_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        # No changes should be made
        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_update_preserves_ids(self, connection, monkeypatch):
        """Test that updating preserves existing phase and task IDs."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_payloads = []

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_LIST_RESPONSE)

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_payloads.append(copy.deepcopy(data))
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(UPDATE_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert len(captured_payloads) > 0

        # Verify the payload preserves IDs for matching items
        payload = captured_payloads[0]
        assert payload.get("id") == "rp-001-uuid"

    # Delete Response Plan Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_delete_success(self, connection, monkeypatch):
        """Test successful deletion of an existing response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_LIST_RESPONSE)

        delete_called = []

        def delete_by_path(self, path):
            delete_called.append(path)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "name": "Incident Response Plan",
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(delete_called) == 1
        assert "rp-001-uuid" in delete_called[0]
        assert result["response_plan"]["before"] is not None
        assert result["response_plan"]["after"] is None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_delete_not_found(self, connection, monkeypatch):
        """Test deleting a non-existent response plan returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Non-Existent Plan",
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should not be changed since it doesn't exist
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "already absent" in _get_msg_str(result) or "not found" in _get_msg_str(result)

    # Validation Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_duplicate_phase_names(self, connection, monkeypatch):
        """Test that duplicate phase names returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Plan",
            "phases": [
                {"name": "Investigation", "tasks": [{"name": "Task 1", "description": "Desc"}]},
                {"name": "Investigation", "tasks": [{"name": "Task 2", "description": "Desc"}]},
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "duplicate" in _get_msg_str(result)
        assert "phase" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_duplicate_task_names_within_phase(self, connection, monkeypatch):
        """Test that duplicate task names within a phase returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Plan",
            "phases": [
                {
                    "name": "Investigation",
                    "tasks": [
                        {"name": "Initial Triage", "description": "First triage"},
                        {"name": "Initial Triage", "description": "Duplicate triage"},
                    ],
                },
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "duplicate" in _get_msg_str(result)
        assert "task" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_same_task_names_different_phases(self, connection, monkeypatch):
        """Test that same task names in different phases is allowed."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return {
                "id": "new-uuid",
                "name": "Test Plan",
                "description": "",
                "template_status": "draft",
                "phases": [
                    {
                        "id": "p1",
                        "name": "Phase 1",
                        "tasks": [
                            {
                                "id": "t1",
                                "name": "Review",
                                "description": "",
                                "is_note_required": False,
                                "owner": "unassigned",
                                "suggestions": {"actions": [], "playbooks": [], "searches": []},
                            },
                        ],
                    },
                    {
                        "id": "p2",
                        "name": "Phase 2",
                        "tasks": [
                            {
                                "id": "t2",
                                "name": "Review",  # Same name allowed in different phase
                                "description": "",
                                "is_note_required": False,
                                "owner": "unassigned",
                                "suggestions": {"actions": [], "playbooks": [], "searches": []},
                            },
                        ],
                    },
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "name": "Test Plan",
            "phases": [
                {"name": "Phase 1", "tasks": [{"name": "Review", "description": "Phase 1 review"}]},
                {"name": "Phase 2", "tasks": [{"name": "Review", "description": "Phase 2 review"}]},
            ],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should succeed - same task name allowed in different phases
        assert result["changed"] is True
        assert result.get("failed") is not True

    # Check Mode Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_check_mode_create(self, connection, monkeypatch):
        """Test check mode for creating a response plan.

        In check mode, the module should report what would happen without
        actually making API calls. It should return changed=True but not
        create the response plan.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        # Track if create_update is called (it shouldn't be)
        create_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            create_called.append(True)
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(CREATE_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not actually call API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(create_called) == 0  # API should not be called
        assert "check mode" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_check_mode_update(self, connection, monkeypatch):
        """Test check mode for updating a response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_LIST_RESPONSE)

        update_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            update_called.append(True)
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = copy.deepcopy(UPDATE_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(update_called) == 0  # Update API should not be called
        assert "check mode" in _get_msg_str(result)
        assert result["response_plan"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_check_mode_delete(self, connection, monkeypatch):
        """Test check mode for deleting a response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_LIST_RESPONSE)

        delete_called = []

        def delete_by_path(self, path):
            delete_called.append(True)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "name": "Incident Response Plan",
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(delete_called) == 0  # Delete API should not be called
        assert "check mode" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_check_mode_no_changes(self, connection, monkeypatch):
        """Test check mode when no changes are needed."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        existing_response = {
            "items": [
                {
                    "id": "rp-001-uuid",
                    "name": "Minimal Response Plan",
                    "description": "",
                    "template_status": "draft",
                    "phases": [
                        {
                            "id": "phase-uuid",
                            "name": "Phase 1",
                            "tasks": [
                                {
                                    "id": "task-uuid",
                                    "name": "Task 1",
                                    "description": "First task",
                                    "is_note_required": False,
                                    "owner": "unassigned",
                                    "suggestions": {
                                        "actions": [],
                                        "playbooks": [],
                                        "searches": [],
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
        }

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(existing_response)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = copy.deepcopy(MINIMAL_RESPONSE_PLAN_PARAMS)

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

    # Custom API Path Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return {"items": []}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_paths.append(rest_path)
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = copy.deepcopy(CREATE_RESPONSE_PLAN_PARAMS)
        params["api_namespace"] = "customNS"
        params["api_user"] = "customuser"
        params["api_app"] = "CustomApp"

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        # Verify the custom path was used
        assert len(captured_paths) > 0
        assert "customNS" in captured_paths[-1]
        assert "customuser" in captured_paths[-1]
        assert "CustomApp" in captured_paths[-1]

    # Template Status Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_draft_status(self, connection, monkeypatch):
        """Test creating a response plan with draft status."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_payloads = []

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_payloads.append(copy.deepcopy(data))
            response = copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)
            response["template_status"] = "draft"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = copy.deepcopy(MINIMAL_RESPONSE_PLAN_PARAMS)
        params["template_status"] = "draft"

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert len(captured_payloads) > 0
        assert captured_payloads[0]["template_status"] == "draft"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_published_status(self, connection, monkeypatch):
        """Test creating a response plan with published status."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_payloads = []

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_payloads.append(copy.deepcopy(data))
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = copy.deepcopy(CREATE_RESPONSE_PLAN_PARAMS)
        params["template_status"] = "published"

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert len(captured_payloads) > 0
        assert captured_payloads[0]["template_status"] == "published"


class TestResponsePlanUtilityFunctions:
    """Tests for the utility functions in the response plan action plugin.

    These functions handle API path building and data transformations.
    """

    # API Path Building Tests
    def test_build_response_plan_api_path_defaults(self):
        """Test that default API path is constructed correctly."""
        result = _build_response_plan_api_path()

        assert result == "servicesNS/nobody/missioncontrol/v1/responsetemplates"

    def test_build_response_plan_api_path_custom_namespace(self):
        """Test API path with custom namespace value."""
        result = _build_response_plan_api_path(namespace="customNS")

        assert result == "customNS/nobody/missioncontrol/v1/responsetemplates"

    def test_build_response_plan_api_path_custom_user(self):
        """Test API path with custom user value."""
        result = _build_response_plan_api_path(user="admin")

        assert result == "servicesNS/admin/missioncontrol/v1/responsetemplates"

    def test_build_response_plan_api_path_custom_app(self):
        """Test API path with custom app value."""
        result = _build_response_plan_api_path(app="CustomApp")

        assert result == "servicesNS/nobody/CustomApp/v1/responsetemplates"

    def test_build_response_plan_api_path_all_custom(self):
        """Test API path with all custom values."""
        result = _build_response_plan_api_path(
            namespace="myNS",
            user="myuser",
            app="MyApp",
        )

        assert result == "myNS/myuser/MyApp/v1/responsetemplates"

    def test_build_response_plan_update_path(self):
        """Test update API path includes ref_id."""
        result = _build_response_plan_update_path("rp-001-uuid")

        assert "rp-001-uuid" in result
        assert result.endswith("/rp-001-uuid")

    def test_build_response_plan_update_path_custom_params(self):
        """Test update API path with custom namespace/user/app."""
        result = _build_response_plan_update_path(
            "rp-001-uuid",
            namespace="customNS",
            user="customuser",
            app="CustomApp",
        )

        assert "customNS" in result
        assert "customuser" in result
        assert "CustomApp" in result
        assert "rp-001-uuid" in result

    # Task ID Lookup Tests
    def test_find_task_id_by_name_found(self):
        """Test finding existing task ID by name."""
        existing_tasks = [
            {"id": "task-001", "name": "Initial Triage"},
            {"id": "task-002", "name": "Gather Evidence"},
        ]

        result = _find_task_id_by_name(existing_tasks, "Initial Triage")

        assert result == "task-001"

    def test_find_task_id_by_name_not_found(self):
        """Test that non-existent task returns None."""
        existing_tasks = [
            {"id": "task-001", "name": "Initial Triage"},
        ]

        result = _find_task_id_by_name(existing_tasks, "Non-Existent")

        assert result is None

    def test_find_task_id_by_name_empty_list(self):
        """Test that empty task list returns None."""
        result = _find_task_id_by_name([], "Any Task")

        assert result is None

    # Search Payload Building Tests
    def test_build_search_payload_complete(self):
        """Test building search payload with all fields."""
        search = {
            "name": "Access Over Time",
            "description": "Check access patterns",
            "spl": "| tstats count from datamodel=Authentication",
        }

        result = _build_search_payload(search)

        assert result["name"] == "Access Over Time"
        assert result["description"] == "Check access patterns"
        assert result["spl"] == "| tstats count from datamodel=Authentication"

    def test_build_search_payload_minimal(self):
        """Test building search payload with minimal fields."""
        search = {"name": "Search", "spl": "index=main"}

        result = _build_search_payload(search)

        assert result["name"] == "Search"
        assert result["spl"] == "index=main"
        assert result["description"] == ""  # Default empty string

    def test_build_search_payload_empty(self):
        """Test building search payload from empty dict."""
        result = _build_search_payload({})

        assert result["name"] == ""
        assert result["description"] == ""
        assert result["spl"] == ""

    # Task Payload Building Tests
    def test_build_task_payload_new_task(self):
        """Test building payload for a new task."""
        task = {
            "name": "Initial Triage",
            "description": "Perform initial assessment",
            "is_note_required": True,
            "owner": "admin",
        }

        result = _build_task_payload(task, order=1, existing_id=None)

        assert result["name"] == "Initial Triage"
        assert result["description"] == "Perform initial assessment"
        assert result["is_note_required"] is True
        assert result["owner"] == "admin"
        assert result["order"] == 1
        assert result["isNewTask"] is True
        assert result["id"] is not None  # Should have generated UUID

    def test_build_task_payload_existing_task(self):
        """Test building payload for an existing task preserves ID."""
        task = {
            "name": "Initial Triage",
            "description": "Updated description",
        }

        result = _build_task_payload(task, order=2, existing_id="existing-task-uuid")

        assert result["id"] == "existing-task-uuid"
        assert result["isNewTask"] is False
        assert result["order"] == 2

    def test_build_task_payload_with_searches(self):
        """Test building task payload with searches."""
        task = {
            "name": "Analysis Task",
            "description": "Run analysis",
            "searches": [
                {"name": "Search 1", "spl": "index=main"},
                {"name": "Search 2", "spl": "index=security"},
            ],
        }

        result = _build_task_payload(task, order=1)

        assert len(result["suggestions"]["searches"]) == 2
        assert result["suggestions"]["searches"][0]["name"] == "Search 1"
        assert result["suggestions"]["searches"][1]["name"] == "Search 2"

    def test_build_task_payload_defaults(self):
        """Test that task payload uses correct defaults."""
        task = {"name": "Minimal Task"}

        result = _build_task_payload(task, order=1)

        assert result["is_note_required"] is False
        assert result["owner"] == "unassigned"
        assert result["status"] == "Pending"
        assert result["sla"] is None
        assert result["sla_type"] == "minutes"
        assert result["files"] == []
        assert result["notes"] == []

    # Phase Payload Building Tests
    def test_build_phase_payload_new_phase(self):
        """Test building payload for a new phase."""
        phase = {
            "name": "Investigation",
            "tasks": [
                {"name": "Task 1", "description": "First task"},
            ],
        }

        result = _build_phase_payload(phase, order=1, existing_phase=None)

        assert result["name"] == "Investigation"
        assert result["order"] == 1
        assert len(result["tasks"]) == 1
        assert result["id"] is not None  # Should have generated UUID

    def test_build_phase_payload_existing_phase(self):
        """Test building payload for an existing phase preserves ID."""
        phase = {
            "name": "Investigation",
            "tasks": [],
        }
        existing_phase = {
            "id": "existing-phase-uuid",
            "name": "Investigation",
            "tasks": [],
        }

        result = _build_phase_payload(phase, order=1, existing_phase=existing_phase)

        assert result["id"] == "existing-phase-uuid"

    def test_build_phase_payload_with_existing_tasks(self):
        """Test that existing task IDs are preserved during phase build."""
        phase = {
            "name": "Investigation",
            "tasks": [
                {"name": "Initial Triage", "description": "Updated"},
                {"name": "New Task", "description": "Brand new"},
            ],
        }
        existing_phase = {
            "id": "phase-uuid",
            "name": "Investigation",
            "tasks": [
                {"id": "existing-task-uuid", "name": "Initial Triage"},
            ],
        }

        result = _build_phase_payload(phase, order=1, existing_phase=existing_phase)

        # First task should keep existing ID
        assert result["tasks"][0]["id"] == "existing-task-uuid"
        assert result["tasks"][0]["isNewTask"] is False
        # Second task should be new
        assert result["tasks"][1]["isNewTask"] is True

    # Response Plan to API Mapping Tests
    def test_map_response_plan_to_api_create(self):
        """Test mapping response plan for creation (no existing data)."""
        response_plan = {
            "name": "Test Plan",
            "description": "A test plan",
            "template_status": "draft",
            "phases": [
                {
                    "name": "Phase 1",
                    "tasks": [{"name": "Task 1", "description": "Desc"}],
                },
            ],
        }

        result = _map_response_plan_to_api(response_plan)

        assert result["name"] == "Test Plan"
        assert result["description"] == "A test plan"
        assert result["template_status"] == "draft"
        assert result["incident_types"] == []
        assert len(result["phases"]) == 1
        assert "id" not in result  # No ID for new plan

    def test_map_response_plan_to_api_update(self):
        """Test mapping response plan for update (with existing data)."""
        response_plan = {
            "name": "Test Plan",
            "description": "Updated description",
            "phases": [],
        }
        existing = {
            "id": "existing-plan-uuid",
            "name": "Test Plan",
            "phases": [],
        }

        result = _map_response_plan_to_api(response_plan, existing)

        assert result["id"] == "existing-plan-uuid"

    # API to Response Plan Mapping Tests
    def test_map_task_from_api(self):
        """Test mapping task from API format to module format."""
        api_task = {
            "id": "task-uuid",
            "name": "Initial Triage",
            "description": "Perform triage",
            "is_note_required": True,
            "owner": "admin",
            "suggestions": {
                "actions": [],
                "playbooks": [],
                "searches": [
                    {"name": "Search 1", "description": "Desc", "spl": "index=main"},
                ],
            },
        }

        result = _map_task_from_api(api_task)

        assert result["name"] == "Initial Triage"
        assert result["description"] == "Perform triage"
        assert result["is_note_required"] is True
        assert result["owner"] == "admin"
        assert len(result["searches"]) == 1
        assert result["searches"][0]["name"] == "Search 1"

    def test_map_task_from_api_defaults(self):
        """Test mapping task with missing optional fields."""
        api_task = {"name": "Minimal Task"}

        result = _map_task_from_api(api_task)

        assert result["name"] == "Minimal Task"
        assert result["description"] == ""
        assert result["is_note_required"] is False
        assert result["owner"] == "unassigned"
        assert result["searches"] == []

    def test_map_phase_from_api(self):
        """Test mapping phase from API format to module format."""
        api_phase = {
            "id": "phase-uuid",
            "name": "Investigation",
            "tasks": [
                {
                    "name": "Task 1",
                    "description": "Desc",
                    "is_note_required": False,
                    "owner": "admin",
                    "suggestions": {"actions": [], "playbooks": [], "searches": []},
                },
            ],
        }

        result = _map_phase_from_api(api_phase)

        assert result["name"] == "Investigation"
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["name"] == "Task 1"

    def test_map_response_plan_from_api_complete(self):
        """Test mapping complete response plan from API format."""
        api_response = copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        result = _map_response_plan_from_api(api_response)

        assert result["name"] == "Incident Response Plan"
        assert result["description"] == "Standard incident response procedure"
        assert result["template_status"] == "published"
        assert len(result["phases"]) == 2
        assert result["phases"][0]["name"] == "Investigation"
        assert result["phases"][1]["name"] == "Containment"

    def test_map_response_plan_from_api_empty(self):
        """Test mapping empty response plan from API format."""
        result = _map_response_plan_from_api({})

        assert result["name"] == ""
        assert result["description"] == ""
        assert result["template_status"] == "draft"
        assert result["phases"] == []

    def test_map_response_plan_from_api_with_searches(self):
        """Test that searches are correctly extracted from tasks."""
        api_response = copy.deepcopy(RESPONSE_PLAN_API_RESPONSE)

        result = _map_response_plan_from_api(api_response)

        # First phase, first task should have searches
        task = result["phases"][0]["tasks"][0]
        assert len(task["searches"]) == 1
        assert task["searches"][0]["name"] == "Access Over Time"
        assert task["searches"][0]["spl"].startswith("| tstats")
