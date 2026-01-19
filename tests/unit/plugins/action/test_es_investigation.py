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
Unit tests for the splunk_investigation action plugin.

These tests verify that the splunk_investigation action plugin works correctly for:
- Creating new investigations (without investigation_ref_id)
- Updating existing investigations (with investigation_ref_id)
- Idempotency (no changes when state matches)
- Error handling (missing parameters, investigation not found)
- Check mode behavior
- Adding findings to investigations

The tests use mocking to simulate Splunk API responses without requiring
a real Splunk server connection.
"""


import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_investigation import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


# Test data: API Response Payloads
# These represent what the Splunk API returns for investigations.
INVESTIGATION_API_RESPONSE = {
    "investigation_guid": "inv-12345-abcde",
    "name": "Security Incident 2026-01",
    "description": "Investigation into suspicious login activity",
    "owner": "admin",
    "status": "1",  # "new" in API format
    "urgency": "high",
    "disposition": "disposition:6",  # "undetermined" in API format
    "sensitivity": "Amber",  # API uses capitalized
    "consolidated_findings": {
        "event_id": ["finding-001@@notable@@time123"],
    },
}

INVESTIGATION_API_RESPONSE_UPDATED = {
    "investigation_guid": "inv-12345-abcde",
    "name": "Security Incident 2026-01",
    "description": "Updated investigation description",
    "owner": "analyst1",
    "status": "4",  # "resolved" in API format
    "urgency": "high",
    "disposition": "disposition:1",  # "true_positive" in API format
    "sensitivity": "Red",
    "consolidated_findings": {
        "event_id": ["finding-001@@notable@@time123", "finding-002@@notable@@time456"],
    },
}


# Test data: Module Request Payloads
# These represent what users provide to the Ansible module.

CREATE_INVESTIGATION_PARAMS = {
    "name": "Security Incident 2026-01",
    "description": "Investigation into suspicious login activity",
    "status": "new",
    "owner": "admin",
    "urgency": "high",
    "disposition": "undetermined",
    "sensitivity": "amber",
}

UPDATE_INVESTIGATION_PARAMS = {
    "investigation_ref_id": "inv-12345-abcde",
    "owner": "analyst1",
    "status": "resolved",
    "disposition": "true_positive",
    "sensitivity": "red",
}

MINIMAL_CREATE_PARAMS = {
    "name": "Minimal Investigation",
}


class TestSplunkInvestigation:
    """Test class for the splunk_investigation action plugin.

    Each test follows this pattern:
    1. setup_method: Creates mock Ansible components (task, connection, play_context)
    2. Test method: Sets task.args, mocks API methods, runs plugin, asserts results

    """

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

        # Create a mock connection (we'll set socket_path in each test)
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
        self._plugin._task.action = "splunk_investigation"
        self._plugin._task.async_val = False

        # Task variables (empty for most tests)
        self._task_vars = {}

    # Create Investigation Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_create_success(self, connection, monkeypatch):
        """Test successful creation of a new investigation.

        When creating an investigation (no investigation_ref_id), the module should:
        1. Call the investigations API to create the resource
        2. Return changed=True
        3. Include the created investigation in the result
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert "investigation" in result
        assert result["investigation"]["after"] is not None
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_create_minimal(self, connection, monkeypatch):
        """Test creation with only required parameters.

        The module requires only 'name' for creating a new investigation.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return {
                "investigation_guid": "inv-new-12345",
                "name": "Minimal Investigation",
            }

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = MINIMAL_CREATE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_create_missing_name(self, connection):
        """Test that missing name returns an error.

        Name is a required field when creating a new investigation.
        The module should fail with a clear error message.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Create params without name
        params = CREATE_INVESTIGATION_PARAMS.copy()
        del params["name"]

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "name" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_create_with_findings(self, connection, monkeypatch):
        """Test creation with finding_ids attached."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = CREATE_INVESTIGATION_PARAMS.copy()
        params["finding_ids"] = [
            "A265ED94-AE9E-428C-91D2-64BB956EB7CB@@notable@@time1234567890",
        ]

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    # Update Investigation Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_success(self, connection, monkeypatch):
        """Test successful update of an existing investigation."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return existing investigation
        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        # Mock create_update for the update operation
        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = UPDATE_INVESTIGATION_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "investigation" in result
        # Should have both before and after states
        assert result["investigation"]["before"] is not None
        assert result["investigation"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_idempotent(self, connection, monkeypatch):
        """Test that updating with same values returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return investigation that already has the desired values
        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Request the same values that already exist
        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "owner": "analyst1",
            "status": "resolved",
            "disposition": "true_positive",
            "sensitivity": "red",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # No changes should be made
        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_not_found(self, connection, monkeypatch):
        """Test updating a non-existent investigation returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return empty (investigation not found)
        def get_by_path(self, path, query_params=None):
            return []

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "non-existent-id",
            "status": "resolved",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "not found" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_ignores_name(self, connection, monkeypatch):
        """Test that name is ignored during update (cannot be updated)."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # Include both name (non-updatable) and status (updatable)
        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "name": "This should be ignored",  # Not updatable
            "status": "resolved",  # Updatable - should trigger change
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should still succeed with the updatable field
        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_no_updatable_fields(self, connection, monkeypatch):
        """Test that providing only non-updatable fields returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Only provide non-updatable fields
        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "name": "Cannot update this",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True

    # Add Findings Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_add_findings(self, connection, monkeypatch):
        """Test adding findings to an existing investigation."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        api_calls = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            api_calls.append({"path": rest_path, "data": data})
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "finding_ids": ["finding-002@@notable@@time456"],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        # Should have called the findings endpoint
        assert any("/findings" in call["path"] for call in api_calls)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_add_existing_findings_skipped(self, connection, monkeypatch):
        """Test that existing findings are skipped (not duplicated)."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        api_calls = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            api_calls.append({"path": rest_path, "data": data})
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # Try to add a finding that already exists
        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "finding_ids": ["finding-001@@notable@@time123"],  # Already exists
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should not report changes (finding already exists)
        assert result["changed"] is False
        assert result.get("failed") is not True

    # Check Mode Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_check_mode_create(self, connection, monkeypatch):
        """Test check mode for creating an investigation."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        # Track if create_update is called (it shouldn't be)
        create_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            create_called.append(True)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not actually call API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(create_called) == 0  # API should not be called
        assert "check mode" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_check_mode_update(self, connection, monkeypatch):
        """Test check mode for updating an investigation."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        # Track if create_update is called (it shouldn't be for the update)
        update_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            update_called.append(True)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = UPDATE_INVESTIGATION_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not call update API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(update_called) == 0  # Update API should not be called
        assert "check mode" in result["msg"].lower()
        # Should show what the after state would be
        assert result["investigation"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_check_mode_no_changes(self, connection, monkeypatch):
        """Test check mode when no changes are needed."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        # Return investigation that already matches desired state
        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "owner": "analyst1",
            "status": "resolved",
            "disposition": "true_positive",
            "sensitivity": "red",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

    # Custom API Path Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Capture the path used in the API call
        captured_paths = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_paths.append(rest_path)
            return copy.deepcopy(INVESTIGATION_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = CREATE_INVESTIGATION_PARAMS.copy()
        params["api_namespace"] = "customNS"
        params["api_user"] = "customuser"
        params["api_app"] = "CustomApp"

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        # Verify the custom path was used
        assert len(captured_paths) > 0
        assert "customNS" in captured_paths[0]
        assert "customuser" in captured_paths[0]
        assert "CustomApp" in captured_paths[0]

    # Field Update Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_single_field(self, connection, monkeypatch):
        """Test updating just one field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # Only update status
        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "status": "resolved",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_urgency(self, connection, monkeypatch):
        """Test updating urgency field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(INVESTIGATION_API_RESPONSE)
            response["urgency"] = "critical"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "urgency": "critical",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_description(self, connection, monkeypatch):
        """Test updating description field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(INVESTIGATION_API_RESPONSE)
            response["description"] = "Updated description"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "description": "Updated description",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_update_sensitivity(self, connection, monkeypatch):
        """Test updating sensitivity field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE)]

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(INVESTIGATION_API_RESPONSE)
            response["sensitivity"] = "Red"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "sensitivity": "red",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    # Result Message Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_create_success_message(self, connection, monkeypatch):
        """Test that successful create returns appropriate message."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert "msg" in result
        assert "successfully" in result["msg"].lower() or "created" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_no_changes_message(self, connection, monkeypatch):
        """Test that no changes returns appropriate message."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return [copy.deepcopy(INVESTIGATION_API_RESPONSE_UPDATED)]

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "investigation_ref_id": "inv-12345-abcde",
            "owner": "analyst1",
            "status": "resolved",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert "msg" in result
        assert "no changes" in result["msg"].lower()
