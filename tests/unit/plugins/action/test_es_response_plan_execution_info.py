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
Unit tests for the splunk_response_plan_execution_info action plugin.
"""


import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_response_plan_execution_info import (
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
# Investigation with no applied response plans
INVESTIGATION_NO_PLANS = {
    "id": "investigation-001-uuid",
    "name": "Test Investigation",
    "status": "1",
    "response_plans": [],
}

# Investigation with a single applied response plan
INVESTIGATION_WITH_ONE_PLAN = {
    "id": "investigation-001-uuid",
    "name": "Test Investigation",
    "status": "1",
    "response_plans": [
        {
            "id": "applied-plan-001-uuid",
            "name": "Incident Response Plan",
            "description": "Standard incident response procedure",
            "template_id": "template-001-uuid",
            "phases": [
                {
                    "id": "phase-001-uuid",
                    "name": "Investigation",
                    "tasks": [
                        {
                            "id": "task-001-uuid",
                            "name": "Initial Triage",
                            "description": "Perform initial assessment",
                            "status": "Pending",
                            "owner": "admin",
                            "is_note_required": True,
                        },
                        {
                            "id": "task-002-uuid",
                            "name": "Gather Evidence",
                            "description": "Collect relevant logs",
                            "status": "Started",
                            "owner": "analyst",
                            "is_note_required": False,
                        },
                    ],
                },
                {
                    "id": "phase-002-uuid",
                    "name": "Containment",
                    "tasks": [
                        {
                            "id": "task-003-uuid",
                            "name": "Isolate Systems",
                            "description": "Isolate affected systems",
                            "status": "Pending",
                            "owner": "unassigned",
                            "is_note_required": False,
                        },
                    ],
                },
            ],
        },
    ],
}

# Investigation with multiple applied response plans
INVESTIGATION_WITH_MULTIPLE_PLANS = {
    "id": "investigation-001-uuid",
    "name": "Test Investigation",
    "status": "1",
    "response_plans": [
        {
            "id": "applied-plan-001-uuid",
            "name": "Incident Response Plan",
            "description": "Standard incident response",
            "template_id": "template-001-uuid",
            "phases": [
                {
                    "id": "phase-001-uuid",
                    "name": "Investigation",
                    "tasks": [
                        {
                            "id": "task-001-uuid",
                            "name": "Initial Triage",
                            "description": "Perform assessment",
                            "status": "Ended",
                            "owner": "admin",
                            "is_note_required": True,
                        },
                    ],
                },
            ],
        },
        {
            "id": "applied-plan-002-uuid",
            "name": "Data Breach Response",
            "description": "Data breach handling",
            "template_id": "template-002-uuid",
            "phases": [
                {
                    "id": "phase-002-uuid",
                    "name": "Identification",
                    "tasks": [
                        {
                            "id": "task-002-uuid",
                            "name": "Identify Scope",
                            "description": "Determine breach scope",
                            "status": "Started",
                            "owner": "analyst",
                            "is_note_required": False,
                        },
                    ],
                },
            ],
        },
    ],
}

# Investigation with URL-encoded data in response
INVESTIGATION_WITH_ENCODED_DATA = {
    "id": "investigation-001-uuid",
    "name": "Test Investigation",
    "status": "1",
    "response_plans": [
        {
            "id": "applied-plan-001-uuid",
            "name": "Incident%20Response%20Plan",
            "description": "Standard%20incident%20response",
            "template_id": "template-001-uuid",
            "phases": [
                {
                    "id": "phase-001-uuid",
                    "name": "phase%201",
                    "tasks": [
                        {
                            "id": "task-001-uuid",
                            "name": "task%201",
                            "description": "task%201%20description",
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


class TestSplunkResponsePlanExecutionInfo:
    """Test class for the splunk_response_plan_execution_info action plugin."""

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
        self._plugin._task.action = "splunk_response_plan_execution_info"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Query Applied Response Plans Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_no_applied_plans(self, connection, monkeypatch):
        """Test querying an investigation with no applied response plans."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_NO_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "applied_response_plans" in result
        assert len(result["applied_response_plans"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_single_applied_plan(self, connection, monkeypatch):
        """Test querying an investigation with a single applied response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_ONE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 1

        plan = result["applied_response_plans"][0]
        assert plan["id"] == "applied-plan-001-uuid"
        assert plan["name"] == "Incident Response Plan"
        assert len(plan["phases"]) == 2

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_multiple_applied_plans(self, connection, monkeypatch):
        """Test querying an investigation with multiple applied response plans."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_MULTIPLE_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 2

        # Verify first plan
        plan1 = result["applied_response_plans"][0]
        assert plan1["name"] == "Incident Response Plan"

        # Verify second plan
        plan2 = result["applied_response_plans"][1]
        assert plan2["name"] == "Data Breach Response"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_field_mapping(self, connection, monkeypatch):
        """Test that all fields are correctly mapped from API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_ONE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        plan = result["applied_response_plans"][0]

        # Verify plan-level fields
        assert "id" in plan
        assert "name" in plan
        assert "description" in plan
        assert "source_template_id" in plan
        assert "phases" in plan

        # Verify phase-level fields
        phase = plan["phases"][0]
        assert "id" in phase
        assert "name" in phase
        assert "tasks" in phase

        # Verify task-level fields
        task = phase["tasks"][0]
        assert "id" in task
        assert "name" in task
        assert "description" in task
        assert "status" in task
        assert "owner" in task
        assert "is_note_required" in task

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_task_status_mapping(self, connection, monkeypatch):
        """Test that task statuses are correctly mapped from API format."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_ONE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        plan = result["applied_response_plans"][0]
        tasks = plan["phases"][0]["tasks"]

        # API returns "Pending" -> module returns "pending"
        assert tasks[0]["status"] == "pending"
        # API returns "Started" -> module returns "started"
        assert tasks[1]["status"] == "started"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_url_decoding(self, connection, monkeypatch):
        """Test that URL-encoded strings are properly decoded."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_ENCODED_DATA)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        plan = result["applied_response_plans"][0]

        # Verify URL-encoded strings are decoded
        assert plan["name"] == "Incident Response Plan"
        assert plan["description"] == "Standard incident response"
        assert plan["phases"][0]["name"] == "phase 1"
        assert plan["phases"][0]["tasks"][0]["name"] == "task 1"
        assert plan["phases"][0]["tasks"][0]["description"] == "task 1 description"

    # Always Changed=False Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_always_changed_false(self, connection, monkeypatch):
        """Test that info module always returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        test_responses = [
            INVESTIGATION_NO_PLANS,
            INVESTIGATION_WITH_ONE_PLAN,
            INVESTIGATION_WITH_MULTIPLE_PLANS,
        ]

        for response in test_responses:

            def get_by_path(self, path, query_params=None):
                return copy.deepcopy(response)

            monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

            self._plugin._task.args = {
                "investigation_ref_id": "investigation-001-uuid",
            }

            result = self._plugin.run(task_vars=self._task_vars)

            assert result["changed"] is False

    # Validation Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_missing_investigation_ref_id(self, connection):
        """Test that missing investigation_ref_id returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "investigation_ref_id" in _get_msg_str(result)

    # Check Mode Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_check_mode(self, connection, monkeypatch):
        """Test that check mode works correctly for info module.

        Info modules should behave the same in check mode (read-only anyway).
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_ONE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should behave normally in check mode
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 1

    # Custom API Path Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return copy.deepcopy(INVESTIGATION_NO_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
            "api_namespace": "customNS",
            "api_user": "customuser",
            "api_app": "CustomApp",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

        # Verify custom path was used
        assert len(captured_paths) > 0
        assert "customNS" in captured_paths[0]
        assert "customuser" in captured_paths[0]
        assert "CustomApp" in captured_paths[0]

    # Empty/Null Response Handling Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_empty_response(self, connection, monkeypatch):
        """Test handling of empty API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_null_response_plans(self, connection, monkeypatch):
        """Test handling of null response_plans in API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "id": "investigation-001-uuid",
                "response_plans": None,
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_null_phases_in_plan(self, connection, monkeypatch):
        """Test handling of null phases in a response plan."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "id": "investigation-001-uuid",
                "response_plans": [
                    {
                        "id": "plan-001-uuid",
                        "name": "Test Plan",
                        "phases": None,
                    },
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 1
        assert result["applied_response_plans"][0]["phases"] == []

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_null_tasks_in_phase(self, connection, monkeypatch):
        """Test handling of null tasks in a phase."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "id": "investigation-001-uuid",
                "response_plans": [
                    {
                        "id": "plan-001-uuid",
                        "name": "Test Plan",
                        "phases": [
                            {
                                "id": "phase-001-uuid",
                                "name": "Phase 1",
                                "tasks": None,
                            },
                        ],
                    },
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["applied_response_plans"]) == 1
        assert result["applied_response_plans"][0]["phases"][0]["tasks"] == []

    # Source Template ID Mapping Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_source_template_id_from_template_id(self, connection, monkeypatch):
        """Test that template_id from GET response is mapped to source_template_id."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_WITH_ONE_PLAN)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        plan = result["applied_response_plans"][0]
        assert plan["source_template_id"] == "template-001-uuid"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_info_source_template_id_from_source_template_id(self, connection, monkeypatch):
        """Test that source_template_id from POST response is correctly preserved."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # API response with source_template_id (POST response format)
        investigation_with_source_id = {
            "id": "investigation-001-uuid",
            "response_plans": [
                {
                    "id": "plan-001-uuid",
                    "name": "Test Plan",
                    "source_template_id": "source-template-uuid",
                    "phases": [],
                },
            ],
        }

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(investigation_with_source_id)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "investigation-001-uuid",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        plan = result["applied_response_plans"][0]
        assert plan["source_template_id"] == "source-template-uuid"


class TestResponsePlanExecutionInfoHelperMethods:
    """Tests for the helper methods in the response plan execution info action plugin."""

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

        self._plugin._task.action = "splunk_response_plan_execution_info"
        self._plugin._task.async_val = False

    def test_api_config_defaults(self):
        """Test that default API configuration is set correctly."""
        assert self._plugin.api_namespace == "servicesNS"
        assert self._plugin.api_user == "nobody"
        assert self._plugin.api_app == "missioncontrol"
