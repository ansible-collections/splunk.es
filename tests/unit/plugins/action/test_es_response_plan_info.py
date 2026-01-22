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
Unit tests for the splunk_response_plan_info action plugin.
"""


import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_response_plan_info import (
    ActionModule,
    _build_response_plan_api_path,
    _map_phase_info_from_api,
    _map_response_plan_info_from_api,
    _map_task_info_from_api,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


# Test data: API Response Payloads
# These represent what the Splunk API returns for response plans queries.

RESPONSE_PLAN_API_RESPONSE_SINGLE = {
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
    ],
}

RESPONSE_PLAN_API_RESPONSE_LIST = {
    "items": [
        {
            "id": "rp-001-uuid",
            "name": "Incident Response Plan",
            "description": "Standard incident response procedure",
            "template_status": "published",
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
                            "suggestions": {
                                "actions": [],
                                "playbooks": [],
                                "searches": [
                                    {
                                        "name": "Access Search",
                                        "description": "Check access",
                                        "spl": "index=access",
                                    },
                                ],
                            },
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
            "phases": [
                {
                    "id": "phase-002-uuid",
                    "name": "Identification",
                    "tasks": [
                        {
                            "id": "task-002-uuid",
                            "name": "Identify Scope",
                            "description": "Determine breach scope",
                            "is_note_required": False,
                            "owner": "unassigned",
                            "suggestions": {"actions": [], "playbooks": [], "searches": []},
                        },
                    ],
                },
            ],
        },
        {
            "id": "rp-003-uuid",
            "name": "Incident Response Plan",
            "description": "Another plan with same name",
            "template_status": "draft",
            "phases": [],
        },
    ],
}

EMPTY_RESPONSE_PLANS = {
    "items": [],
}


class TestSplunkResponsePlanInfo:
    """Test class for the splunk_response_plan_info action plugin.

    The splunk_response_plan_info module is a "read-only" info module that queries
    Splunk for response plans without making changes. It should always return
    changed=False.

    Query modes:
    1. By name: Returns response plans matching the exact name
    2. All: Returns all response plans (when no filters provided)
    """

    def setup_method(self):
        """Set up test fixtures before each test method.

        Creates mock Ansible components needed to test the action plugin.
        """
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
        self._plugin._task.action = "splunk_response_plan_info"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Query All Response Plans Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_all(self, connection, monkeypatch):
        """Test querying all response plans without filters.

        When no name is provided, should return all response plans.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "response_plans" in result
        assert len(result["response_plans"]) == 3

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_all_empty(self, connection, monkeypatch):
        """Test querying all response plans when none exist.

        Should return an empty list without error.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_RESPONSE_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["response_plans"]) == 0

    # Query by Name Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_by_name(self, connection, monkeypatch):
        """Test querying response plans by name.

        When name is provided, the module should fetch all response plans and
        filter by exact name match.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Data Breach Response",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "response_plans" in result
        # Should return 1 response plan with matching name
        assert len(result["response_plans"]) == 1
        assert result["response_plans"][0]["name"] == "Data Breach Response"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_by_name_multiple_matches(self, connection, monkeypatch):
        """Test querying by name with multiple matches.

        When multiple response plans have the same name, all should be returned.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Incident Response Plan",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        # Should return both response plans with matching name
        assert len(result["response_plans"]) == 2
        for plan in result["response_plans"]:
            assert plan["name"] == "Incident Response Plan"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_by_name_no_match(self, connection, monkeypatch):
        """Test querying by name with no matches.

        When no response plans match the name, should return an empty list.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Non-Existent Plan",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["response_plans"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_by_name_exact_match(self, connection, monkeypatch):
        """Test that name filtering uses exact match.

        "Incident" should not match "Incident Response Plan".
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Partial name should not match
        self._plugin._task.args = {
            "name": "Incident",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["response_plans"]) == 0  # No exact match

    # Always Changed=False Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_always_changed_false(self, connection, monkeypatch):
        """Verify that info module always returns changed=False.

        Info modules are read-only and should never report changes.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Test with various query types
        test_cases = [
            {},  # All response plans
            {"name": "Incident Response Plan"},  # By name
            {"name": "Non-Existent"},  # No match
        ]

        for args in test_cases:
            self._plugin._task.args = args
            result = self._plugin.run(task_vars=self._task_vars)
            assert result["changed"] is False, f"Expected changed=False for args: {args}"

    # Custom API Path Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
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

    # Field Mapping Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_field_mapping(self, connection, monkeypatch):
        """Test that API fields are correctly mapped to module format.

        Verify that all fields including IDs are present in the result.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Data Breach Response",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        plan = result["response_plans"][0]

        # Verify all expected fields are present
        assert "id" in plan
        assert "name" in plan
        assert "description" in plan
        assert "template_status" in plan
        assert "phases" in plan

        # Verify phase fields
        assert len(plan["phases"]) > 0
        phase = plan["phases"][0]
        assert "id" in phase
        assert "name" in phase
        assert "tasks" in phase

        # Verify task fields
        assert len(phase["tasks"]) > 0
        task = phase["tasks"][0]
        assert "id" in task
        assert "name" in task
        assert "description" in task
        assert "is_note_required" in task
        assert "owner" in task
        assert "searches" in task

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_searches_mapped(self, connection, monkeypatch):
        """Test that searches are correctly mapped in tasks."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Incident Response Plan",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # First matching plan should have searches
        plan = result["response_plans"][0]
        task = plan["phases"][0]["tasks"][0]

        assert len(task["searches"]) == 1
        search = task["searches"][0]
        assert "name" in search
        assert "description" in search
        assert "spl" in search

    # Error Handling Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_handles_null_items(self, connection, monkeypatch):
        """Test handling of null items in API response.

        The API might return None values in the items list; these should
        be filtered out.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "items": [
                    None,  # Null item
                    copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST["items"][0]),
                    None,  # Another null
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        # Should only have 1 valid response plan (nulls filtered)
        assert len(result["response_plans"]) == 1

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_handles_empty_response(self, connection, monkeypatch):
        """Test handling of empty API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {}  # Empty response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["response_plans"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_handles_no_items_key(self, connection, monkeypatch):
        """Test handling of API response without items key."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"other_key": "value"}  # No items key

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["response_plans"]) == 0

    # Check Mode Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_response_plan_info_check_mode(self, connection, monkeypatch):
        """Test that check mode works correctly for info module.

        Info modules should behave the same in check mode (read-only anyway).
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        # Should behave normally in check mode
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["response_plans"]) == 3


class TestResponsePlanInfoUtilityFunctions:
    """Tests for the utility functions in the response plan info action plugin.

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

    # Task Info Mapping Tests
    def test_map_task_info_from_api_complete(self):
        """Test mapping task from API format includes all fields."""
        api_task = {
            "id": "task-001-uuid",
            "name": "Initial Triage",
            "description": "Perform initial assessment",
            "is_note_required": True,
            "owner": "admin",
            "suggestions": {
                "actions": [],
                "playbooks": [],
                "searches": [
                    {
                        "name": "Access Search",
                        "description": "Check access patterns",
                        "spl": "| tstats count from datamodel=Authentication",
                    },
                ],
            },
        }

        result = _map_task_info_from_api(api_task)

        assert result["id"] == "task-001-uuid"
        assert result["name"] == "Initial Triage"
        assert result["description"] == "Perform initial assessment"
        assert result["is_note_required"] is True
        assert result["owner"] == "admin"
        assert len(result["searches"]) == 1
        assert result["searches"][0]["name"] == "Access Search"
        assert result["searches"][0]["spl"].startswith("| tstats")

    def test_map_task_info_from_api_minimal(self):
        """Test mapping task with minimal fields."""
        api_task = {"name": "Minimal Task"}

        result = _map_task_info_from_api(api_task)

        assert result["id"] == ""
        assert result["name"] == "Minimal Task"
        assert result["description"] == ""
        assert result["is_note_required"] is False
        assert result["owner"] == "unassigned"
        assert result["searches"] == []

    def test_map_task_info_from_api_empty_suggestions(self):
        """Test mapping task with empty suggestions."""
        api_task = {
            "id": "task-uuid",
            "name": "Task",
            "suggestions": {},
        }

        result = _map_task_info_from_api(api_task)

        assert result["searches"] == []

    def test_map_task_info_from_api_null_suggestions(self):
        """Test mapping task with null suggestions."""
        api_task = {
            "id": "task-uuid",
            "name": "Task",
            "suggestions": None,
        }

        result = _map_task_info_from_api(api_task)

        assert result["searches"] == []

    # Phase Info Mapping Tests
    def test_map_phase_info_from_api_complete(self):
        """Test mapping phase from API format includes ID."""
        api_phase = {
            "id": "phase-001-uuid",
            "name": "Investigation",
            "tasks": [
                {
                    "id": "task-001-uuid",
                    "name": "Initial Triage",
                    "description": "Triage the incident",
                    "is_note_required": False,
                    "owner": "admin",
                    "suggestions": {"actions": [], "playbooks": [], "searches": []},
                },
            ],
        }

        result = _map_phase_info_from_api(api_phase)

        assert result["id"] == "phase-001-uuid"
        assert result["name"] == "Investigation"
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["id"] == "task-001-uuid"
        assert result["tasks"][0]["name"] == "Initial Triage"

    def test_map_phase_info_from_api_empty_tasks(self):
        """Test mapping phase with no tasks."""
        api_phase = {
            "id": "phase-uuid",
            "name": "Empty Phase",
            "tasks": [],
        }

        result = _map_phase_info_from_api(api_phase)

        assert result["id"] == "phase-uuid"
        assert result["name"] == "Empty Phase"
        assert result["tasks"] == []

    def test_map_phase_info_from_api_null_tasks(self):
        """Test mapping phase with null tasks."""
        api_phase = {
            "id": "phase-uuid",
            "name": "Phase",
            "tasks": None,
        }

        result = _map_phase_info_from_api(api_phase)

        assert result["tasks"] == []

    # Response Plan Info Mapping Tests
    def test_map_response_plan_info_from_api_complete(self):
        """Test mapping complete response plan includes all IDs."""
        api_response = copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_SINGLE)

        result = _map_response_plan_info_from_api(api_response)

        assert result["id"] == "rp-001-uuid"
        assert result["name"] == "Incident Response Plan"
        assert result["description"] == "Standard incident response procedure"
        assert result["template_status"] == "published"
        assert len(result["phases"]) == 1
        assert result["phases"][0]["id"] == "phase-001-uuid"
        assert result["phases"][0]["name"] == "Investigation"
        assert result["phases"][0]["tasks"][0]["id"] == "task-001-uuid"

    def test_map_response_plan_info_from_api_empty(self):
        """Test mapping empty response plan from API format."""
        result = _map_response_plan_info_from_api({})

        assert result["id"] == ""
        assert result["name"] == ""
        assert result["description"] == ""
        assert result["template_status"] == "draft"
        assert result["phases"] == []

    def test_map_response_plan_info_from_api_null_phases(self):
        """Test mapping response plan with null phases."""
        api_response = {
            "id": "rp-uuid",
            "name": "Plan",
            "phases": None,
        }

        result = _map_response_plan_info_from_api(api_response)

        assert result["phases"] == []

    def test_map_response_plan_info_from_api_with_searches(self):
        """Test that searches are correctly extracted and mapped."""
        api_response = copy.deepcopy(RESPONSE_PLAN_API_RESPONSE_SINGLE)

        result = _map_response_plan_info_from_api(api_response)

        task = result["phases"][0]["tasks"][0]
        assert len(task["searches"]) == 1
        assert task["searches"][0]["name"] == "Access Over Time"
        assert task["searches"][0]["description"] == "Check access patterns"
        assert "| tstats" in task["searches"][0]["spl"]

    def test_map_response_plan_info_from_api_defaults(self):
        """Test that defaults are applied for missing optional fields."""
        api_response = {
            "id": "rp-uuid",
            "name": "Test Plan",
            # Missing description and template_status
            "phases": [],
        }

        result = _map_response_plan_info_from_api(api_response)

        assert result["description"] == ""
        assert result["template_status"] == "draft"
