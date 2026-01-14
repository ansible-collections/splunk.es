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
Unit tests for the splunk_finding_info action plugin.

These tests verify that the splunk_finding_info action plugin works correctly for:
- Querying a specific finding by ref_id
- Querying findings by title (with filtering)
- Querying all findings
- Handling time range parameters (earliest/latest)
- Handling not found scenarios

The tests use mocking to simulate Splunk API responses
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

import copy
import tempfile

from unittest.mock import MagicMock, patch

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.splunk.es.plugins.action.splunk_finding_info import ActionModule
from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest


# Test data: API Response Payloads
# These represent what the Splunk API returns for findings queries.

FINDING_API_RESPONSE_SINGLE = {
    "finding_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
    "rule_title": "Suspicious Login Activity",
    "rule_description": "Multiple failed login attempts detected",
    "security_domain": "access",
    "risk_object": "testuser",
    "risk_object_type": "user",
    "risk_score": "50.0",
    "owner": "admin",
    "status": "1",
    "urgency": "high",
    "disposition": "disposition:6",
}

FINDING_API_RESPONSE_LIST = {
    "items": [
        {
            "finding_id": "finding-001@@notable@@time1768225865",
            "rule_title": "Suspicious Login Activity",
            "rule_description": "Multiple failed login attempts",
            "security_domain": "access",
            "risk_object": "testuser",
            "risk_object_type": "user",
            "risk_score": "50.0",
            "owner": "admin",
            "status": "1",
            "urgency": "high",
            "disposition": "disposition:6",
        },
        {
            "finding_id": "finding-002@@notable@@time1768225866",
            "rule_title": "Malware Detection",
            "rule_description": "Potential malware detected",
            "security_domain": "endpoint",
            "risk_object": "server01",
            "risk_object_type": "system",
            "risk_score": "80.0",
            "owner": "analyst",
            "status": "2",
            "urgency": "critical",
            "disposition": "disposition:1",
        },
        {
            "finding_id": "finding-003@@notable@@time1768225867",
            "rule_title": "Suspicious Login Activity",
            "rule_description": "Another login attempt",
            "security_domain": "access",
            "risk_object": "admin",
            "risk_object_type": "user",
            "risk_score": "45.0",
            "owner": "admin",
            "status": "1",
            "urgency": "medium",
            "disposition": "disposition:6",
        },
    ],
}

EMPTY_FINDINGS_RESPONSE = {
    "items": [],
}


class TestSplunkFindingInfo:
    """Test class for the splunk_finding_info action plugin.

    The splunk_finding_info module is a "read-only" info module that queries
    Splunk for findings without making changes. It should always return
    changed=False.

    Query modes:
    1. By ref_id: Returns a single specific finding
    2. By title: Returns all findings matching the exact title
    3. All: Returns all findings (when no filters provided)
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
        self._plugin._task.action = "splunk_finding_info"
        self._plugin._task.async_val = False

        # Task variables
        self._task_vars = {}

    # Query by ref_id Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_by_ref_id(self, connection, monkeypatch):
        """Test querying a specific finding by ref_id.

        When ref_id is provided, the module should query for that specific
        finding and return it in a list (for consistency with other query modes).
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            # When querying by ref_id, path includes the ref_id
            # Use deepcopy to prevent mutation of test data
            if "2008e99d" in path:
                return copy.deepcopy(FINDING_API_RESPONSE_SINGLE)
            return {}

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Info modules should always return changed=False
        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "findings" in result
        assert len(result["findings"]) == 1
        assert result["findings"][0]["title"] == "Suspicious Login Activity"
        assert (
            result["findings"][0]["ref_id"]
            == "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
        )

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_by_ref_id_not_found(self, connection, monkeypatch):
        """Test querying a non-existent finding by ref_id.

        When the finding doesn't exist, the module should return an empty
        list rather than failing.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {}  # Empty response = not found

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "non-existent-id@@notable@@time1234567890",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "findings" in result
        assert len(result["findings"]) == 0

    # Query by Title Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_by_title(self, connection, monkeypatch):
        """Test querying findings by title.

        When title is provided, the module should fetch all findings and
        filter by exact title match.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "title": "Suspicious Login Activity",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "findings" in result
        # Should return 2 findings with matching title (items 0 and 2)
        assert len(result["findings"]) == 2
        for finding in result["findings"]:
            assert finding["title"] == "Suspicious Login Activity"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_by_title_no_match(self, connection, monkeypatch):
        """Test querying by title with no matches.

        When no findings match the title, should return an empty list.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "title": "Non-Existent Finding Title",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["findings"]) == 0

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_by_title_exact_match(self, connection, monkeypatch):
        """Test that title filtering uses exact match.

        "Suspicious" should not match "Suspicious Login Activity".
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Partial title should not match
        self._plugin._task.args = {
            "title": "Suspicious",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert len(result["findings"]) == 0  # No exact match

    # Query All Findings Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_all(self, connection, monkeypatch):
        """Test querying all findings without filters.

        When no ref_id or title is provided, should return all findings.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert "findings" in result
        assert len(result["findings"]) == 3

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_all_empty(self, connection, monkeypatch):
        """Test querying all findings when none exist.

        Should return an empty list without error.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(EMPTY_FINDINGS_RESPONSE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(result["findings"]) == 0

    # Time Range Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_with_earliest(self, connection, monkeypatch):
        """Test that earliest time parameter is passed to API.

        The earliest parameter controls the time range for returned findings.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "earliest": "-7d",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        # Verify earliest was passed to API
        assert len(captured_params) > 0
        assert captured_params[0] is not None
        assert captured_params[0].get("earliest") == "-7d"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_with_latest(self, connection, monkeypatch):
        """Test that latest time parameter is passed to API."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "latest": "now",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(captured_params) > 0
        assert captured_params[0] is not None
        assert captured_params[0].get("latest") == "now"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_with_time_range(self, connection, monkeypatch):
        """Test that both earliest and latest are passed to API."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "earliest": "-30d",
            "latest": "-1d",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(captured_params) > 0
        assert captured_params[0].get("earliest") == "-30d"
        assert captured_params[0].get("latest") == "-1d"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_ref_id_extracts_time_from_ref_id(self, connection, monkeypatch):
        """Test that time is extracted from ref_id and user-provided time params are ignored.

        When querying by ref_id, the earliest time should be automatically extracted from
        the ref_id (format: uuid@@notable@@time{timestamp}), and any user-provided
        earliest/latest parameters should be ignored.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_params = []

        def get_by_path(self, path, query_params=None):
            captured_params.append(query_params)
            return copy.deepcopy(FINDING_API_RESPONSE_SINGLE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "earliest": "-7d",  # This should be ignored
            "latest": "now",  # This should be ignored
        }

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        assert len(captured_params) > 0
        # Time should be extracted from ref_id, not from user-provided params
        assert captured_params[0].get("earliest") == "1768225865"
        # latest should not be passed when querying by ref_id
        assert captured_params[0].get("latest") is None

    # Always Changed=False Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_always_changed_false(self, connection, monkeypatch):
        """Verify that info module always returns changed=False.

        Info modules are read-only and should never report changes.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        # Test with various query types
        test_cases = [
            {},  # All findings
            {"ref_id": "finding-001@@notable@@time1768225865"},  # By ref_id
            {"title": "Suspicious Login Activity"},  # By title
            {"earliest": "-7d"},  # With time filter
        ]

        for args in test_cases:
            self._plugin._task.args = args
            result = self._plugin.run(task_vars=self._task_vars)
            assert result["changed"] is False, f"Expected changed=False for args: {args}"

    # Custom API Path Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_custom_api_path(self, connection, monkeypatch):
        """Test that custom API path parameters are used."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        captured_paths = []

        def get_by_path(self, path, query_params=None):
            captured_paths.append(path)
            return copy.deepcopy(FINDING_API_RESPONSE_LIST)

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
    def test_finding_info_field_mapping(self, connection, monkeypatch):
        """Test that API fields are correctly mapped to module format.

        Verify that API field names (rule_title, risk_score) are converted
        to module field names (title, finding_score).
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_SINGLE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        finding = result["findings"][0]

        # Verify field mapping
        assert "title" in finding  # rule_title -> title
        assert "description" in finding  # rule_description -> description
        assert "entity" in finding  # risk_object -> entity
        assert "entity_type" in finding  # risk_object_type -> entity_type
        assert "finding_score" in finding  # risk_score -> finding_score

        # Verify status/disposition are converted to human-readable
        assert finding["status"] == "new"  # "1" -> "new"
        assert finding["disposition"] == "undetermined"  # "disposition:6" -> "undetermined"

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_finding_score_type(self, connection, monkeypatch):
        """Test that finding_score is converted to integer.

        The API returns risk_score as a string like "50.0", but the module
        should return it as an integer.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return copy.deepcopy(FINDING_API_RESPONSE_SINGLE)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
        }

        result = self._plugin.run(task_vars=self._task_vars)

        finding = result["findings"][0]
        assert finding["finding_score"] == 50
        assert isinstance(finding["finding_score"], int)

    # Priority Tests (ref_id takes precedence over title) #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_ref_id_priority(self, connection, monkeypatch):
        """Test that ref_id takes precedence over title when both are provided.

        If both ref_id and title are specified, the module should query
        by ref_id and ignore the title parameter.
        """
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        call_count = {"ref_id_calls": 0, "all_calls": 0}

        def get_by_path(self, path, query_params=None):
            if "2008e99d" in path:
                call_count["ref_id_calls"] += 1
                return copy.deepcopy(FINDING_API_RESPONSE_SINGLE)
            else:
                call_count["all_calls"] += 1
                return copy.deepcopy(FINDING_API_RESPONSE_LIST)

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {
            "ref_id": "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865",
            "title": "Some Other Title",  # Should be ignored
        }

        result = self._plugin.run(task_vars=self._task_vars)

        # Should have called the ref_id path, not the all-findings path
        assert call_count["ref_id_calls"] == 1
        assert call_count["all_calls"] == 0
        assert len(result["findings"]) == 1

    # Error Handling Tests #
    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_handles_null_items(self, connection, monkeypatch):
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
                    copy.deepcopy(FINDING_API_RESPONSE_LIST["items"][0]),
                    None,  # Another null
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
        # Should only have 1 valid finding (the null ones filtered out)
        assert len(result["findings"]) == 1

    @patch("ansible.module_utils.connection.Connection.__rpc__")
    def test_finding_info_handles_empty_items(self, connection, monkeypatch):
        """Test handling of empty dict items in API response."""
        self._plugin._connection.socket_path = tempfile.NamedTemporaryFile().name
        self._plugin._connection._shell = MagicMock()

        def get_by_path(self, path, query_params=None):
            return {
                "items": [
                    {},  # Empty item
                    copy.deepcopy(FINDING_API_RESPONSE_LIST["items"][0]),
                ],
            }

        monkeypatch.setattr(SplunkRequest, "get_by_path", get_by_path)

        self._plugin._task.args = {}

        result = self._plugin.run(task_vars=self._task_vars)

        assert result["changed"] is False
        assert result.get("failed") is not True
