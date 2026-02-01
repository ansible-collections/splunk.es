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
Unit tests for the investigation module utilities.

These tests verify that the utility functions work correctly for:
- Building API paths
- Mapping between API and module parameter formats
- Status, disposition, and sensitivity value conversions

Shared utilities are in plugins/module_utils/investigation.py
Main-only utilities are in plugins/action/splunk_investigation.py
"""


# Main-only utilities via ActionModule class
from ansible_collections.splunk.es.plugins.action.splunk_investigation import ActionModule

# Shared utilities (used by both info and main modules)
from ansible_collections.splunk.es.plugins.module_utils.investigation import (
    SENSITIVITY_FROM_API,
    build_investigation_api_path,
    map_investigation_from_api,
)

# Shared constants from splunk_utils
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    DISPOSITION_FROM_API,
    DISPOSITION_TO_API,
    STATUS_FROM_API,
    STATUS_TO_API,
)


class TestBuildInvestigationApiPath:
    """Tests for the build_investigation_api_path function.

    This function constructs the REST API path for the investigations endpoint.
    It should handle default values and custom namespace/user/app overrides.
    """

    def test_build_investigation_api_path_defaults(self):
        """Test that default API path is constructed correctly.

        When called without arguments, should use the default namespace,
        user, and app values defined in the module.
        """
        result = build_investigation_api_path()

        expected = (
            f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations"
        )
        assert result == expected

    def test_build_investigation_api_path_custom_namespace(self):
        """Test API path with custom namespace value."""
        result = build_investigation_api_path(namespace="customNS")

        expected = f"customNS/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations"
        assert result == expected

    def test_build_investigation_api_path_custom_user(self):
        """Test API path with custom user value."""
        result = build_investigation_api_path(user="admin")

        expected = f"{DEFAULT_API_NAMESPACE}/admin/{DEFAULT_API_APP}/public/v2/investigations"
        assert result == expected

    def test_build_investigation_api_path_custom_app(self):
        """Test API path with custom app value."""
        result = build_investigation_api_path(app="CustomApp")

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/CustomApp/public/v2/investigations"
        assert result == expected

    def test_build_investigation_api_path_all_custom(self):
        """Test API path with all custom values."""
        result = build_investigation_api_path(
            namespace="myNS",
            user="myuser",
            app="MyApp",
        )

        assert result == "myNS/myuser/MyApp/public/v2/investigations"


class TestBuildInvestigationUpdatePath:
    """Tests for the ActionModule.build_update_path method.

    This method constructs the REST API path for updating a specific investigation.
    """

    def test_build_investigation_update_path_defaults(self):
        """Test update API path with default namespace and user."""
        ref_id = "inv-abc-123"
        result = ActionModule.build_update_path(ref_id)

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations/{ref_id}"
        assert result == expected

    def test_build_investigation_update_path_custom_namespace(self):
        """Test update API path with custom namespace."""
        ref_id = "inv-abc-123"
        result = ActionModule.build_update_path(ref_id, namespace="customNS")

        expected = (
            f"customNS/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations/{ref_id}"
        )
        assert result == expected

    def test_build_investigation_update_path_custom_user(self):
        """Test update API path with custom user."""
        ref_id = "inv-abc-123"
        result = ActionModule.build_update_path(ref_id, user="admin")

        expected = (
            f"{DEFAULT_API_NAMESPACE}/admin/{DEFAULT_API_APP}/public/v2/investigations/{ref_id}"
        )
        assert result == expected

    def test_build_investigation_update_path_guid_ref_id(self):
        """Test update API path with GUID-style ref_id."""
        ref_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        result = ActionModule.build_update_path(ref_id)

        assert ref_id in result


class TestBuildInvestigationFindingsPath:
    """Tests for the ActionModule.build_findings_path method.

    This method constructs the REST API path for adding findings to an investigation.
    """

    def test_build_investigation_findings_path_defaults(self):
        """Test findings API path with default values."""
        ref_id = "inv-abc-123"
        result = ActionModule.build_findings_path(ref_id)

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/public/v2/investigations/{ref_id}/findings"
        assert result == expected
        assert result.endswith("/findings")

    def test_build_investigation_findings_path_custom_namespace(self):
        """Test findings API path with custom namespace."""
        ref_id = "inv-abc-123"
        result = ActionModule.build_findings_path(ref_id, namespace="customNS")

        assert "customNS" in result
        assert result.endswith("/findings")

    def test_build_investigation_findings_path_includes_ref_id(self):
        """Test that ref_id is included in the path."""
        ref_id = "unique-investigation-id"
        result = ActionModule.build_findings_path(ref_id)

        assert ref_id in result


class TestMapInvestigationFromApi:
    """Tests for the map_investigation_from_api function.

    This function converts the API response format to the module parameter format.
    It handles key renaming, status/disposition/sensitivity conversion.
    """

    def test_map_investigation_from_api_basic(self):
        """Test basic field mapping from API to module format."""
        api_response = {
            "investigation_guid": "inv-12345",
            "name": "Test Investigation",
            "description": "A test description",
            "owner": "admin",
            "urgency": "high",
        }

        result = map_investigation_from_api(api_response)

        assert result["investigation_ref_id"] == "inv-12345"
        assert result["name"] == "Test Investigation"
        assert result["description"] == "A test description"
        assert result["owner"] == "admin"
        assert result["urgency"] == "high"

    def test_map_investigation_from_api_with_investigation_guid(self):
        """Test that investigation_guid is extracted as investigation_ref_id."""
        api_response = {
            "investigation_guid": "abc-123-def-456",
            "name": "Test Investigation",
        }

        result = map_investigation_from_api(api_response)

        assert result["investigation_ref_id"] == "abc-123-def-456"

    def test_map_investigation_from_api_status_conversion(self):
        """Test that numeric status codes are converted to string names."""
        api_response = {
            "name": "Test",
            "status": "1",  # API uses numeric codes
        }

        result = map_investigation_from_api(api_response)

        assert result["status"] == "new"

    def test_map_investigation_from_api_all_status_values(self):
        """Test all status value conversions."""
        for api_value, module_value in STATUS_FROM_API.items():
            api_response = {"name": "Test", "status": api_value}
            result = map_investigation_from_api(api_response)
            assert result["status"] == module_value

    def test_map_investigation_from_api_disposition_conversion(self):
        """Test that disposition codes are converted to string names."""
        api_response = {
            "name": "Test",
            "disposition": "disposition:6",  # API format
        }

        result = map_investigation_from_api(api_response)

        assert result["disposition"] == "undetermined"

    def test_map_investigation_from_api_all_disposition_values(self):
        """Test all disposition value conversions."""
        for api_value, module_value in DISPOSITION_FROM_API.items():
            api_response = {"name": "Test", "disposition": api_value}
            result = map_investigation_from_api(api_response)
            assert result["disposition"] == module_value

    def test_map_investigation_from_api_sensitivity_conversion(self):
        """Test that capitalized sensitivity is converted to lowercase."""
        api_response = {
            "name": "Test",
            "sensitivity": "Amber",  # API uses capitalized
        }

        result = map_investigation_from_api(api_response)

        assert result["sensitivity"] == "amber"

    def test_map_investigation_from_api_all_sensitivity_values(self):
        """Test all sensitivity value conversions."""
        for api_value, module_value in SENSITIVITY_FROM_API.items():
            api_response = {"name": "Test", "sensitivity": api_value}
            result = map_investigation_from_api(api_response)
            assert result["sensitivity"] == module_value

    def test_map_investigation_from_api_with_findings(self):
        """Test extraction of finding_ids from consolidated_findings."""
        api_response = {
            "name": "Test",
            "consolidated_findings": {
                "event_id": ["finding-001", "finding-002", "finding-003"],
            },
        }

        result = map_investigation_from_api(api_response)

        assert "finding_ids" in result
        assert result["finding_ids"] == ["finding-001", "finding-002", "finding-003"]

    def test_map_investigation_from_api_with_single_finding(self):
        """Test extraction of single finding_id (string instead of list)."""
        api_response = {
            "name": "Test",
            "consolidated_findings": {
                "event_id": "finding-001",  # Single string
            },
        }

        result = map_investigation_from_api(api_response)

        assert "finding_ids" in result
        assert result["finding_ids"] == ["finding-001"]

    def test_map_investigation_from_api_empty_config(self):
        """Test handling of empty configuration."""
        result = map_investigation_from_api({})

        assert result == {}

    def test_map_investigation_from_api_none_values(self):
        """Test that None values are excluded."""
        api_response = {
            "name": "Test",
            "description": None,
            "status": None,
        }

        result = map_investigation_from_api(api_response)

        assert result["name"] == "Test"
        assert "description" not in result
        assert "status" not in result


class TestMapInvestigationToApi:
    """Tests for the ActionModule.map_to_api method.

    This method converts module parameters to API payload format.
    """

    def test_map_investigation_to_api_basic(self):
        """Test basic field mapping from module to API format."""
        investigation = {
            "name": "Test Investigation",
            "description": "A test description",
            "owner": "admin",
            "urgency": "high",
        }

        result = ActionModule.map_to_api(investigation)

        assert result["name"] == "Test Investigation"
        assert result["description"] == "A test description"
        assert result["owner"] == "admin"
        assert result["urgency"] == "high"

    def test_map_investigation_to_api_status_conversion(self):
        """Test that string status is converted to numeric code."""
        investigation = {
            "name": "Test",
            "status": "new",
        }

        result = ActionModule.map_to_api(investigation)

        assert result["status"] == "1"

    def test_map_investigation_to_api_all_status_values(self):
        """Test all status value conversions to API format."""
        for module_value, api_value in STATUS_TO_API.items():
            investigation = {"name": "Test", "status": module_value}
            result = ActionModule.map_to_api(investigation)
            assert result["status"] == api_value

    def test_map_investigation_to_api_disposition_conversion(self):
        """Test that string disposition is converted to API format."""
        investigation = {
            "name": "Test",
            "disposition": "true_positive",
        }

        result = ActionModule.map_to_api(investigation)

        assert result["disposition"] == "disposition:1"

    def test_map_investigation_to_api_all_disposition_values(self):
        """Test all disposition value conversions to API format."""
        for module_value, api_value in DISPOSITION_TO_API.items():
            investigation = {"name": "Test", "disposition": module_value}
            result = ActionModule.map_to_api(investigation)
            assert result["disposition"] == api_value

    def test_map_investigation_to_api_sensitivity_conversion(self):
        """Test that lowercase sensitivity is converted to capitalized."""
        investigation = {
            "name": "Test",
            "sensitivity": "amber",
        }

        result = ActionModule.map_to_api(investigation)

        assert result["sensitivity"] == "Amber"

    def test_map_investigation_to_api_all_sensitivity_values(self):
        """Test all sensitivity value conversions to API format."""
        for module_value, api_value in ActionModule.SENSITIVITY_TO_API.items():
            investigation = {"name": "Test", "sensitivity": module_value}
            result = ActionModule.map_to_api(investigation)
            assert result["sensitivity"] == api_value


class TestMapInvestigationUpdateToApi:
    """Tests for the ActionModule.map_update_to_api method.

    This method converts module parameters to the update API payload format.
    Only updatable fields are included in the result.
    """

    def test_map_investigation_update_to_api_description(self):
        """Test that description is passed through."""
        investigation = {"description": "Updated description"}

        result = ActionModule.map_update_to_api(investigation)

        assert result["description"] == "Updated description"

    def test_map_investigation_update_to_api_status(self):
        """Test that status is converted to numeric code."""
        investigation = {"status": "resolved"}

        result = ActionModule.map_update_to_api(investigation)

        assert result["status"] == "4"

    def test_map_investigation_update_to_api_urgency(self):
        """Test that urgency is passed through."""
        investigation = {"urgency": "high"}

        result = ActionModule.map_update_to_api(investigation)

        assert result["urgency"] == "high"

    def test_map_investigation_update_to_api_owner(self):
        """Test that owner is passed through."""
        investigation = {"owner": "analyst1"}

        result = ActionModule.map_update_to_api(investigation)

        assert result["owner"] == "analyst1"

    def test_map_investigation_update_to_api_disposition(self):
        """Test that disposition is converted to API format."""
        investigation = {"disposition": "false_positive"}

        result = ActionModule.map_update_to_api(investigation)

        assert result["disposition"] == "disposition:3"

    def test_map_investigation_update_to_api_sensitivity(self):
        """Test that sensitivity is converted to capitalized format."""
        investigation = {"sensitivity": "red"}

        result = ActionModule.map_update_to_api(investigation)

        assert result["sensitivity"] == "Red"

    def test_map_investigation_update_to_api_all_updatable_fields(self):
        """Test mapping with all updatable fields."""
        investigation = {
            "description": "Updated desc",
            "owner": "analyst",
            "status": "in_progress",
            "urgency": "critical",
            "disposition": "true_positive",
            "sensitivity": "amber",
        }

        result = ActionModule.map_update_to_api(investigation)

        assert result["description"] == "Updated desc"
        assert result["owner"] == "analyst"
        assert result["status"] == "2"
        assert result["urgency"] == "critical"
        assert result["disposition"] == "disposition:1"
        assert result["sensitivity"] == "Amber"

    def test_map_investigation_update_to_api_ignores_non_updatable(self):
        """Test that non-updatable fields are ignored."""
        investigation = {
            "name": "Should be ignored",  # name cannot be updated
            "owner": "admin",
        }

        result = ActionModule.map_update_to_api(investigation)

        assert "name" not in result
        assert result["owner"] == "admin"

    def test_map_investigation_update_to_api_none_values(self):
        """Test that None values are excluded."""
        investigation = {
            "owner": None,
            "status": "new",
        }

        result = ActionModule.map_update_to_api(investigation)

        assert "owner" not in result
        assert result["status"] == "1"

    def test_map_investigation_update_to_api_empty_dict(self):
        """Test handling of empty dictionary."""
        result = ActionModule.map_update_to_api({})

        assert result == {}


class TestStatusMappings:
    """Tests for status mapping constants.

    Verify that STATUS_TO_API and STATUS_FROM_API are consistent inverses.
    """

    def test_status_mappings_are_inverses(self):
        """Test that TO_API and FROM_API mappings are consistent inverses."""
        for module_val, api_val in STATUS_TO_API.items():
            assert STATUS_FROM_API[api_val] == module_val

    def test_status_mappings_complete(self):
        """Test that all expected status values are mapped."""
        expected_statuses = ["unassigned", "new", "in_progress", "pending", "resolved", "closed"]

        for status in expected_statuses:
            assert status in STATUS_TO_API


class TestDispositionMappings:
    """Tests for disposition mapping constants.

    Verify that DISPOSITION_TO_API and DISPOSITION_FROM_API are consistent inverses.
    """

    def test_disposition_mappings_are_inverses(self):
        """Test that TO_API and FROM_API mappings are consistent inverses."""
        for module_val, api_val in DISPOSITION_TO_API.items():
            assert DISPOSITION_FROM_API[api_val] == module_val

    def test_disposition_mappings_complete(self):
        """Test that all expected disposition values are mapped."""
        expected_dispositions = [
            "unassigned",
            "true_positive",
            "benign_positive",
            "false_positive",
            "false_positive_inaccurate_data",
            "other",
            "undetermined",
        ]

        for disposition in expected_dispositions:
            assert disposition in DISPOSITION_TO_API


class TestSensitivityMappings:
    """Tests for sensitivity mapping constants.

    Verify that SENSITIVITY_TO_API and SENSITIVITY_FROM_API are consistent inverses.
    """

    def test_sensitivity_mappings_are_inverses(self):
        """Test that TO_API and FROM_API mappings are consistent inverses."""
        for module_val, api_val in ActionModule.SENSITIVITY_TO_API.items():
            assert SENSITIVITY_FROM_API[api_val] == module_val

    def test_sensitivity_mappings_complete(self):
        """Test that all expected sensitivity values are mapped."""
        expected_sensitivities = ["white", "green", "amber", "red", "unassigned"]

        for sensitivity in expected_sensitivities:
            assert sensitivity in ActionModule.SENSITIVITY_TO_API


class TestUpdatableFields:
    """Tests for the ActionModule.UPDATABLE_FIELDS constant."""

    def test_updatable_fields_contains_expected(self):
        """Test that UPDATABLE_FIELDS contains the correct fields."""
        expected = [
            "description",
            "status",
            "disposition",
            "owner",
            "urgency",
            "sensitivity",
            "investigation_type",
        ]

        assert set(ActionModule.UPDATABLE_FIELDS) == set(expected)

    def test_updatable_fields_excludes_name(self):
        """Test that name is not in UPDATABLE_FIELDS."""
        assert "name" not in ActionModule.UPDATABLE_FIELDS

    def test_updatable_fields_excludes_finding_ids(self):
        """Test that finding_ids is not in UPDATABLE_FIELDS (handled separately)."""
        assert "finding_ids" not in ActionModule.UPDATABLE_FIELDS
