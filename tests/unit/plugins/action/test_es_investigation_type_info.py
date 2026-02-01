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
Unit tests for the splunk_investigation_type_info action plugin.

These tests verify that the splunk_investigation_type_info action plugin works correctly for:
- Querying a specific investigation type by name
- Querying all investigation types
- Handling not found scenarios
- Field mapping from API to module format

The tests use mocking to simulate Splunk API responses.
"""

__metaclass__ = type

import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_investigation_type_info import (
    ActionModule,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


# Test data: API Response Payloads
# These represent what the Splunk API returns for investigation type queries.

INVESTIGATION_TYPE_API_RESPONSE_SINGLE = {
    "incident_type": "Insider Threat",
    "description": "Investigation type for insider threat incidents",
    "response_template_ids": [],
}

INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS = {
    "incident_type": "Malware Incident",
    "description": "Investigation type for malware-related incidents",
    "response_template_ids": [
        "3415de6d-cdfb-4bdb-a21d-693cde38f1e8",
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    ],
}

INVESTIGATION_TYPES_API_RESPONSE_LIST = {
    "items": [
        {
            "incident_type": "Insider Threat",
            "description": "Investigation type for insider threat incidents",
            "response_template_ids": [],
        },
        {
            "incident_type": "Malware Incident",
            "description": "Investigation type for malware-related incidents",
            "response_template_ids": [
                "3415de6d-cdfb-4bdb-a21d-693cde38f1e8",
            ],
        },
        {
            "incident_type": "Phishing Attack",
            "description": "Investigation type for phishing attacks",
            "response_template_ids": [
                "uuid-1111-2222-3333-444455556666",
                "uuid-aaaa-bbbb-cccc-ddddeeeeffff",
            ],
        },
    ],
}

EMPTY_INVESTIGATION_TYPES_RESPONSE = {"items": []}


class TestSplunkInvestigationTypeInfo:
    """Test class for the splunk_investigation_type_info action plugin.

    The splunk_investigation_type_info module is a "read-only" info module that queries
    Splunk for investigation types without making changes. It should always return
    changed=False.

    Query modes:
    1. By name: Returns a single specific investigation type
    2. All: Returns all investigation types (when no name provided)
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
        self._plugin._task.action = "splunk_investigation_type_info"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Query by Name Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_by_name(self, connection, monkeypatch):
        """Test querying a specific investigation type by name.

        When name is provided, the module should query for that
        specific investigation type and return it in a list.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            # When querying by name
            if "Insider%20Threat" in path:
                return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_SINGLE)
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Info modules should always return changed=False
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigation_types" in result
        assert len(result["investigation_types"]) == 1
        assert result["investigation_types"][0]["name"] == "Insider Threat"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_by_name_not_found(self, connection, monkeypatch):
        """Test querying a non-existent investigation type by name.

        When the investigation type doesn't exist, the module should return an empty
        list rather than failing.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Non-Existent Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigation_types" in result
        assert len(result["investigation_types"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_by_name_with_response_plans(self, connection, monkeypatch):
        """Test querying an investigation type that has response plan associations."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Malware Incident",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["investigation_types"]) == 1
        investigation_type = result["investigation_types"][0]
        assert investigation_type["name"] == "Malware Incident"
        assert "response_plan_ids" in investigation_type
        assert len(investigation_type["response_plan_ids"]) == 2

    # Query All Investigation Types Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_all(self, connection, monkeypatch):
        """Test querying all investigation types without filters.

        When no name is provided, should return all investigation types.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPES_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "investigation_types" in result
        assert len(result["investigation_types"]) == 3

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_all_empty(self, connection, monkeypatch):
        """Test querying all investigation types when none exist.

        Should return an empty list without error.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_INVESTIGATION_TYPES_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["investigation_types"]) == 0

    # Always Changed=False Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_always_changed_false(self, connection, monkeypatch):
        """Verify that info module always returns changed=False.

        Info modules are read-only and should never report changes.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            if "incidenttypes" in path and not path.endswith("incidenttypes"):
                return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_SINGLE)
            return copy.deepcopy(INVESTIGATION_TYPES_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Test with various query types
        test_cases = [
            {},  # All investigation types
            {"name": "Insider Threat"},  # By name
        ]

        for args in test_cases:
            self._plugin._task.args = args
            result = self._plugin.run(task_vars=self._task_vars)
            assert result["changed"] is False, f"Expected changed=False for args: {args}"

    # Custom API Path Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return copy.deepcopy(INVESTIGATION_TYPES_API_RESPONSE_LIST)

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
    def test_investigation_type_info_field_mapping(self, connection, monkeypatch):
        """Test that API fields are correctly mapped to module format.

        Verify that API field names are converted to module format:
        - incident_type -> name
        - response_template_ids -> response_plan_ids
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Malware Incident",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        investigation_type = result["investigation_types"][0]

        # Verify field mapping: incident_type -> name
        assert "name" in investigation_type
        assert investigation_type["name"] == "Malware Incident"

        # Verify field mapping: response_template_ids -> response_plan_ids
        assert "response_plan_ids" in investigation_type
        assert len(investigation_type["response_plan_ids"]) == 2
        assert "3415de6d-cdfb-4bdb-a21d-693cde38f1e8" in investigation_type["response_plan_ids"]

        # Verify description is included
        assert "description" in investigation_type
        assert (
            investigation_type["description"] == "Investigation type for malware-related incidents"
        )

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_field_mapping_all(self, connection, monkeypatch):
        """Test that field mapping works for all items when querying all."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPES_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        # Verify all items have correct field mapping
        for investigation_type in result["investigation_types"]:
            assert "name" in investigation_type
            assert "description" in investigation_type
            assert "response_plan_ids" in investigation_type

    # Error Handling Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_handles_null_items(self, connection, monkeypatch):
        """Test handling of null items in API response.

        The API might return None values in the items list; these should be filtered out.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "items": [
                    None,  # Null item
                    copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_SINGLE),
                    None,  # Another null
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        # Should only have 1 valid investigation type (the null ones filtered out)
        assert len(result["investigation_types"]) == 1

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_handles_empty_items(self, connection, monkeypatch):
        """Test handling of empty dict items in API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "items": [
                    {},  # Empty item
                    copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_SINGLE),
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_handles_404(self, connection, monkeypatch):
        """Test graceful handling of 404 errors."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Non-Existent Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should return empty list, not fail
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["investigation_types"] == []

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_handles_generic_404(self, connection, monkeypatch):
        """Test graceful handling of 404 errors with different message format."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("Resource not found")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Non-Existent Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should return empty list for "not found" errors
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["investigation_types"] == []

    # Consistency Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_returns_list(self, connection, monkeypatch):
        """Test that investigation_types are always returned as a list.

        Even when querying by name (single result), should return a list.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_SINGLE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["investigation_types"], list)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_empty_returns_list(self, connection, monkeypatch):
        """Test that empty results are returned as an empty list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_INVESTIGATION_TYPES_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["investigation_types"], list)
        assert len(result["investigation_types"]) == 0

    # Response Plan IDs Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_empty_response_plan_ids(self, connection, monkeypatch):
        """Test that empty response_plan_ids are handled correctly."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "incident_type": "Test Type",
                "description": "Test",
                "response_template_ids": [],  # Empty list
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["investigation_types"]) == 1
        assert result["investigation_types"][0]["response_plan_ids"] == []

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_null_response_plan_ids(self, connection, monkeypatch):
        """Test that null response_template_ids are converted to empty list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "incident_type": "Test Type",
                "description": "Test",
                "response_template_ids": None,  # None instead of list
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["investigation_types"]) == 1
        # None should be converted to empty list
        assert result["investigation_types"][0]["response_plan_ids"] == []

    # URL Encoding Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_name_with_spaces(self, connection, monkeypatch):
        """Test querying investigation type with spaces in name."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return {
                "incident_type": "Insider Threat Investigation",
                "description": "Test",
                "response_template_ids": [],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat Investigation",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["investigation_types"]) == 1
        # Verify the path was URL encoded
        assert len(captured_paths) > 0
        assert "%20" in captured_paths[0] or "Insider Threat Investigation" in captured_paths[0]

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_name_with_special_characters(self, connection, monkeypatch):
        """Test querying investigation type with special characters in name."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return {
                "incident_type": "Test/Type&Name",
                "description": "Test",
                "response_template_ids": [],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test/Type&Name",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["investigation_types"]) == 1

    # Missing Fields Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_missing_description(self, connection, monkeypatch):
        """Test handling of missing description field in API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "incident_type": "Test Type",
                # description is missing
                "response_template_ids": [],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["investigation_types"]) == 1
        # Description should default to empty string
        assert result["investigation_types"][0]["description"] == ""

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_missing_incident_type(self, connection, monkeypatch):
        """Test handling of missing incident_type field in API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                # incident_type is missing
                "description": "Test description",
                "response_template_ids": [],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        # Missing incident_type is treated as not found - empty list returned
        assert len(result["investigation_types"]) == 0

    # API Response Structure Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_info_no_items_key(self, connection, monkeypatch):
        """Test handling of API response without 'items' key for list query."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {}  # No 'items' key

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["investigation_types"] == []
