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
Unit tests for the splunk_investigation_info action plugin.

These tests verify that the splunk_investigation_info action plugin works correctly for:
- Querying a specific investigation by investigation_ref_id
- Querying investigations by name (with filtering)
- Querying all investigations
- Handling time range parameters (create_time_min/create_time_max)
- Handling not found scenarios

The tests use mocking to simulate Splunk API responses.
"""

import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_investigation_info import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


# Test data: API Response Payloads
# These represent what the Splunk API returns for investigation queries.

INVESTIGATION_API_RESPONSE_SINGLE = {
    "investigation_guid": "inv-12345-abcde",
    "name": "Security Incident 2026-01",
    "description": "Investigation into suspicious login activity",
    "owner": "admin",
    "status": "1",
    "urgency": "high",
    "disposition": "disposition:6",
    "sensitivity": "Amber",
    "consolidated_findings": {
        "event_id": ["finding-001@@notable@@time123"],
    },
}

INVESTIGATION_API_RESPONSE_LIST = [
    {
        "investigation_guid": "inv-001-aaaaa",
        "name": "Security Incident 2026-01",
        "description": "Investigation into suspicious login activity",
        "owner": "admin",
        "status": "1",
        "urgency": "high",
        "disposition": "disposition:6",
        "sensitivity": "Amber",
    },
    {
        "investigation_guid": "inv-002-bbbbb",
        "name": "Malware Investigation",
        "description": "Potential malware detected",
        "owner": "analyst",
        "status": "2",
        "urgency": "critical",
        "disposition": "disposition:1",
        "sensitivity": "Red",
    },
    {
        "investigation_guid": "inv-003-ccccc",
        "name": "Security Incident 2026-01",
        "description": "Another investigation with same name",
        "owner": "admin",
        "status": "1",
        "urgency": "medium",
        "disposition": "disposition:6",
        "sensitivity": "Green",
    },
]

EMPTY_INVESTIGATIONS_RESPONSE = []


class TestSplunkInvestigationInfo:
    """Test class for the splunk_investigation_info action plugin.

    The splunk_investigation_info module is a "read-only" info module that queries
    Splunk for investigations without making changes. It should always return
    changed=False.

    Query modes:
    1. By investigation_ref_id: Returns a single specific investigation
    2. By name: Returns all investigations matching the exact name
    3. All: Returns all investigations (when no filters provided)
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
        self._plugin._task.action = "splunk_investigation_info"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Query by investigation_ref_id Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_by_ref_id(self, connection, monkeypatch):
        """Test querying a specific investigation by investigation_ref_id.

        When investigation_ref_id is provided, the module should query for that
        specific investigation and return it in a list (for consistency).
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            # When querying by ref_id, API returns a list with one item
            if query_params and query_params.get("ids") == "inv-12345-abcde":
                return [copy.deepcopy(INVESTIGATION_API_RESPONSE_SINGLE)]
            return []

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Info modules should always return changed=False
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigations" in result
        assert len(result["investigations"]) == 1
        assert result["investigations"][0]["name"] == "Security Incident 2026-01"
        assert result["investigations"][0]["investigation_ref_id"] == "inv-12345-abcde"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_by_ref_id_not_found(self, connection, monkeypatch):
        """Test querying a non-existent investigation by investigation_ref_id.

        When the investigation doesn't exist, the module should return an empty
        list rather than failing.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return []  # Empty response = not found

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "non-existent-id",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigations" in result
        assert len(result["investigations"]) == 0

    # Query by Name Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_by_name(self, connection, monkeypatch):
        """Test querying investigations by name.

        When name is provided, the module should fetch all investigations and
        filter by exact name match.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Security Incident 2026-01",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigations" in result
        # Should return 2 investigations with matching name (items 0 and 2)
        assert len(result["investigations"]) == 2
        for investigation in result["investigations"]:
            assert investigation["name"] == "Security Incident 2026-01"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_by_name_no_match(self, connection, monkeypatch):
        """Test querying by name with no matches.

        When no investigations match the name, should return an empty list.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Non-Existent Investigation Name",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["investigations"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_by_name_exact_match(self, connection, monkeypatch):
        """Test that name filtering uses exact match.

        "Security" should not match "Security Incident 2026-01".
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Partial name should not match
        self._plugin._task.args = {
            "name": "Security",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["investigations"]) == 0  # No exact match

    # Query All Investigations Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_all(self, connection, monkeypatch):
        """Test querying all investigations without filters.

        When no investigation_ref_id or name is provided, should return all investigations.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigations" in result
        assert len(result["investigations"]) == 3

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_all_empty(self, connection, monkeypatch):
        """Test querying all investigations when none exist.

        Should return an empty list without error.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_INVESTIGATIONS_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["investigations"]) == 0

    # Time Range Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_with_create_time_min(self, connection, monkeypatch):
        """Test that create_time_min parameter is passed to API."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "create_time_min": "-7d",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        # Verify create_time_min was passed to API
        assert len(captured_params) > 0
        assert captured_params[0] is not None
        assert captured_params[0].get("create_time_min") == "-7d"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_with_create_time_max(self, connection, monkeypatch):
        """Test that create_time_max parameter is passed to API."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "create_time_max": "now",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(captured_params) > 0
        assert captured_params[0] is not None
        assert captured_params[0].get("create_time_max") == "now"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_with_time_range(self, connection, monkeypatch):
        """Test that both create_time_min and create_time_max are passed to API."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "create_time_min": "-30d",
            "create_time_max": "-1d",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(captured_params) > 0
        assert captured_params[0].get("create_time_min") == "-30d"
        assert captured_params[0].get("create_time_max") == "-1d"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_time_range_with_name(self, connection, monkeypatch):
        """Test that time filters are applied when querying by name."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Security Incident 2026-01",
            "create_time_min": "-7d",
            "create_time_max": "now",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(captured_params) > 0
        assert captured_params[0].get("create_time_min") == "-7d"
        assert captured_params[0].get("create_time_max") == "now"

    # Always Changed=False Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_always_changed_false(self, connection, monkeypatch):
        """Verify that info module always returns changed=False.

        Info modules are read-only and should never report changes.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Test with various query types
        test_cases = [
            {},  # All investigations
            {"investigation_ref_id": "inv-001-aaaaa"},  # By ref_id
            {"name": "Security Incident 2026-01"},  # By name
            {"create_time_min": "-7d"},  # With time filter
        ]

        for args in test_cases:
            self._plugin._task.args = args
            result = self._plugin.run(task_vars=self._task_vars)
            assert result["changed"] is False, f"Expected changed=False for args: {args}"

    # Custom API Path Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

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

    # Field Mapping Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_field_mapping(self, connection, monkeypatch):
        """Test that API fields are correctly mapped to module format.

        Verify that API field names and values are converted to module format.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE_SINGLE)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        investigation = result["investigations"][0]

        # Verify field mapping
        assert "investigation_ref_id" in investigation  # investigation_guid -> investigation_ref_id
        assert "name" in investigation
        assert "description" in investigation
        assert "owner" in investigation

        # Verify status/disposition/sensitivity are converted to human-readable
        assert investigation["status"] == "new"  # "1" -> "new"
        assert investigation["disposition"] == "undetermined"  # "disposition:6" -> "undetermined"
        assert investigation["sensitivity"] == "amber"  # "Amber" -> "amber"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_finding_ids_extraction(self, connection, monkeypatch):
        """Test that finding_ids are extracted from consolidated_findings."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE_SINGLE)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        investigation = result["investigations"][0]

        # Verify finding_ids are extracted
        assert "finding_ids" in investigation
        assert investigation["finding_ids"] == ["finding-001@@notable@@time123"]

    # Priority Tests (investigation_ref_id takes precedence over name) #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_ref_id_priority(self, connection, monkeypatch):
        """Test that investigation_ref_id takes precedence over name when both are provided."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        call_count = {"ref_id_calls": 0, "all_calls": 0}

        def get_by_path(self, path, query_params=None):
            if query_params and query_params.get("ids"):
                call_count["ref_id_calls"] += 1
                return [copy.deepcopy(INVESTIGATION_API_RESPONSE_SINGLE)]
            else:
                call_count["all_calls"] += 1
                return copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "name": "Some Other Name",  # Should be ignored
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should have called the ref_id path, not the all-investigations path
        assert call_count["ref_id_calls"] == 1
        assert call_count["all_calls"] == 0
        assert len(result["investigations"]) == 1

    # Error Handling Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_handles_null_items(self, connection, monkeypatch):
        """Test handling of null items in API response.

        The API might return None values in the list; these should be filtered out.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [
                None,  # Null item
                copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST[0]),
                None,  # Another null
            ]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        # Should only have 1 valid investigation (the null ones filtered out)
        assert len(result["investigations"]) == 1

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_handles_empty_items(self, connection, monkeypatch):
        """Test handling of empty dict items in API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [
                {},  # Empty item
                copy.deepcopy(INVESTIGATION_API_RESPONSE_LIST[0]),
            ]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_handles_404(self, connection, monkeypatch):
        """Test graceful handling of 404 errors."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "non-existent-id",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should return empty list, not fail
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["investigations"] == []

    # Consistency Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_returns_list(self, connection, monkeypatch):
        """Test that investigations are always returned as a list.

        Even when querying by ref_id (single result), should return a list.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE_SINGLE)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["investigations"], list)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_info_empty_returns_list(self, connection, monkeypatch):
        """Test that empty results are returned as an empty list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return []

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["investigations"], list)
        assert len(result["investigations"]) == 0
