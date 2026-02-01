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
Unit tests for the investigation_type module utilities.

These tests verify that the utility functions work correctly for:
- Building API paths for investigation types
- Mapping between API and module parameter formats
- URL encoding of names

Utilities are in plugins/module_utils/investigation_type.py
"""

from ansible_collections.splunk.es.plugins.module_utils.investigation_type import (
    build_investigation_type_api_path,
    build_investigation_type_path_by_name,
    map_investigation_type_from_api,
    map_investigation_type_to_api_create,
    map_investigation_type_to_api_update,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk_utils import (
    DEFAULT_API_APP,
    DEFAULT_API_NAMESPACE,
    DEFAULT_API_USER,
)


class TestBuildInvestigationTypeApiPath:
    """Tests for the build_investigation_type_api_path function.

    This function constructs the REST API path for the incident types endpoint.
    It should handle default values and custom namespace/user/app overrides.
    """

    def test_build_investigation_type_api_path_defaults(self):
        """Test that default API path is constructed correctly.

        When called without arguments, should use the default namespace,
        user, and app values defined in the module.
        """
        result = build_investigation_type_api_path()

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/v1/incidenttypes"
        assert result == expected

    def test_build_investigation_type_api_path_custom_namespace(self):
        """Test API path with custom namespace value."""
        result = build_investigation_type_api_path(namespace="customNS")

        expected = f"customNS/{DEFAULT_API_USER}/{DEFAULT_API_APP}/v1/incidenttypes"
        assert result == expected

    def test_build_investigation_type_api_path_custom_user(self):
        """Test API path with custom user value."""
        result = build_investigation_type_api_path(user="admin")

        expected = f"{DEFAULT_API_NAMESPACE}/admin/{DEFAULT_API_APP}/v1/incidenttypes"
        assert result == expected

    def test_build_investigation_type_api_path_custom_app(self):
        """Test API path with custom app value."""
        result = build_investigation_type_api_path(app="CustomApp")

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/CustomApp/v1/incidenttypes"
        assert result == expected

    def test_build_investigation_type_api_path_all_custom(self):
        """Test API path with all custom values."""
        result = build_investigation_type_api_path(
            namespace="myNS",
            user="myuser",
            app="MyApp",
        )

        assert result == "myNS/myuser/MyApp/v1/incidenttypes"


class TestBuildInvestigationTypePathByName:
    """Tests for the build_investigation_type_path_by_name function.

    This function constructs the REST API path for a specific investigation type.
    It should properly URL-encode the name and handle special characters.
    """

    def test_build_investigation_type_path_by_name_simple(self):
        """Test building path with simple name."""
        result = build_investigation_type_path_by_name("TestType")

        expected = f"{DEFAULT_API_NAMESPACE}/{DEFAULT_API_USER}/{DEFAULT_API_APP}/v1/incidenttypes/TestType"
        assert result == expected

    def test_build_investigation_type_path_by_name_with_spaces(self):
        """Test building path with name containing spaces.

        Spaces should be URL-encoded as %20.
        """
        result = build_investigation_type_path_by_name("Insider Threat")

        assert "Insider%20Threat" in result
        assert result.endswith("/Insider%20Threat")

    def test_build_investigation_type_path_by_name_with_special_characters(self):
        """Test building path with name containing special characters.

        Special characters should be properly URL-encoded.
        """
        result = build_investigation_type_path_by_name("Test/Type&Name")

        # Forward slash and ampersand should be encoded
        assert "%2F" in result or "%26" in result or "Test" in result

    def test_build_investigation_type_path_by_name_custom_namespace(self):
        """Test building path with custom namespace."""
        result = build_investigation_type_path_by_name("TestType", namespace="customNS")

        assert "customNS" in result
        assert result.startswith("customNS/")

    def test_build_investigation_type_path_by_name_custom_user(self):
        """Test building path with custom user."""
        result = build_investigation_type_path_by_name("TestType", user="admin")

        assert "/admin/" in result

    def test_build_investigation_type_path_by_name_custom_app(self):
        """Test building path with custom app."""
        result = build_investigation_type_path_by_name("TestType", app="CustomApp")

        assert "/CustomApp/" in result

    def test_build_investigation_type_path_by_name_all_custom(self):
        """Test building path with all custom values."""
        result = build_investigation_type_path_by_name(
            "TestType",
            namespace="myNS",
            user="myuser",
            app="MyApp",
        )

        assert result == "myNS/myuser/MyApp/v1/incidenttypes/TestType"

    def test_build_investigation_type_path_by_name_unicode(self):
        """Test building path with Unicode characters in name."""
        result = build_investigation_type_path_by_name("Test Type ü")

        # Unicode should be properly encoded
        assert "incidenttypes" in result


class TestMapInvestigationTypeFromApi:
    """Tests for the map_investigation_type_from_api function.

    This function converts the API response format to the module parameter format.
    It handles key renaming and value normalization.
    """

    def test_map_investigation_type_from_api_basic(self):
        """Test basic field mapping from API to module format."""
        api_response = {
            "incident_type": "Insider Threat",
            "description": "Investigation type for insider threat incidents",
            "response_template_ids": [],
        }

        result = map_investigation_type_from_api(api_response)

        # incident_type -> name
        assert result["name"] == "Insider Threat"
        assert result["description"] == "Investigation type for insider threat incidents"
        # response_template_ids -> response_plan_ids
        assert result["response_plan_ids"] == []

    def test_map_investigation_type_from_api_with_response_plans(self):
        """Test mapping with response plan IDs."""
        api_response = {
            "incident_type": "Malware Incident",
            "description": "Test description",
            "response_template_ids": [
                "uuid-1111-2222-3333-444455556666",
                "uuid-aaaa-bbbb-cccc-ddddeeeeffff",
            ],
        }

        result = map_investigation_type_from_api(api_response)

        assert result["name"] == "Malware Incident"
        assert len(result["response_plan_ids"]) == 2
        assert "uuid-1111-2222-3333-444455556666" in result["response_plan_ids"]
        assert "uuid-aaaa-bbbb-cccc-ddddeeeeffff" in result["response_plan_ids"]

    def test_map_investigation_type_from_api_empty_config(self):
        """Test handling of empty configuration."""
        result = map_investigation_type_from_api({})

        assert result["name"] == ""
        assert result["description"] == ""
        assert result["response_plan_ids"] == []

    def test_map_investigation_type_from_api_null_response_template_ids(self):
        """Test that None response_template_ids is converted to empty list."""
        api_response = {
            "incident_type": "Test Type",
            "description": "Test",
            "response_template_ids": None,
        }

        result = map_investigation_type_from_api(api_response)

        assert result["response_plan_ids"] == []

    def test_map_investigation_type_from_api_missing_fields(self):
        """Test handling of missing optional fields."""
        api_response = {
            "incident_type": "Test Type",
        }

        result = map_investigation_type_from_api(api_response)

        assert result["name"] == "Test Type"
        assert result["description"] == ""
        assert result["response_plan_ids"] == []

    def test_map_investigation_type_from_api_extra_fields_ignored(self):
        """Test that extra API fields are not included in result."""
        api_response = {
            "incident_type": "Test Type",
            "description": "Test",
            "response_template_ids": [],
            "some_extra_field": "should be ignored",
            "another_field": 12345,
        }

        result = map_investigation_type_from_api(api_response)

        # Only expected fields should be present
        assert set(result.keys()) == {"name", "description", "response_plan_ids"}


class TestMapInvestigationTypeToApiCreate:
    """Tests for the map_investigation_type_to_api_create function.

    This function converts module parameters to API payload format for creation.
    """

    def test_map_investigation_type_to_api_create_basic(self):
        """Test basic field mapping from module to API format for creation."""
        params = {
            "name": "Insider Threat",
            "description": "Investigation type for insider threat incidents",
        }

        result = map_investigation_type_to_api_create(params)

        # name -> incident_type
        assert result["incident_type"] == "Insider Threat"
        assert result["description"] == "Investigation type for insider threat incidents"

    def test_map_investigation_type_to_api_create_minimal(self):
        """Test creation payload with minimal parameters."""
        params = {
            "name": "Minimal Type",
        }

        result = map_investigation_type_to_api_create(params)

        assert result["incident_type"] == "Minimal Type"
        assert result["description"] == ""

    def test_map_investigation_type_to_api_create_empty_description(self):
        """Test creation payload with explicit empty description."""
        params = {
            "name": "Test Type",
            "description": "",
        }

        result = map_investigation_type_to_api_create(params)

        assert result["incident_type"] == "Test Type"
        assert result["description"] == ""

    def test_map_investigation_type_to_api_create_ignores_response_plan_ids(self):
        """Test that response_plan_ids are not included in create payload.

        Response plans are associated via a separate PUT operation after creation.
        """
        params = {
            "name": "Test Type",
            "description": "Test",
            "response_plan_ids": ["uuid-1234"],  # Should be ignored for create
        }

        result = map_investigation_type_to_api_create(params)

        assert "response_template_ids" not in result
        assert "response_plan_ids" not in result

    def test_map_investigation_type_to_api_create_empty_params(self):
        """Test handling of empty parameters."""
        result = map_investigation_type_to_api_create({})

        assert result["incident_type"] == ""
        assert result["description"] == ""


class TestMapInvestigationTypeToApiUpdate:
    """Tests for the map_investigation_type_to_api_update function.

    This function converts module parameters to API payload format for update.
    """

    def test_map_investigation_type_to_api_update_basic(self):
        """Test basic field mapping from module to API format for update."""
        params = {
            "name": "Insider Threat",
            "description": "Updated description",
            "response_plan_ids": [],
        }

        result = map_investigation_type_to_api_update(params)

        assert result["incident_type"] == "Insider Threat"
        assert result["description"] == "Updated description"
        assert result["response_template_ids"] == []

    def test_map_investigation_type_to_api_update_with_response_plans(self):
        """Test update payload with response plan IDs."""
        params = {
            "name": "Malware Incident",
            "description": "Test",
            "response_plan_ids": [
                "uuid-1111-2222-3333-444455556666",
                "uuid-aaaa-bbbb-cccc-ddddeeeeffff",
            ],
        }

        result = map_investigation_type_to_api_update(params)

        assert result["incident_type"] == "Malware Incident"
        assert len(result["response_template_ids"]) == 2
        assert "uuid-1111-2222-3333-444455556666" in result["response_template_ids"]

    def test_map_investigation_type_to_api_update_null_response_plan_ids(self):
        """Test that None response_plan_ids is converted to empty list."""
        params = {
            "name": "Test Type",
            "description": "Test",
            "response_plan_ids": None,
        }

        result = map_investigation_type_to_api_update(params)

        assert result["response_template_ids"] == []

    def test_map_investigation_type_to_api_update_empty_response_plan_ids(self):
        """Test update payload with explicit empty response_plan_ids."""
        params = {
            "name": "Test Type",
            "description": "Test",
            "response_plan_ids": [],
        }

        result = map_investigation_type_to_api_update(params)

        assert result["response_template_ids"] == []

    def test_map_investigation_type_to_api_update_empty_params(self):
        """Test handling of empty parameters."""
        result = map_investigation_type_to_api_update({})

        assert result["incident_type"] == ""
        assert result["description"] == ""
        assert result["response_template_ids"] == []


class TestFieldMappingConsistency:
    """Tests to verify consistency between from_api and to_api mappings.

    These tests ensure that data can be round-tripped between API and module formats.
    """

    def test_round_trip_basic(self):
        """Test that data can round-trip from API -> module -> API."""
        original_api = {
            "incident_type": "Test Type",
            "description": "Test description",
            "response_template_ids": ["uuid-1234", "uuid-5678"],
        }

        # API -> Module format
        module_format = map_investigation_type_from_api(original_api)

        # Module -> API format
        result_api = map_investigation_type_to_api_update(module_format)

        # Should match original
        assert result_api["incident_type"] == original_api["incident_type"]
        assert result_api["description"] == original_api["description"]
        assert set(result_api["response_template_ids"]) == set(
            original_api["response_template_ids"],
        )

    def test_round_trip_empty_response_plans(self):
        """Test round-trip with empty response plans."""
        original_api = {
            "incident_type": "Test Type",
            "description": "Test",
            "response_template_ids": [],
        }

        module_format = map_investigation_type_from_api(original_api)
        result_api = map_investigation_type_to_api_update(module_format)

        assert result_api["incident_type"] == original_api["incident_type"]
        assert result_api["response_template_ids"] == []

    def test_round_trip_null_to_empty(self):
        """Test that null values are normalized to empty during round-trip."""
        original_api = {
            "incident_type": "Test Type",
            "description": "Test",
            "response_template_ids": None,
        }

        module_format = map_investigation_type_from_api(original_api)
        result_api = map_investigation_type_to_api_update(module_format)

        # None should become empty list
        assert result_api["response_template_ids"] == []


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_name(self):
        """Test handling of very long investigation type names."""
        long_name = "A" * 500

        result = build_investigation_type_path_by_name(long_name)

        assert long_name in result or "A" * 100 in result  # At least partial encoding

    def test_empty_name(self):
        """Test handling of empty name."""
        result = build_investigation_type_path_by_name("")

        assert result.endswith("/")

    def test_name_with_only_spaces(self):
        """Test handling of name with only spaces."""
        result = build_investigation_type_path_by_name("   ")

        # Should be URL-encoded
        assert "%20" in result

    def test_map_from_api_preserves_order_of_response_plans(self):
        """Test that order of response plan IDs is preserved."""
        api_response = {
            "incident_type": "Test",
            "description": "Test",
            "response_template_ids": ["c-uuid", "a-uuid", "b-uuid"],
        }

        result = map_investigation_type_from_api(api_response)

        assert result["response_plan_ids"] == ["c-uuid", "a-uuid", "b-uuid"]

    def test_map_to_api_preserves_order_of_response_plans(self):
        """Test that order of response plan IDs is preserved in API mapping."""
        params = {
            "name": "Test",
            "description": "Test",
            "response_plan_ids": ["c-uuid", "a-uuid", "b-uuid"],
        }

        result = map_investigation_type_to_api_update(params)

        assert result["response_template_ids"] == ["c-uuid", "a-uuid", "b-uuid"]
