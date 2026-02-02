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
Unit tests for the splunk_notes_info action plugin.

These tests verify that the splunk_notes_info action plugin works correctly for:
- Querying notes from findings, investigations, and response plan tasks
- Querying a specific note by note_id
- Querying all notes with limit parameter
- Handling not found scenarios (404 and MC_0050 errors)

The tests use mocking to simulate Splunk API responses.
"""

import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_notes_info import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.notes import validate_target_params
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
NOTE_UUID_1 = "note-abc123"
NOTE_UUID_2 = "note-def456"

# Note API responses (as returned by API in "items" array)
NOTES_API_RESPONSE = {
    "items": [
        {
            "id": NOTE_UUID_1,
            "content": "First note content.",
        },
        {
            "id": NOTE_UUID_2,
            "content": "Second note content.",
        },
    ],
    "offset": 0,
    "limit": 100,
    "total": 2,
}

SINGLE_NOTE_API_RESPONSE = {
    "id": NOTE_UUID_1,
    "content": "First note content.",
}

EMPTY_NOTES_RESPONSE = {
    "items": [],
    "offset": 0,
    "limit": 100,
    "total": 0,
}


class TestEsNotesInfo:
    """Test class for the splunk_notes_info action plugin.

    The splunk_notes_info module is a "read-only" info module that queries
    Splunk for notes without making changes. It should always return
    changed=False.

    Query modes:
    1. All notes: Returns all notes for the target (with optional limit)
    2. By note_id: Returns a specific note
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
        self._plugin._task.action = "splunk_notes_info"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Finding Notes Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_notes_all(self, connection, monkeypatch):
        """Test querying all notes from a finding."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "finding",
            "finding_ref_id": FINDING_REF_ID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "notes" in result
        assert len(result["notes"]) == 2
        assert result["notes"][0]["note_id"] == NOTE_UUID_1
        assert result["notes"][1]["note_id"] == NOTE_UUID_2

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_notes_by_id(self, connection, monkeypatch):
        """Test querying a specific note from a finding by note_id."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            # Finding/investigation use filtered lookup, so return all notes
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "finding",
            "finding_ref_id": FINDING_REF_ID,
            "note_id": NOTE_UUID_1,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["notes"]) == 1
        assert result["notes"][0]["note_id"] == NOTE_UUID_1

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_notes_notable_time_extracted(self, connection, monkeypatch):
        """Test that notable_time is extracted from finding_ref_id for API query."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "finding",
            "finding_ref_id": FINDING_REF_ID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        # Verify notable_time was extracted and passed to API
        assert len(captured_params) > 0
        assert "notable_time" in captured_params[0]
        assert captured_params[0]["notable_time"] == "1768225865"

    # Investigation Notes Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_notes_all(self, connection, monkeypatch):
        """Test querying all notes from an investigation."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["notes"]) == 2

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_investigation_notes_by_id(self, connection, monkeypatch):
        """Test querying a specific note from an investigation by note_id."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID_2,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["notes"]) == 1
        assert result["notes"][0]["note_id"] == NOTE_UUID_2

    # Response Plan Task Notes Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_notes_all(self, connection, monkeypatch):
        """Test querying all notes from a response plan task."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "response_plan_task",
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan_id": RESPONSE_PLAN_UUID,
            "phase_id": PHASE_UUID,
            "task_id": TASK_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["notes"]) == 2

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_task_notes_by_id_direct_lookup(self, connection, monkeypatch):
        """Test querying a specific task note by ID uses direct API lookup."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            # Direct lookup returns single note dict, not wrapped in items
            return copy.deepcopy(SINGLE_NOTE_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "response_plan_task",
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan_id": RESPONSE_PLAN_UUID,
            "phase_id": PHASE_UUID,
            "task_id": TASK_UUID,
            "note_id": NOTE_UUID_1,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["notes"]) == 1
        # Verify direct note path was used (contains note_id in path)
        assert len(captured_paths) == 1
        assert NOTE_UUID_1 in captured_paths[0]

    # Limit Parameter Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_limit_parameter_default(self, connection, monkeypatch):
        """Test that default limit (100) is used when not specified."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(captured_params) > 0
        assert captured_params[0]["limit"] == 100

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_limit_parameter_custom(self, connection, monkeypatch):
        """Test that custom limit is passed to API."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "limit": 10,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(captured_params) > 0
        assert captured_params[0]["limit"] == 10

    # Empty Results Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_empty_notes_response(self, connection, monkeypatch):
        """Test handling of empty notes response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_NOTES_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["notes"] == []

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_note_by_id_not_found(self, connection, monkeypatch):
        """Test querying a non-existent note by ID returns empty list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": "non-existent-note-id",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["notes"] == []

    # Error Handling Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_handles_404_error(self, connection, monkeypatch):
        """Test graceful handling of 404 errors."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("HTTP Error 404: Not Found")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should return empty list, not fail
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["notes"] == []

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_handles_mc_0050_error(self, connection, monkeypatch):
        """Test graceful handling of MC_0050 (internal server error for missing resource)."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception(
                "Splunk httpapi returned error 500 with message "
                "{'code': 'MC_0050', 'message': 'Internal server error'}",
            )

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "response_plan_task",
            "investigation_ref_id": INVESTIGATION_UUID,
            "response_plan_id": RESPONSE_PLAN_UUID,
            "phase_id": PHASE_UUID,
            "task_id": TASK_UUID,
            "note_id": "deleted-note-id",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should return empty list, not fail
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert result["notes"] == []

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_handles_other_errors(self, connection, monkeypatch):
        """Test that other errors properly fail the module."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            raise Exception("Connection timeout error")

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        try:
            self._plugin.run(task_vars=self._task_vars)
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Connection timeout" in str(e) or "Failed to query" in str(e)

    # Validation Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_target_type(self, connection):
        """Test that missing target_type returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_missing_finding_ref_id_for_finding(self, connection):
        """Test that missing finding_ref_id for finding target returns an error."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        self._plugin._task.args = {
            "target_type": "finding",
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
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["failed"] is True
        assert "response_plan_id" in _get_msg_str(result) or "phase_id" in _get_msg_str(result)

    # Custom API Path Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "api_namespace": "customNS",
            "api_user": "customuser",
            "api_app": "CustomApp",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(captured_paths) > 0
        assert "customNS" in captured_paths[0]
        assert "customuser" in captured_paths[0]
        assert "CustomApp" in captured_paths[0]

    # Always Changed=False Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_always_changed_false(self, connection, monkeypatch):
        """Verify that info module always returns changed=False.

        Info modules are read-only and should never report changes.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Test with various query types
        test_cases = [
            {
                "target_type": "investigation",
                "investigation_ref_id": INVESTIGATION_UUID,
            },
            {
                "target_type": "investigation",
                "investigation_ref_id": INVESTIGATION_UUID,
                "note_id": NOTE_UUID_1,
            },
            {
                "target_type": "finding",
                "finding_ref_id": FINDING_REF_ID,
            },
            {
                "target_type": "investigation",
                "investigation_ref_id": INVESTIGATION_UUID,
                "limit": 10,
            },
        ]

        for args in test_cases:
            self._plugin._task.args = args
            result = self._plugin.run(task_vars=self._task_vars)
            assert result["changed"] is False, f"Expected changed=False for args: {args}"

    # Field Mapping Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_field_mapping(self, connection, monkeypatch):
        """Test that API fields are correctly mapped to module format."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        note = result["notes"][0]

        # Verify field mapping (id -> note_id)
        assert "note_id" in note
        assert "content" in note
        assert note["note_id"] == NOTE_UUID_1
        assert note["content"] == "First note content."

    # Consistency Tests
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_returns_list(self, connection, monkeypatch):
        """Test that notes are always returned as a list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["notes"], list)

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_single_note_returns_list(self, connection, monkeypatch):
        """Test that even single note query returns a list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(NOTES_API_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
            "note_id": NOTE_UUID_1,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["notes"], list)
        assert len(result["notes"]) == 1

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_empty_returns_list(self, connection, monkeypatch):
        """Test that empty results are returned as an empty list."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_NOTES_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "target_type": "investigation",
            "investigation_ref_id": INVESTIGATION_UUID,
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert isinstance(result["notes"], list)
        assert len(result["notes"]) == 0


class TestEsNotesInfoHelperMethods:
    """Tests for the helper methods in the splunk_notes_info action plugin."""

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

        self._plugin._task.action = "splunk_notes_info"
        self._plugin._task.async_val = False

    def test_validate_target_params_finding_valid(self):
        """Test validation passes for finding with finding_ref_id."""
        args = {"finding_ref_id": FINDING_REF_ID}

        result = validate_target_params("finding", args)

        assert result is None

    def test_validate_target_params_finding_missing(self):
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

    def test_validate_target_params_investigation_missing(self):
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

    def test_validate_target_params_response_plan_task_missing(self):
        """Test validation fails for response_plan_task with missing params."""
        args = {"investigation_ref_id": INVESTIGATION_UUID}

        result = validate_target_params("response_plan_task", args)

        assert result is not None
        assert "response_plan_id" in result
