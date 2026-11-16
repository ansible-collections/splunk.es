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
Unit tests for the splunk_notes action plugin and module utilities.
"""

import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_notes import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.notes import (
    build_note_api_path,
    build_notes_api_path,
    build_task_note_api_path,
    build_task_notes_api_path,
    map_note_from_api,
    map_note_to_api,
    validate_target_params,
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


# Test data
FINDING_REF_ID = "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
INVESTIGATION_UUID = "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
RESPONSE_PLAN_UUID = "b9ef7dce-6dcd-4900-b5d5-982fc194554a"
PHASE_UUID = "phase-001-uuid"
TASK_UUID = "task-001-uuid"
NOTE_UUID = "note-abc123"

# Note API response
NOTE_RESPONSE = {
    "id": NOTE_UUID,
    "content": "This is the note content.",
}

NOTE_RESPONSE_MINIMAL = {
    "id": NOTE_UUID,
    "content": "Minimal note content.",
}


class TestNotesModuleUtils:
    """Tests for the notes module utility functions."""

    # Path Builder Tests
    def test_build_notes_api_path_defaults(self):
        """Test building notes path with default values."""
        result = build_notes_api_path(INVESTIGATION_UUID)

        expected = (
            f"servicesNS/nobody/missioncontrol/public/v2/investigations/{INVESTIGATION_UUID}/notes"
        )
        assert result == expected

    def test_build_notes_api_path_custom(self):
        """Test building notes path with custom values."""
        result = build_notes_api_path(
            investigation_id=INVESTIGATION_UUID,
            namespace="customNS",
            user="customuser",
            app="CustomApp",
        )

        expected = (
            f"customNS/customuser/CustomApp/public/v2/investigations/{INVESTIGATION_UUID}/notes"
        )
        assert result == expected

    def test_build_note_api_path_defaults(self):
        """Test building specific note path with default values."""
        result = build_note_api_path(INVESTIGATION_UUID, NOTE_UUID)

        expected = f"servicesNS/nobody/missioncontrol/public/v2/investigations/{INVESTIGATION_UUID}/notes/{NOTE_UUID}"
        assert result == expected

    def test_build_note_api_path_custom(self):
        """Test building specific note path with custom values."""
        result = build_note_api_path(
            investigation_id=INVESTIGATION_UUID,
            note_id=NOTE_UUID,
            namespace="customNS",
            user="customuser",
            app="CustomApp",
        )

        expected = f"customNS/customuser/CustomApp/public/v2/investigations/{INVESTIGATION_UUID}/notes/{NOTE_UUID}"
        assert result == expected

    def test_build_task_notes_api_path_defaults(self):
        """Test building task notes path with default values."""
        result = build_task_notes_api_path(
            investigation_id=INVESTIGATION_UUID,
            response_plan_id=RESPONSE_PLAN_UUID,
            phase_id=PHASE_UUID,
            task_id=TASK_UUID,
        )

        expected = (
            f"servicesNS/nobody/missioncontrol/public/v2/investigations/{INVESTIGATION_UUID}"
            f"/responseplans/{RESPONSE_PLAN_UUID}/phase/{PHASE_UUID}/tasks/{TASK_UUID}/notes"
        )
        assert result == expected

    def test_build_task_notes_api_path_custom(self):
        """Test building task notes path with custom values."""
        result = build_task_notes_api_path(
            investigation_id=INVESTIGATION_UUID,
            response_plan_id=RESPONSE_PLAN_UUID,
            phase_id=PHASE_UUID,
            task_id=TASK_UUID,
            namespace="customNS",
            user="customuser",
            app="CustomApp",
        )

        expected = (
            f"customNS/customuser/CustomApp/public/v2/investigations/{INVESTIGATION_UUID}"
            f"/responseplans/{RESPONSE_PLAN_UUID}/phase/{PHASE_UUID}/tasks/{TASK_UUID}/notes"
        )
        assert result == expected

    def test_build_task_note_api_path_defaults(self):
        """Test building specific task note path with default values."""
        result = build_task_note_api_path(
            investigation_id=INVESTIGATION_UUID,
            response_plan_id=RESPONSE_PLAN_UUID,
            phase_id=PHASE_UUID,
            task_id=TASK_UUID,
            note_id=NOTE_UUID,
        )

        expected = (
            f"servicesNS/nobody/missioncontrol/public/v2/investigations/{INVESTIGATION_UUID}"
            f"/responseplans/{RESPONSE_PLAN_UUID}/phase/{PHASE_UUID}/tasks/{TASK_UUID}/notes/{NOTE_UUID}"
        )
        assert result == expected

    # Mapping Tests
    def test_map_note_from_api_full(self):
        """Test mapping a full note response from API."""
        result = map_note_from_api(copy.deepcopy(NOTE_RESPONSE))

        assert result["note_id"] == NOTE_UUID
        assert result["content"] == "This is the note content."

    def test_map_note_from_api_minimal(self):
        """Test mapping a minimal note response from API."""
        result = map_note_from_api(copy.deepcopy(NOTE_RESPONSE_MINIMAL))

        assert result["note_id"] == NOTE_UUID
        assert result["content"] == "Minimal note content."

    def test_map_note_from_api_empty(self):
        """Test mapping an empty note response from API."""
        result = map_note_from_api({})

        assert result["note_id"] == ""
        assert result["content"] == ""

    def test_map_note_to_api(self):
        """Test mapping a note to API payload."""
        note = {"content": "Test content"}

        result = map_note_to_api(note)

        assert result["content"] == "Test content"


class TestEsNotesActionPlugin:
    """Test class for the splunk_notes action plugin."""

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
        self._plugin._task.action = "splunk_notes"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Finding Notes Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_create_finding_note_success(self, connection, monkeypatch):
        """Test successful creation of a finding note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(NOTE_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "finding",
            "finding_ref_id": FINDING_REF_ID,
            "content": "This is a test note.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "note" in result
        assert result["note"]["after"]["note_id"] == NOTE_UUID
        assert "created" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_create_finding_note_minimal(self, connection, monkeypatch):
        """Test creating a finding note with minimal parameters (only content)."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(NOTE_RESPONSE_MINIMAL)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "finding",
            "finding_ref_id": FINDING_REF_ID,
            "content": "Minimal note content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    # Investigation Notes Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_create_investigation_note_success(self, connection, monkeypatch):
        """Test successful creation of an investigation note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(NOTE_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "content": "Investigation note content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "created" in _get_msg_str(result)

    # Response Plan Task Notes Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_create_task_note_success(self, connection, monkeypatch):
        """Test successful creation of a response plan task note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return copy.deepcopy(NOTE_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "response_plan_task",
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan_id": RESPONSE_PLAN_UUID,
            "phase_id": PHASE_UUID,
            "task_id": TASK_UUID,
            "content": "Task note content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True

    # Update Note Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_update_note_success(self, connection, monkeypatch):
        """Test successful update of an existing note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": [copy.deepcopy(NOTE_RESPONSE)]}

        updated_response = copy.deepcopy(NOTE_RESPONSE)
        updated_response["content"] = "Updated content."

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            return updated_response

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID,
            "content": "Updated content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert "updated" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_update_note_idempotent(self, connection, monkeypatch):
        """Test that update is idempotent when content is the same."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": [copy.deepcopy(NOTE_RESPONSE)]}

        update_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            update_called.append(True)
            return copy.deepcopy(NOTE_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID,
            "content": "This is the note content.",  # Same as NOTE_RESPONSE
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(update_called) == 0  # API should not be called
        assert "no change" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_update_note_not_found(self, connection, monkeypatch):
        """Test update when note doesn't exist."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": "non-existent-note",
            "content": "Some content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "not found" in _get_msg_str(result)

    # Delete Note Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_delete_note_success(self, connection, monkeypatch):
        """Test successful deletion of a note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": [copy.deepcopy(NOTE_RESPONSE)]}

        delete_called = []

        def delete_by_path(self, path):
            delete_called.append(path)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID,
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(delete_called) == 1
        assert NOTE_UUID in delete_called[0]
        assert "deleted" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_delete_note_already_absent(self, connection, monkeypatch):
        """Test deleting a note that doesn't exist returns changed=False."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {"items": []}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID,
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "already absent" in _get_msg_str(result) or "not found" in _get_msg_str(result)

    # Check Mode Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_create_note_check_mode(self, connection, monkeypatch):
        """Test check mode for creating a note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        create_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            create_called.append(True)
            return copy.deepcopy(NOTE_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "content": "Check mode test content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(create_called) == 0  # API should not be called
        assert "check mode" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_update_note_check_mode(self, connection, monkeypatch):
        """Test check mode for updating a note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return {"items": [copy.deepcopy(NOTE_RESPONSE)]}

        update_called = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            update_called.append(True)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID,
            "content": "Updated content for check mode.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(update_called) == 0  # API should not be called
        assert "check mode" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_delete_note_check_mode(self, connection, monkeypatch):
        """Test check mode for deleting a note."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        # Enable check mode
        self._plugin._task.check_mode = True

        def get_by_path(self, path, query_params=None):
            return {"items": [copy.deepcopy(NOTE_RESPONSE)]}

        delete_called = []

        def delete_by_path(self, path):
            delete_called.append(True)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)
        monkeypatch.setattr(SplunkRequest, "delete_by_path", delete_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID,
            "state": "absent",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert result.get("failed") is not True
        assert len(delete_called) == 0  # DELETE should not be called
        assert "check mode" in _get_msg_str(result)

    # Validation Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_target_type(self, connection):
        """Test that missing target_type returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "content": "Test content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_ref_id_for_finding(self, connection):
        """Test that missing ref_id for finding target returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "target_type": "finding",
            "content": "Test content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "finding_ref_id" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_investigation_ref_id_for_investigation(self, connection):
        """Test that missing investigation_ref_id for investigation target returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "target_type": "investigation",
            "content": "Test content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "investigation_ref_id" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_params_for_response_plan_task(self, connection):
        """Test that missing parameters for response_plan_task target returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "target_type": "response_plan_task",
            "investigation_ref_id": INVESTIGATION_UUID,
            # Missing response_plan_id, phase_id, task_id
            "content": "Test content.",
            "state": "present",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "response_plan_id" in _get_msg_str(result) or "phase_id" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_content_for_present_state(self, connection):
        """Test that missing content for state=present returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "state": "present",
            # Missing content
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "content" in _get_msg_str(result)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_note_id_for_absent_state(self, connection):
        """Test that missing note_id for state=absent returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "state": "absent",
            # Missing note_id
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "note_id" in _get_msg_str(result)

    # Custom API Path Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def create_update(self, rest_path, data=None, query_params=None, json_payload=False):
            captured_paths.append(rest_path)
            return copy.deepcopy(NOTE_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "create_update", create_update)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "content": "Test content.",
            "state": "present",
            "api_namespace": "customNS",
            "api_user": "customuser",
            "api_app": "CustomApp",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is True
        assert len(captured_paths) >= 1
        for path in captured_paths:
            assert "customNS" in path
            assert "customuser" in path
            assert "CustomApp" in path


class TestEsNotesHelperMethods:
    """Tests for the helper methods in the splunk_notes action plugin."""

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

        self._plugin._task.action = "splunk_notes"
        self._plugin._task.async_val = False

    def test_validate_target_params_finding_valid(self):
        """Test validation passes for finding with finding_ref_id."""
        args = {"finding_ref_id": FINDING_REF_ID}

        result = validate_target_params("finding", args)

        assert result is None

    def test_validate_target_params_finding_missing_finding_ref_id(self):
        """Test validation fails for finding without finding_ref_id."""
        args = {}

        result = validate_target_params("finding", args)

        assert result is not None
        assert "finding_ref_id" in result

    def test_validate_target_params_investigation_valid(self):
        """Test validation passes for investigation with investigation_ref_id."""
        args = {"investigation_ref_id": INVESTIGATION_UUID}

        result = validate_target_params("investigation", args)

        assert result is None

    def test_validate_target_params_investigation_missing_ref_id(self):
        """Test validation fails for investigation without investigation_ref_id."""
        args = {}

        result = validate_target_params("investigation", args)

        assert result is not None
        assert "investigation_ref_id" in result

    def test_validate_target_params_response_plan_task_valid(self):
        """Test validation passes for response_plan_task with all required params."""
        args = {
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan_id": RESPONSE_PLAN_UUID,
            "phase_id": PHASE_UUID,
            "task_id": TASK_UUID,
        }

        result = validate_target_params("response_plan_task", args)

        assert result is None

    def test_validate_target_params_response_plan_task_missing_params(self):
        """Test validation fails for response_plan_task with missing params."""
        args = {"investigation_ref_id": INVESTIGATION_UUID}

        result = validate_target_params("response_plan_task", args)

        assert result is not None
        assert "response_plan_id" in result

    def test_validate_state_params_present_valid(self):
        """Test validation passes for present state with content."""
        self._plugin._task.args = {"content": "Test content"}

        result = self._plugin._validate_state_params("present", None)

        assert result is None

    def test_validate_state_params_present_missing_content(self):
        """Test validation fails for present state without content."""
        self._plugin._task.args = {}

        result = self._plugin._validate_state_params("present", None)

        assert result is not None
        assert "content" in result

    def test_validate_state_params_absent_valid(self):
        """Test validation passes for absent state with note_id."""
        self._plugin._task.args = {}

        result = self._plugin._validate_state_params("absent", NOTE_UUID)

        assert result is None

    def test_validate_state_params_absent_missing_note_id(self):
        """Test validation fails for absent state without note_id."""
        self._plugin._task.args = {}

        result = self._plugin._validate_state_params("absent", None)

        assert result is not None
        assert "note_id" in result

    def test_compare_notes_same(self):
        """Test comparing identical notes returns False (no difference)."""
        existing = {"content": "Same content"}
        desired = {"content": "Same content"}

        result = self._plugin._compare_notes(existing, desired)

        assert result is False

    def test_compare_notes_different_content(self):
        """Test comparing notes with different content returns True."""
        existing = {"content": "Original content"}
        desired = {"content": "Updated content"}

        result = self._plugin._compare_notes(existing, desired)

        assert result is True

    def test_build_note_params(self):
        """Test building note parameters from task args."""
        self._plugin._task.args = {
            "content": "Test content",
        }

        result = self._plugin._build_note_params()

        assert result["content"] == "Test content"
