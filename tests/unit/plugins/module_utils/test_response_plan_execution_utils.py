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
Unit tests for the response_plan_execution module utilities.
"""

import copy

from ansible_collections.splunk.es.plugins.module_utils.response_plan_execution import (
    TASK_STATUS_FROM_API,
    map_applied_response_plan_from_api,
    map_phase_from_api,
    map_task_from_api,
)


class TestTaskStatusFromApiMapping:
    """Tests for the TASK_STATUS_FROM_API constant mapping."""

    def test_started_status_mapping(self):
        """Test that 'Started' API status maps to 'started'."""
        assert TASK_STATUS_FROM_API["Started"] == "started"

    def test_ended_status_mapping(self):
        """Test that 'Ended' API status maps to 'ended'."""
        assert TASK_STATUS_FROM_API["Ended"] == "ended"

    def test_reopened_status_mapping(self):
        """Test that 'Reopened' API status maps to 'reopened'."""
        assert TASK_STATUS_FROM_API["Reopened"] == "reopened"

    def test_pending_status_mapping(self):
        """Test that 'Pending' API status maps to 'pending'."""
        assert TASK_STATUS_FROM_API["Pending"] == "pending"

    def test_all_statuses_are_lowercase(self):
        """Test that all mapped values are lowercase."""
        for api_status, module_status in TASK_STATUS_FROM_API.items():
            assert module_status == module_status.lower()


class TestMapTaskFromApi:
    """Tests for the map_task_from_api function."""

    def test_complete_task_mapping(self):
        """Test mapping a task with all fields populated."""
        api_task = {
            "id": "task-001-uuid",
            "name": "Initial Triage",
            "description": "Perform initial assessment of the incident",
            "owner": "admin",
            "is_note_required": True,
            "status": "Started",
        }

        result = map_task_from_api(api_task)

        assert result["id"] == "task-001-uuid"
        assert result["name"] == "Initial Triage"
        assert result["description"] == "Perform initial assessment of the incident"
        assert result["owner"] == "admin"
        assert result["is_note_required"] is True
        assert result["status"] == "started"

    def test_minimal_task_mapping(self):
        """Test mapping a task with only required fields."""
        api_task = {
            "name": "Minimal Task",
        }

        result = map_task_from_api(api_task)

        assert result["id"] == ""
        assert result["name"] == "Minimal Task"
        assert result["description"] == ""
        assert result["owner"] == "unassigned"
        assert result["is_note_required"] is False
        assert result["status"] == ""

    def test_empty_task_mapping(self):
        """Test mapping an empty task dictionary."""
        result = map_task_from_api({})

        assert result["id"] == ""
        assert result["name"] == ""
        assert result["description"] == ""
        assert result["owner"] == "unassigned"
        assert result["is_note_required"] is False
        assert result["status"] == ""

    def test_status_pending_mapping(self):
        """Test that 'Pending' status is correctly mapped."""
        api_task = {
            "name": "Test Task",
            "status": "Pending",
        }

        result = map_task_from_api(api_task)

        assert result["status"] == "pending"

    def test_status_started_mapping(self):
        """Test that 'Started' status is correctly mapped."""
        api_task = {
            "name": "Test Task",
            "status": "Started",
        }

        result = map_task_from_api(api_task)

        assert result["status"] == "started"

    def test_status_ended_mapping(self):
        """Test that 'Ended' status is correctly mapped."""
        api_task = {
            "name": "Test Task",
            "status": "Ended",
        }

        result = map_task_from_api(api_task)

        assert result["status"] == "ended"

    def test_unknown_status_lowercase(self):
        """Test that unknown statuses are converted to lowercase."""
        api_task = {
            "name": "Test Task",
            "status": "UNKNOWN_STATUS",
        }

        result = map_task_from_api(api_task)

        assert result["status"] == "unknown_status"

    def test_url_encoded_name_decoded(self):
        """Test that URL-encoded name is decoded."""
        api_task = {
            "name": "task%201",
            "description": "description%20text",
        }

        result = map_task_from_api(api_task)

        assert result["name"] == "task 1"
        assert result["description"] == "description text"

    def test_url_encoded_special_characters(self):
        """Test decoding of various URL-encoded characters."""
        api_task = {
            "name": "task%20with%20spaces%20%26%20special",
            "description": "description%3A%20test%21",
        }

        result = map_task_from_api(api_task)

        assert result["name"] == "task with spaces & special"
        assert result["description"] == "description: test!"

    def test_boolean_is_note_required_true(self):
        """Test that is_note_required True is preserved."""
        api_task = {
            "name": "Test",
            "is_note_required": True,
        }

        result = map_task_from_api(api_task)

        assert result["is_note_required"] is True

    def test_boolean_is_note_required_false(self):
        """Test that is_note_required False is preserved."""
        api_task = {
            "name": "Test",
            "is_note_required": False,
        }

        result = map_task_from_api(api_task)

        assert result["is_note_required"] is False


class TestMapPhaseFromApi:
    """Tests for the map_phase_from_api function."""

    def test_complete_phase_mapping(self):
        """Test mapping a phase with all fields and tasks."""
        api_phase = {
            "id": "phase-001-uuid",
            "name": "Investigation",
            "tasks": [
                {
                    "id": "task-001-uuid",
                    "name": "Initial Triage",
                    "description": "Perform assessment",
                    "status": "Pending",
                    "owner": "admin",
                    "is_note_required": True,
                },
                {
                    "id": "task-002-uuid",
                    "name": "Gather Evidence",
                    "description": "Collect logs",
                    "status": "Started",
                    "owner": "analyst",
                    "is_note_required": False,
                },
            ],
        }

        result = map_phase_from_api(api_phase)

        assert result["id"] == "phase-001-uuid"
        assert result["name"] == "Investigation"
        assert len(result["tasks"]) == 2
        assert result["tasks"][0]["name"] == "Initial Triage"
        assert result["tasks"][0]["status"] == "pending"
        assert result["tasks"][1]["name"] == "Gather Evidence"
        assert result["tasks"][1]["status"] == "started"

    def test_phase_with_no_tasks(self):
        """Test mapping a phase with empty tasks list."""
        api_phase = {
            "id": "phase-001-uuid",
            "name": "Empty Phase",
            "tasks": [],
        }

        result = map_phase_from_api(api_phase)

        assert result["id"] == "phase-001-uuid"
        assert result["name"] == "Empty Phase"
        assert result["tasks"] == []

    def test_phase_with_null_tasks(self):
        """Test mapping a phase with null tasks."""
        api_phase = {
            "id": "phase-001-uuid",
            "name": "Phase with null tasks",
            "tasks": None,
        }

        result = map_phase_from_api(api_phase)

        assert result["id"] == "phase-001-uuid"
        assert result["tasks"] == []

    def test_minimal_phase_mapping(self):
        """Test mapping a phase with only name."""
        api_phase = {
            "name": "Minimal Phase",
        }

        result = map_phase_from_api(api_phase)

        assert result["id"] == ""
        assert result["name"] == "Minimal Phase"
        assert result["tasks"] == []

    def test_empty_phase_mapping(self):
        """Test mapping an empty phase dictionary."""
        result = map_phase_from_api({})

        assert result["id"] == ""
        assert result["name"] == ""
        assert result["tasks"] == []

    def test_url_encoded_name_decoded(self):
        """Test that URL-encoded phase name is decoded."""
        api_phase = {
            "id": "phase-001-uuid",
            "name": "phase%201",
            "tasks": [],
        }

        result = map_phase_from_api(api_phase)

        assert result["name"] == "phase 1"

    def test_tasks_are_mapped_correctly(self):
        """Test that each task is mapped using map_task_from_api."""
        api_phase = {
            "id": "phase-001-uuid",
            "name": "Test Phase",
            "tasks": [
                {
                    "id": "task-001",
                    "name": "task%201",
                    "description": "task%20description",
                    "status": "Started",
                    "owner": "admin",
                    "is_note_required": True,
                },
            ],
        }

        result = map_phase_from_api(api_phase)

        task = result["tasks"][0]
        # Verify task was properly mapped with URL decoding
        assert task["name"] == "task 1"
        assert task["description"] == "task description"
        assert task["status"] == "started"


class TestMapAppliedResponsePlanFromApi:
    """Tests for the map_applied_response_plan_from_api function."""

    def test_complete_plan_mapping(self):
        """Test mapping a complete applied response plan."""
        api_plan = {
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
                            "description": "Perform assessment",
                            "status": "Pending",
                            "owner": "admin",
                            "is_note_required": True,
                        },
                    ],
                },
                {
                    "id": "phase-002-uuid",
                    "name": "Containment",
                    "tasks": [],
                },
            ],
        }

        result = map_applied_response_plan_from_api(api_plan)

        assert result["id"] == "applied-plan-001-uuid"
        assert result["name"] == "Incident Response Plan"
        assert result["description"] == "Standard incident response procedure"
        assert result["source_template_id"] == "template-001-uuid"
        assert len(result["phases"]) == 2
        assert result["phases"][0]["name"] == "Investigation"
        assert result["phases"][1]["name"] == "Containment"

    def test_minimal_plan_mapping(self):
        """Test mapping a plan with minimal fields."""
        api_plan = {
            "name": "Minimal Plan",
        }

        result = map_applied_response_plan_from_api(api_plan)

        assert result["id"] == ""
        assert result["name"] == "Minimal Plan"
        assert result["description"] == ""
        assert result["source_template_id"] == ""
        assert result["phases"] == []

    def test_empty_plan_mapping(self):
        """Test mapping an empty plan dictionary."""
        result = map_applied_response_plan_from_api({})

        assert result["id"] == ""
        assert result["name"] == ""
        assert result["description"] == ""
        assert result["source_template_id"] == ""
        assert result["phases"] == []

    def test_source_template_id_from_template_id(self):
        """Test that template_id from GET response is used for source_template_id."""
        api_plan = {
            "name": "Test Plan",
            "template_id": "template-from-get-uuid",
        }

        result = map_applied_response_plan_from_api(api_plan)

        assert result["source_template_id"] == "template-from-get-uuid"

    def test_source_template_id_from_source_template_id(self):
        """Test that source_template_id from POST response takes precedence."""
        api_plan = {
            "name": "Test Plan",
            "source_template_id": "template-from-post-uuid",
            "template_id": "template-from-get-uuid",
        }

        result = map_applied_response_plan_from_api(api_plan)

        # source_template_id should take precedence over template_id
        assert result["source_template_id"] == "template-from-post-uuid"

    def test_null_phases_handled(self):
        """Test that null phases are handled gracefully."""
        api_plan = {
            "id": "plan-001-uuid",
            "name": "Plan with null phases",
            "phases": None,
        }

        result = map_applied_response_plan_from_api(api_plan)

        assert result["phases"] == []

    def test_empty_phases_list(self):
        """Test that empty phases list is preserved."""
        api_plan = {
            "id": "plan-001-uuid",
            "name": "Plan with empty phases",
            "phases": [],
        }

        result = map_applied_response_plan_from_api(api_plan)

        assert result["phases"] == []

    def test_url_encoded_name_and_description_decoded(self):
        """Test that URL-encoded name and description are decoded."""
        api_plan = {
            "id": "plan-001-uuid",
            "name": "Incident%20Response%20Plan",
            "description": "Standard%20incident%20response",
            "phases": [],
        }

        result = map_applied_response_plan_from_api(api_plan)

        assert result["name"] == "Incident Response Plan"
        assert result["description"] == "Standard incident response"

    def test_phases_are_mapped_correctly(self):
        """Test that each phase is mapped using map_phase_from_api."""
        api_plan = {
            "id": "plan-001-uuid",
            "name": "Test Plan",
            "phases": [
                {
                    "id": "phase-001-uuid",
                    "name": "phase%201",
                    "tasks": [
                        {
                            "id": "task-001-uuid",
                            "name": "task%201",
                            "status": "Started",
                            "owner": "admin",
                        },
                    ],
                },
            ],
        }

        result = map_applied_response_plan_from_api(api_plan)

        phase = result["phases"][0]
        # Verify phase was properly mapped with URL decoding
        assert phase["name"] == "phase 1"
        # Verify nested task was also mapped
        assert phase["tasks"][0]["name"] == "task 1"
        assert phase["tasks"][0]["status"] == "started"

    def test_deep_nesting_preserved(self):
        """Test that deep nesting of phases and tasks is preserved."""
        api_plan = {
            "id": "plan-001-uuid",
            "name": "Complex Plan",
            "description": "Plan with multiple phases and tasks",
            "template_id": "template-001-uuid",
            "phases": [
                {
                    "id": "phase-001-uuid",
                    "name": "Phase 1",
                    "tasks": [
                        {
                            "id": "task-001-uuid",
                            "name": "Task 1.1",
                            "description": "First task",
                            "status": "Ended",
                            "owner": "admin",
                            "is_note_required": True,
                        },
                        {
                            "id": "task-002-uuid",
                            "name": "Task 1.2",
                            "description": "Second task",
                            "status": "Started",
                            "owner": "analyst",
                            "is_note_required": False,
                        },
                    ],
                },
                {
                    "id": "phase-002-uuid",
                    "name": "Phase 2",
                    "tasks": [
                        {
                            "id": "task-003-uuid",
                            "name": "Task 2.1",
                            "description": "Third task",
                            "status": "Pending",
                            "owner": "unassigned",
                            "is_note_required": False,
                        },
                    ],
                },
                {
                    "id": "phase-003-uuid",
                    "name": "Phase 3",
                    "tasks": [],
                },
            ],
        }

        result = map_applied_response_plan_from_api(api_plan)

        # Verify structure
        assert len(result["phases"]) == 3
        assert len(result["phases"][0]["tasks"]) == 2
        assert len(result["phases"][1]["tasks"]) == 1
        assert len(result["phases"][2]["tasks"]) == 0

        # Verify nested data
        assert result["phases"][0]["tasks"][0]["status"] == "ended"
        assert result["phases"][0]["tasks"][1]["status"] == "started"
        assert result["phases"][1]["tasks"][0]["status"] == "pending"


class TestMappingImmutability:
    """Tests to verify that mapping functions don't modify input data."""

    def test_map_task_does_not_modify_input(self):
        """Test that map_task_from_api doesn't modify the input dict."""
        original_task = {
            "id": "task-001",
            "name": "Original Name",
            "description": "Original Description",
            "status": "Pending",
            "owner": "admin",
            "is_note_required": True,
        }
        task_copy = copy.deepcopy(original_task)

        map_task_from_api(original_task)

        assert original_task == task_copy

    def test_map_phase_does_not_modify_input(self):
        """Test that map_phase_from_api doesn't modify the input dict."""
        original_phase = {
            "id": "phase-001",
            "name": "Original Phase",
            "tasks": [
                {"id": "task-001", "name": "Task", "status": "Pending"},
            ],
        }
        phase_copy = copy.deepcopy(original_phase)

        map_phase_from_api(original_phase)

        assert original_phase == phase_copy

    def test_map_plan_does_not_modify_input(self):
        """Test that map_applied_response_plan_from_api doesn't modify the input."""
        original_plan = {
            "id": "plan-001",
            "name": "Original Plan",
            "description": "Original Description",
            "template_id": "template-001",
            "phases": [
                {
                    "id": "phase-001",
                    "name": "Phase",
                    "tasks": [
                        {"id": "task-001", "name": "Task", "status": "Pending"},
                    ],
                },
            ],
        }
        plan_copy = copy.deepcopy(original_plan)

        map_applied_response_plan_from_api(original_plan)

        assert original_plan == plan_copy
