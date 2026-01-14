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
Unit tests for the splunk_finding action plugin.

These tests verify that the splunk_finding action plugin works correctly for:
- Creating new findings (without ref_id)
- Updating existing findings (with ref_id)
- Idempotency (no changes when state matches)
- Error handling (missing parameters, finding not found)
- Check mode behavior

The tests use mocking to simulate Splunk API responses without requiring
a real Splunk server connection.
"""


import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_finding import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


# Test data: API Response Payloads
# These represent what the Splunk API returns for findings.
FINDING_API_RESPONSE = {
    "finding_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
    "rule_title": "Suspicious Login Activity",
    "rule_description": "Multiple failed login attempts detected",
    "security_domain": "access",
    "risk_object": "testuser",
    "risk_object_type": "user",
    "risk_score": "50.0",
    "owner": "admin",
    "status": "1",  # "new" in API format
    "urgency": "high",
    "disposition": "disposition:6",  # "undetermined" in API format
}

FINDING_API_RESPONSE_UPDATED = {
    "finding_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
    "rule_title": "Suspicious Login Activity",
    "rule_description": "Multiple failed login attempts detected",
    "security_domain": "access",
    "risk_object": "testuser",
    "risk_object_type": "user",
    "risk_score": "50.0",
    "owner": "analyst",
    "status": "4",  # "resolved" in API format
    "urgency": "high",
    "disposition": "disposition:1",  # "true_positive" in API format
}


# Test data: Module Request Payloads
# These represent what users provide to the Ansible module. Note the
# human-readable field names and values.

CREATE_FINDING_PARAMS = {
    "title": "Suspicious Login Activity",
    "description": "Multiple failed login attempts detected",
    "security_domain": "access",
    "entity": "testuser",
    "entity_type": "user",
    "finding_score": 50,
    "owner": "admin",
    "status": "new",
    "urgency": "high",
    "disposition": "undetermined",
}

UPDATE_FINDING_PARAMS = {
    "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
    "owner": "analyst",
    "status": "resolved",
    "disposition": "true_positive",
}

MINIMAL_CREATE_PARAMS = {
    "title": "Minimal Finding",
    "description": "A minimal finding for testing",
    "security_domain": "network",
    "entity": "firewall01",
    "entity_type": "system",
    "finding_score": 25,
}


class TestSplunkFinding:
    """Test class for the splunk_finding action plugin.

    Each test follows this pattern:
    1. setup_method: Creates mock Ansible components (task, connection, play_context)
    2. Test method: Sets task.args, mocks API methods, runs plugin, asserts results

    Key concepts:
    - monkeypatch: pytest fixture that lets us replace methods at runtime
    - MagicMock: Creates fake objects that record how they're used
    - The plugin's run() method is what Ansible calls to execute the action
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
        self._plugin._task.action = "splunk_finding"
        self._plugin._task.async_val = False

        # Task variables (empty for most tests)
        self._task_vars = {}

    # Create Finding Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_create_success(self, connection, monkeypatch):
        """Test successful creation of a new finding.

        When creating a finding (no ref_id), the module should:
        1. Call the findings API to create the resource
        2. Return changed=True
        3. Include the created finding in the result

        This test mocks the create_update method to return a simulated
        API response, then verifies the plugin handles it correctly.
        """
        # Set up the mock connection
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock the API create method to return our test response
        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(FINDING_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # Set the task arguments (what the user provides in the playbook)
        self._plugin._task.args = CREATE_FINDING_PARAMS.copy()

        # Run the plugin
        result = self._plugin.run(task_vars=self._task_vars)

        # Verify the result
        assert result["changed"] is True
        assert "finding" in result
        assert result["finding"]["after"] is not None
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_create_minimal(self, connection, monkeypatch):
        """Test creation with only required parameters.

        The module requires: title, description, security_domain, entity,
        entity_type, and finding_score for creating a new finding.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return {
                "finding_id": "new-finding-id@@notable@@time1234567890",
                "rule_title": "Minimal Finding",
                "rule_description": "A minimal finding for testing",
                "security_domain": "network",
                "risk_object": "firewall01",
                "risk_object_type": "system",
                "risk_score": "25.0",
            }

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = MINIMAL_CREATE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_create_missing_title(self, connection):
        """Test that missing title returns an error.

        Title is a required field when creating a new finding.
        The module should fail with a clear error message.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Create params without title
        params = CREATE_FINDING_PARAMS.copy()
        del params["title"]

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "title" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_create_missing_required_fields(self, connection):
        """Test that missing required fields returns an error.

        When creating a finding, these fields are required:
        - title, description, security_domain, entity, entity_type, finding_score
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Only provide title, missing other required fields
        self._plugin._task.args = {
            "title": "Incomplete Finding",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "missing" in result["msg"].lower() or "required" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_create_with_custom_fields(self, connection, monkeypatch):
        """Test creation with custom fields.

        Custom fields are passed as a list of name/value pairs and should
        be included in the API payload.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(FINDING_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = CREATE_FINDING_PARAMS.copy()
        params["fields"] = [
            {"name": "custom_field_a", "value": "value1"},
            {"name": "custom_field_b", "value": "value2"},
        ]

        self._plugin._task.args = params

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    # Update Finding Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_success(self, connection, monkeypatch):
        """Test successful update of an existing finding."""

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return existing finding
        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE)

        # Mock create_update for the update operation
        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(FINDING_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = UPDATE_FINDING_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "finding" in result
        # Should have both before and after states
        assert result["finding"]["before"] is not None
        assert result["finding"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_idempotent(self, connection, monkeypatch):
        """Test that updating with same values returns changed=False."""

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return finding that already has the desired values
        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Request the same values that already exist
        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "owner": "analyst",
            "status": "resolved",
            "disposition": "true_positive",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # No changes should be made
        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_not_found(self, connection, monkeypatch):
        """Test updating a non-existent finding returns an error.

        If the specified ref_id doesn't exist, the module should fail
        with a clear error message rather than creating a new finding.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return empty (finding not found)
        def get_by_path(self, path, query_params=None):
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "non-existent-id@@notable@@time1234567890",
            "status": "resolved",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "not found" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_only_updatable_fields(self, connection, monkeypatch):
        """Test that only updatable fields trigger changes.

        When updating, only owner, status, urgency, and disposition can be
        modified. Other fields like title and description are ignored.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE)

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(FINDING_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # Include both updatable and non-updatable fields
        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "title": "This should be ignored",  # Not updatable
            "description": "Also ignored",  # Not updatable
            "status": "resolved",  # Updatable - should trigger change
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should still succeed with the updatable field
        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_no_updatable_fields(self, connection, monkeypatch):
        """Test that providing only non-updatable fields returns an error.

        If the user tries to update a finding but only provides fields that
        cannot be updated (like title), the module should return an error.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Only provide non-updatable fields
        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "title": "Cannot update this",
            "description": "Cannot update this either",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "updatable" in result["msg"].lower() or "update" in result["msg"].lower()

    # Check Mode Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_check_mode_create(self, connection, monkeypatch):
        """Test check mode for creating a finding.

        In check mode, the module should report what would happen without
        actually making API calls. It should return changed=True but not
        create the finding.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        # Track if create_update is called (it shouldn't be)
        create_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            create_called.append(True)
            return copy.deepcopy(FINDING_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_FINDING_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not actually call API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(create_called) == 0  # API should not be called
        assert "check mode" in result["msg"].lower()

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_check_mode_update(self, connection, monkeypatch):
        """Test check mode for updating a finding.

        Check mode should show what would change without making the update.
        It should fetch the existing state but not call the update API.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE)

        # Track if create_update is called (it shouldn't be for the update)
        update_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            update_called.append(True)
            return copy.deepcopy(FINDING_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = UPDATE_FINDING_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not call update API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(update_called) == 0  # Update API should not be called
        assert "check mode" in result["msg"].lower()
        # Should show what the after state would be
        assert result["finding"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_check_mode_no_changes(self, connection, monkeypatch):
        """Test check mode when no changes are needed.

        If the current state matches the desired state, check mode should
        report changed=False.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        # Return finding that already matches desired state
        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "owner": "analyst",
            "status": "resolved",
            "disposition": "true_positive",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

    # Custom API Path Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""

        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Capture the path used in the API call
        captured_paths = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_paths.append(rest_path)
            return copy.deepcopy(FINDING_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = CREATE_FINDING_PARAMS.copy()
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

    # Edge Case Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_single_field(self, connection, monkeypatch):
        """Test updating just one field.

        Users should be able to update a single field without specifying
        all other fields.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE)

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(FINDING_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        # Only update status
        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "status": "resolved",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_update_urgency(self, connection, monkeypatch):
        """Test updating urgency field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE)

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(FINDING_API_RESPONSE)
            response["urgency"] = "critical"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "urgency": "critical",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
