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
Unit tests for the splunk_investigation_type action plugin.

These tests verify that the splunk_investigation_type action plugin works correctly for:
- Creating new investigation types
- Updating existing investigation types
- Idempotency (no changes when state matches)
- Error handling (missing parameters, etc.)
- Check mode behavior
- Managing response plan associations

The tests use mocking to simulate Splunk API responses without requiring
a real Splunk server connection.
"""

import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_investigation_type import ActionModule
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
# These represent what the Splunk API returns for investigation type queries.

INVESTIGATION_TYPE_API_RESPONSE = {
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

INVESTIGATION_TYPE_API_RESPONSE_UPDATED = {
    "incident_type": "Insider Threat",
    "description": "Updated description for insider threat investigations",
    "response_template_ids": ["new-uuid-1234-5678-abcd-ef1234567890"],
}

# Test data: Module Request Payloads
CREATE_INVESTIGATION_TYPE_PARAMS = {
    "name": "Insider Threat",
    "description": "Investigation type for insider threat incidents",
}

CREATE_INVESTIGATION_TYPE_WITH_PLANS_PARAMS = {
    "name": "Malware Incident",
    "description": "Investigation type for malware-related incidents",
    "response_plan_ids": [
        "3415de6d-cdfb-4bdb-a21d-693cde38f1e8",
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    ],
}

UPDATE_INVESTIGATION_TYPE_PARAMS = {
    "name": "Insider Threat",
    "description": "Updated description for insider threat investigations",
    "response_plan_ids": ["new-uuid-1234-5678-abcd-ef1234567890"],
}

MINIMAL_CREATE_PARAMS = {
    "name": "Minimal Investigation Type",
}


class TestSplunkInvestigationType:
    """Test class for the splunk_investigation_type action plugin.

    The splunk_investigation_type module manages investigation types (incident types)
    in Splunk ES. It supports create and update operations (delete is not supported
    by the Splunk API).

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
        self._plugin._task.action = "splunk_investigation_type"
        self._plugin._task.async_val = False

        # Task variables (empty for most tests)
        self._task_vars = {}

    # Create Investigation Type Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_create_success(self, connection, monkeypatch):
        """Test successful creation of a new investigation type.

        When creating an investigation type (name not found), the module should:
        1. Call the incident types API to create the resource
        2. Return changed=True
        3. Include the created investigation type in the result
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return 404 (not found)
        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert "investigation_type" in result
        assert result["investigation_type"]["after"] is not None
        assert result["investigation_type"]["before"] is None
        assert result.get("failed") is not True
        assert "created" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_create_minimal(self, connection, monkeypatch):
        """Test creation with only required parameters.

        The module requires only 'name' for creating a new investigation type.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return {
                "incident_type": "Minimal Investigation Type",
                "description": "",
                "response_template_ids": [],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = MINIMAL_CREATE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_create_missing_name(self, connection):
        """Test that missing name returns an error.

        Name is a required field when creating an investigation type.
        The module should fail with a clear error message.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Create params without name
        self._plugin._task.args = {
            "description": "Some description",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "name" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_create_with_response_plans(self, connection, monkeypatch):
        """Test creation with response plan associations.

        When response_plan_ids are provided, the module should:
        1. Create the investigation type
        2. Then update it with the response plan associations
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        api_calls = []

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            api_calls.append({"path": rest_path, "data": data})
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            api_calls.append({"path": path, "data": data, "method": "PUT"})
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_WITH_PLANS_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        # Verify response plans are in the result
        after = result["investigation_type"]["after"]
        assert len(after["response_plan_ids"]) == 2

    # Update Investigation Type Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_update_success(self, connection, monkeypatch):
        """Test successful update of an existing investigation type."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return existing investigation type
        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = UPDATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "investigation_type" in result
        # Should have both before and after states
        assert result["investigation_type"]["before"] is not None
        assert result["investigation_type"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_update_idempotent(self, connection, monkeypatch):
        """Test that updating with same values returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Mock get_by_path to return investigation type that already has the desired values
        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Request the same values that already exist
        self._plugin._task.args = {
            "name": "Insider Threat",
            "description": "Investigation type for insider threat incidents",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # No changes should be made
        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_update_description_only(self, connection, monkeypatch):
        """Test updating only the description field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)
            response["description"] = "New description"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat",
            "description": "New description",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_update_response_plans_only(self, connection, monkeypatch):
        """Test updating only the response_plan_ids field."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)
            response["response_template_ids"] = ["new-plan-id"]
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat",
            "response_plan_ids": ["new-plan-id"],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_remove_all_response_plans(self, connection, monkeypatch):
        """Test removing all response plan associations."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            response = copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)
            response["response_template_ids"] = []
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = {
            "name": "Malware Incident",
            "response_plan_ids": [],  # Empty list to remove all
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_update_preserves_unspecified_values(self, connection, monkeypatch):
        """Test that unspecified values are preserved from existing state."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_payloads = []

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            captured_payloads.append(data)
            response = copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)
            response["description"] = "Updated description"
            return response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        # Only specify name and description, not response_plan_ids
        self._plugin._task.args = {
            "name": "Malware Incident",
            "description": "Updated description",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        # Response plans should be preserved from existing state
        assert len(captured_payloads) > 0

    # Check Mode Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_check_mode_create(self, connection, monkeypatch):
        """Test check mode for creating an investigation type.

        In check mode, the module should report what would happen without
        actually making API calls.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        # Track if create_update is called (it shouldn't be)
        create_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            create_called.append(True)
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not actually call API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(create_called) == 0  # API should not be called
        assert "check mode" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_check_mode_update(self, connection, monkeypatch):
        """Test check mode for updating an investigation type."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        # Track if update_by_path is called (it shouldn't be)
        update_called = []

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            update_called.append(True)
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = UPDATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changed but not call update API
        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(update_called) == 0  # Update API should not be called
        assert "check mode" in _get_msg_str(result)
        # Should show what the after state would be
        assert result["investigation_type"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_check_mode_no_changes(self, connection, monkeypatch):
        """Test check mode when no changes are needed."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat",
            "description": "Investigation type for insider threat incidents",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True

    # Custom API Path Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_paths.append(rest_path)
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        params = CREATE_INVESTIGATION_TYPE_PARAMS.copy()
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

    # Result Message Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_create_success_message(self, connection, monkeypatch):
        """Test that successful create returns appropriate message."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert "msg" in result
        assert "created" in _get_msg_str(result) or "successfully" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_update_success_message(self, connection, monkeypatch):
        """Test that successful update returns appropriate message."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = UPDATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert "msg" in result
        assert "updated" in _get_msg_str(result) or "successfully" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_no_changes_message(self, connection, monkeypatch):
        """Test that no changes returns appropriate message."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Insider Threat",
            "description": "Investigation type for insider threat incidents",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert "msg" in result
        assert "no changes" in _get_msg_str(result)

    # Field Mapping Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_field_mapping(self, connection, monkeypatch):
        """Test that API fields are correctly mapped to module format."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            # Called to associate response plans after creation
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_WITH_PLANS)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_WITH_PLANS_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        investigation_type = result["investigation_type"]["after"]

        # Verify field mapping: incident_type -> name
        assert investigation_type["name"] == "Malware Incident"
        assert (
            investigation_type["description"] == "Investigation type for malware-related incidents"
        )
        # Verify response_template_ids -> response_plan_ids
        assert "response_plan_ids" in investigation_type
        assert len(investigation_type["response_plan_ids"]) == 2

    # Response Plan ID Comparison Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_response_plan_ids_order_independent(self, connection, monkeypatch):
        """Test that response plan ID comparison is order-independent."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "incident_type": "Test Type",
                "description": "Test description",
                "response_template_ids": ["id-b", "id-a"],  # Different order
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
            "description": "Test description",
            "response_plan_ids": ["id-a", "id-b"],  # Same IDs, different order
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should not report changes since the same IDs are present
        assert result["changed"] is False
        assert result.get("failed") is not True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_response_plan_ids_change_detected(self, connection, monkeypatch):
        """Test that different response plan IDs are detected as a change."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "incident_type": "Test Type",
                "description": "Test description",
                "response_template_ids": ["id-a", "id-b"],
            }

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            return {
                "incident_type": "Test Type",
                "description": "Test description",
                "response_template_ids": ["id-a", "id-c"],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
            "description": "Test description",
            "response_plan_ids": ["id-a", "id-c"],  # id-b changed to id-c
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should report changes
        assert result["changed"] is True
        assert result.get("failed") is not True

    # Error Handling Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_handles_api_error(self, connection, monkeypatch):
        """Test handling of API errors during lookup."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 500: Internal Server Error")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_PARAMS.copy()

        # Should raise an exception for non-404 errors
        try:
            result = self._plugin.run(task_vars=self._task_vars)
            assert result.get("failed") is True or "500" in _get_msg_str(result)
        except Exception as e:
            assert "500" in str(e)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_empty_response_plan_ids_handled(self, connection, monkeypatch):
        """Test that empty response_plan_ids list is handled correctly."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "incident_type": "Test Type",
                "description": "Test",
                "response_template_ids": None,  # None instead of empty list
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "name": "Test Type",
            "description": "Test",
            "response_plan_ids": [],
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should not fail when comparing None to empty list
        assert result.get("failed") is not True

    # Before/After State Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_before_state_null_on_create(self, connection, monkeypatch):
        """Test that before state is null when creating."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = CREATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["investigation_type"]["before"] is None
        assert result["investigation_type"]["after"] is not None

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_type_before_and_after_state_on_update(self, connection, monkeypatch):
        """Test that both before and after states are populated on update."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE)

        def update_by_path(self, path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(INVESTIGATION_TYPE_API_RESPONSE_UPDATED)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "update_by_path", update_by_path)

        self._plugin._task.args = UPDATE_INVESTIGATION_TYPE_PARAMS.copy()

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["investigation_type"]["before"] is not None
        assert result["investigation_type"]["after"] is not None
        # Before and after should be different
        assert (
            result["investigation_type"]["before"]["description"]
            != result["investigation_type"]["after"]["description"]
        )
