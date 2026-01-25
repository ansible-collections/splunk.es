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
Unit tests for the finding module utilities.

These tests verify that the utility functions in plugins/module_utils/finding.py
work correctly for:
- Building API paths
- Extracting notable time from ref_ids
- Mapping between API and module parameter formats
- Status and disposition value conversions
"""


from ansible_collections.splunk.es.plugins.action.splunk_finding import (
    ActionModule,
)
from ansible_collections.splunk.es.plugins.module_utils.finding import (
    FINDING_KEY_TRANSFORM,
    build_finding_api_path,
    extract_notable_time,
    map_finding_from_api,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_APP_SECURITY_SUITE,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
    DISPOSITION_FROM_API,
    DISPOSITION_TO_API,
    STATUS_FROM_API,
    STATUS_TO_API,
)


class TestBuildFindingApiPath:
    """Tests for the build_finding_api_path function.

    This function constructs the REST API path for the findings endpoint.
    It should handle default values and custom namespace/user/app overrides.
    """

    def test_build_finding_api_path_defaults(self):
        """Test that default API path is constructed correctly.

        When called without arguments, should use the default namespace,
        user, and app values defined in the module.
        """
        result = build_finding_api_path()

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP_SECURITY_SUITE}/public/v2/findings"
        assert result == expected

    def test_build_finding_api_path_custom_namespace(self):
        """Test API path with custom namespace value."""
        result = build_finding_api_path(namespace="customNS")

        expected = (
            f"customNS/{DEFAULT_API_USER}/{DEFAULT_API_APP_SECURITY_SUITE}/public/v2/findings"
        )
        assert result == expected

    def test_build_finding_api_path_custom_user(self):
        """Test API path with custom user value."""
        result = build_finding_api_path(user="admin")

        expected = (
            f"{DEFAULT_API_NAMESPACE}/admin/{DEFAULT_API_APP_SECURITY_SUITE}/public/v2/findings"
        )
        assert result == expected

    def test_build_finding_api_path_custom_app(self):
        """Test API path with custom app value."""
        result = build_finding_api_path(app="CustomSecurityApp")

        expected = (
            f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/CustomSecurityApp/public/v2/findings"
        )
        assert result == expected

    def test_build_finding_api_path_all_custom(self):
        """Test API path with all custom values."""
        result = build_finding_api_path(
            namespace="myNS",
            user="myuser",
            app="MyApp",
        )

        assert result == "myNS/myuser/MyApp/public/v2/findings"


class TestBuildUpdateApiPath:
    """Tests for the ActionModule.build_update_api_path method.

    This method constructs the REST API path for updating findings
    via the investigations API (uses missioncontrol app).
    """

    def test_build_update_api_path_defaults(self):
        """Test update API path with default namespace and user."""
        ref_id = "abc-123@@notable@@time1234567890"
        result = ActionModule.build_update_api_path(ref_id)

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/v1/investigations/{ref_id}"
        assert result == expected
        assert "missioncontrol" in result

    def test_build_update_api_path_custom_namespace(self):
        """Test update API path with custom namespace."""
        ref_id = "abc-123@@notable@@time1234567890"
        result = ActionModule.build_update_api_path(ref_id, namespace="customNS")

        expected = f"customNS/{DEFAULT_API_USER}/{DEFAULT_API_APP}/v1/investigations/{ref_id}"
        assert result == expected

    def test_build_update_api_path_custom_user(self):
        """Test update API path with custom user."""
        ref_id = "abc-123@@notable@@time1234567890"
        result = ActionModule.build_update_api_path(ref_id, user="admin")

        expected = f"{DEFAULT_API_NAMESPACE}/admin/{DEFAULT_API_APP}/v1/investigations/{ref_id}"
        assert result == expected

    def test_build_update_api_path_special_characters_in_ref_id(self):
        """Test update API path handles special characters in ref_id.

        The ref_id is included as-is in the path; URL encoding happens elsewhere.
        """
        ref_id = "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
        result = ActionModule.build_update_api_path(ref_id)

        assert ref_id in result


class TestExtractNotableTime:
    """Tests for the extract_notable_time function.

    This function extracts the timestamp from a finding reference ID.
    The ref_id format is: uuid@@notable@@time{timestamp}
    """

    def test_extract_notable_time_valid(self):
        """Test extraction from a valid ref_id format."""
        ref_id = "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
        result = extract_notable_time(ref_id)

        assert result == "1768225865"

    def test_extract_notable_time_different_uuid(self):
        """Test extraction works with different UUID formats."""
        ref_id = "abc123@@notable@@time9999999999"
        result = extract_notable_time(ref_id)

        assert result == "9999999999"

    def test_extract_notable_time_empty_string(self):
        """Test that empty string returns None."""
        result = extract_notable_time("")

        assert result is None

    def test_extract_notable_time_none(self):
        """Test that None input returns None."""
        result = extract_notable_time(None)

        assert result is None

    def test_extract_notable_time_no_time_prefix(self):
        """Test that ref_id without 'time' prefix returns None."""
        ref_id = "abc-123@@notable@@1768225865"
        result = extract_notable_time(ref_id)

        assert result is None

    def test_extract_notable_time_invalid_format(self):
        """Test that completely invalid format returns None."""
        ref_id = "just-some-random-string"
        result = extract_notable_time(ref_id)

        assert result is None

    def test_extract_notable_time_no_digits_after_time(self):
        """Test that 'time' without digits returns None."""
        ref_id = "abc-123@@notable@@time"
        result = extract_notable_time(ref_id)

        assert result is None


class TestMapFindingFromApi:
    """Tests for the map_finding_from_api function.

    This function converts the API response format to the module parameter format.
    It handles key renaming, status/disposition conversion, and type normalization.
    """

    def test_map_finding_from_api_basic(self):
        """Test basic field mapping from API to module format."""
        api_response = {
            "rule_title": "Test Finding",
            "rule_description": "A test description",
            "security_domain": "access",
            "risk_object": "testuser",
            "risk_object_type": "user",
            "risk_score": "50",
        }

        result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)

        assert result["title"] == "Test Finding"
        assert result["description"] == "A test description"
        assert result["security_domain"] == "access"
        assert result["entity"] == "testuser"
        assert result["entity_type"] == "user"
        assert result["finding_score"] == 50  # Converted to int

    def test_map_finding_from_api_with_finding_id(self):
        """Test that finding_id is extracted as ref_id."""
        api_response = {
            "finding_id": "abc-123@@notable@@time1234567890",
            "rule_title": "Test Finding",
        }

        result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)

        assert result["ref_id"] == "abc-123@@notable@@time1234567890"

    def test_map_finding_from_api_status_conversion(self):
        """Test that numeric status codes are converted to string names."""
        api_response = {
            "rule_title": "Test",
            "status": "1",  # API uses numeric codes
        }

        result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)

        assert result["status"] == "new"  # Converted to human-readable

    def test_map_finding_from_api_all_status_values(self):
        """Test all status value conversions."""
        for api_value, module_value in STATUS_FROM_API.items():
            api_response = {"rule_title": "Test", "status": api_value}
            result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)
            assert result["status"] == module_value

    def test_map_finding_from_api_disposition_conversion(self):
        """Test that disposition codes are converted to string names."""
        api_response = {
            "rule_title": "Test",
            "disposition": "disposition:6",  # API format
        }

        result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)

        assert result["disposition"] == "undetermined"

    def test_map_finding_from_api_all_disposition_values(self):
        """Test all disposition value conversions."""
        for api_value, module_value in DISPOSITION_FROM_API.items():
            api_response = {"rule_title": "Test", "disposition": api_value}
            result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)
            assert result["disposition"] == module_value

    def test_map_finding_from_api_finding_score_float_string(self):
        """Test that finding_score handles float strings like '50.0'."""
        api_response = {
            "rule_title": "Test",
            "risk_score": "75.5",
        }

        result = map_finding_from_api(api_response, FINDING_KEY_TRANSFORM)

        assert result["finding_score"] == 75  # Truncated to int

    def test_map_finding_from_api_empty_config(self):
        """Test handling of empty configuration."""
        result = map_finding_from_api({}, FINDING_KEY_TRANSFORM)

        assert result == {}

    def test_map_finding_from_api_default_key_transform(self):
        """Test that default key_transform is used when not provided."""
        api_response = {
            "rule_title": "Test Finding",
        }

        result = map_finding_from_api(api_response)

        assert result["title"] == "Test Finding"


class TestMapFindingToApi:
    """Tests for the ActionModule.map_finding_to_api method.

    This method converts module parameters to API payload format.
    It handles key renaming and adds required default values.
    """

    def test_map_finding_to_api_basic(self):
        """Test basic field mapping from module to API format."""
        finding = {
            "title": "Test Finding",
            "description": "A test description",
            "security_domain": "access",
            "entity": "testuser",
            "entity_type": "user",
            "finding_score": 50,
        }

        result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)

        assert result["rule_title"] == "Test Finding"
        assert result["rule_description"] == "A test description"
        assert result["security_domain"] == "access"
        assert result["risk_object"] == "testuser"
        assert result["risk_object_type"] == "user"
        assert result["risk_score"] == 50

    def test_map_finding_to_api_adds_defaults(self):
        """Test that app and creator defaults are added."""
        finding = {"title": "Test"}

        result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)

        assert result["app"] == "SplunkEnterpriseSecuritySuite"
        assert result["creator"] == "admin"

    def test_map_finding_to_api_status_conversion(self):
        """Test that string status is converted to numeric code."""
        finding = {
            "title": "Test",
            "status": "new",
        }

        result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)

        assert result["status"] == "1"

    def test_map_finding_to_api_all_status_values(self):
        """Test all status value conversions to API format."""
        for module_value, api_value in STATUS_TO_API.items():
            finding = {"title": "Test", "status": module_value}
            result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)
            assert result["status"] == api_value

    def test_map_finding_to_api_disposition_conversion(self):
        """Test that string disposition is converted to API format."""
        finding = {
            "title": "Test",
            "disposition": "true_positive",
        }

        result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)

        assert result["disposition"] == "disposition:1"

    def test_map_finding_to_api_all_disposition_values(self):
        """Test all disposition value conversions to API format."""
        for module_value, api_value in DISPOSITION_TO_API.items():
            finding = {"title": "Test", "disposition": module_value}
            result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)
            assert result["disposition"] == api_value

    def test_map_finding_to_api_with_custom_fields(self):
        """Test that custom fields are flattened into payload."""
        finding = {
            "title": "Test",
            "fields": [
                {"name": "custom_field_a", "value": "value1"},
                {"name": "custom_field_b", "value": "value2"},
            ],
        }

        result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)

        assert result["custom_field_a"] == "value1"
        assert result["custom_field_b"] == "value2"

    def test_map_finding_to_api_empty_fields(self):
        """Test handling of empty fields list."""
        finding = {
            "title": "Test",
            "fields": [],
        }

        result = ActionModule.map_finding_to_api(finding, FINDING_KEY_TRANSFORM)

        # Should not raise error, just skip empty fields
        assert "rule_title" in result


class TestMapUpdateToApi:
    """Tests for the ActionModule.map_update_to_api method.

    This method converts module parameters to the update API payload format.
    Only updatable fields (owner, status, urgency, disposition) are included.
    """

    def test_map_update_to_api_owner(self):
        """Test that owner is mapped to assignee."""
        finding = {"owner": "admin"}

        result = ActionModule.map_update_to_api(finding)

        assert result["assignee"] == "admin"
        assert "owner" not in result

    def test_map_update_to_api_status(self):
        """Test that status is converted to numeric code."""
        finding = {"status": "resolved"}

        result = ActionModule.map_update_to_api(finding)

        assert result["status"] == "4"

    def test_map_update_to_api_urgency(self):
        """Test that urgency is passed through."""
        finding = {"urgency": "high"}

        result = ActionModule.map_update_to_api(finding)

        assert result["urgency"] == "high"

    def test_map_update_to_api_disposition(self):
        """Test that disposition is converted to API format."""
        finding = {"disposition": "false_positive"}

        result = ActionModule.map_update_to_api(finding)

        assert result["disposition"] == "disposition:3"

    def test_map_update_to_api_all_updatable_fields(self):
        """Test mapping with all updatable fields."""
        finding = {
            "owner": "analyst",
            "status": "in_progress",
            "urgency": "critical",
            "disposition": "true_positive",
        }

        result = ActionModule.map_update_to_api(finding)

        assert result["assignee"] == "analyst"
        assert result["status"] == "2"
        assert result["urgency"] == "critical"
        assert result["disposition"] == "disposition:1"

    def test_map_update_to_api_ignores_non_updatable(self):
        """Test that non-updatable fields are ignored."""
        finding = {
            "title": "Should be ignored",
            "description": "Also ignored",
            "owner": "admin",
        }

        result = ActionModule.map_update_to_api(finding)

        assert "title" not in result
        assert "rule_title" not in result
        assert "description" not in result
        assert result["assignee"] == "admin"

    def test_map_update_to_api_none_values(self):
        """Test that None values are excluded."""
        finding = {
            "owner": None,
            "status": "new",
        }

        result = ActionModule.map_update_to_api(finding)

        assert "assignee" not in result
        assert result["status"] == "1"

    def test_map_update_to_api_empty_dict(self):
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


class TestUpdateKeyTransform:
    """Tests for the ActionModule.UPDATE_KEY_TRANSFORM constant."""

    def test_update_key_transform_contains_expected_keys(self):
        """Test that UPDATE_KEY_TRANSFORM contains the correct updatable fields."""
        expected = ["owner", "status", "urgency", "disposition"]

        assert set(ActionModule.UPDATE_KEY_TRANSFORM.keys()) == set(expected)

    def test_update_key_transform_excludes_create_only(self):
        """Test that create-only fields are not in UPDATE_KEY_TRANSFORM."""
        create_only = [
            "title",
            "description",
            "security_domain",
            "entity",
            "entity_type",
            "finding_score",
        ]

        for field in create_only:
            assert field not in ActionModule.UPDATE_KEY_TRANSFORM

    def test_update_key_transform_owner_maps_to_assignee(self):
        """Test that owner is mapped to assignee for the API."""
        assert ActionModule.UPDATE_KEY_TRANSFORM["owner"] == "assignee"
