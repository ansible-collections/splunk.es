# -*- coding: utf-8 -*-
"""Splunk module utilities for Ansible."""

# (c) 2018, Adam Miller (admiller@redhat.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type  # pylint: disable=invalid-name
try:
    from ssl import CertificateError
except ImportError:
    from backports.ssl_match_hostname import CertificateError

from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.connection import ConnectionError as AnsibleConnectionError
from ansible.module_utils.six.moves.urllib.parse import urlencode


def remove_get_keys_from_payload_dict(payload_dict, remove_key_list):
    """Remove specified keys from a payload dictionary."""
    for each_key in remove_key_list:
        if each_key in payload_dict:
            payload_dict.pop(each_key)
    return payload_dict


def map_params_to_obj(module_params, key_transform):
    """The fn to convert the api returned params to module params
    :param module_params: Module params
    :param key_transform: Dict with module equivalent API params
    :rtype: A dict
    :returns: dict with module prams transformed having API expected params
    """

    obj = {}
    for k, v in key_transform.items():
        if k in module_params and (
            module_params.get(k) or module_params.get(k) == 0 or module_params.get(k) is False
        ):
            obj[v] = module_params.pop(k)
    return obj


def map_obj_to_params(module_return_params, key_transform):
    """The fn to convert the module params to api return params
    :param module_return_params: API returned response params
    :param key_transform: Module params
    :rtype: A dict
    :returns: dict with api returned value to module param value
    """
    temp = {}
    for k, v in key_transform.items():
        if v in module_return_params and (
            module_return_params.get(v)
            or module_return_params.get(v) == 0
            or module_return_params.get(v) is False
        ):
            temp[k] = module_return_params.pop(v)
    return temp


def set_defaults(config, defaults):
    """Set default values in config dictionary if keys are not present."""
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


class SplunkRequest:
    """Handle HTTP requests to the Splunk REST API."""

    def __init__(
        self,
        action_module,
        connection,
        keymap=None,
        not_rest_data_keys=None,
    ):
        """Initialize SplunkRequest for action plugin usage.

        :param action_module: The action plugin module instance
        :param connection: The connection object to use for API requests
        :param keymap: Optional mapping of module params to API params
        :param not_rest_data_keys: List of keys to exclude from REST data
        """
        self.connection = connection
        self.connection.load_platform_plugins("splunk.es.splunk")
        self.module = action_module

        # The Splunk REST API endpoints often use keys that aren't pythonic so
        # we need to handle that with a mapping to allow keys to be proper
        # variables in the module argspec
        if keymap is None:
            self.keymap = {}
        else:
            self.keymap = keymap

        # This allows us to exclude specific argspec keys from being included by
        # the rest data that don't follow the splunk_* naming convention
        if not_rest_data_keys is None:
            self.not_rest_data_keys = []
        else:
            self.not_rest_data_keys = not_rest_data_keys
        self.not_rest_data_keys.append("validate_certs")

    def _httpapi_error_handle(self, method, uri, payload=None):
        try:
            code, response = self.connection.send_request(
                method,
                uri,
                payload=payload,
            )

            if code == 404:
                if to_text("Object not found") in to_text(response) or to_text(
                    "Could not find object",
                ) in to_text(response):
                    return {}

            if not 200 <= code < 300:
                self.module.fail_json(
                    msg=f"Splunk httpapi returned error {code} with message {response}",
                )
                return None

            return response

        except AnsibleConnectionError as e:
            self.module.fail_json(
                msg=f"connection error occurred: {e}",
            )
            return None
        except CertificateError as e:
            self.module.fail_json(
                msg=f"certificate error occurred: {e}",
            )
            return None
        except ValueError as e:
            try:
                self.module.fail_json(
                    msg=f"certificate not found: {e}",
                )
            except AttributeError:
                pass
            return None

    def get(self, url, **kwargs):
        """Perform a GET request to the Splunk API."""
        return self._httpapi_error_handle("GET", url, **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request to the Splunk API."""
        return self._httpapi_error_handle("PUT", url, **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request to the Splunk API."""
        return self._httpapi_error_handle("POST", url, **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request to the Splunk API."""
        return self._httpapi_error_handle("DELETE", url, **kwargs)

    def get_data(self, config):
        """
        Get the valid fields that should be passed to the REST API as urlencoded
        data so long as the argument specification to the module follows the
        convention:
            - the key to the argspec item does not start with splunk_
            - the key does not exist in the not_data_keys list

        :param config: Configuration dictionary to transform
        :return: Dictionary with transformed data for REST API
        """
        try:
            splunk_data = {}
            for param in config:
                if (config[param]) is not None and (param not in self.not_rest_data_keys):
                    if param in self.keymap:
                        splunk_data[self.keymap[param]] = config[param]
                    else:
                        splunk_data[param] = config[param]

            return splunk_data

        except TypeError as e:
            self.module.fail_json(
                msg=f"invalid data type provided: {e}",
            )
            return None

    def get_urlencoded_data(self, config):
        """Get data as URL-encoded string for REST API requests."""
        return urlencode(self.get_data(config))

    def get_by_path(self, rest_path):
        """
        GET attributes of a monitor by rest path
        """

        return self.get(f"/{rest_path}?output_mode=json")

    def delete_by_path(self, rest_path):
        """
        DELETE attributes of a monitor by rest path
        """

        return self.delete(f"/{rest_path}?output_mode=json")

    def create_update(self, rest_path, data):
        """
        Create or Update a file/directory monitor data input in Splunk

        :param rest_path: The REST API path
        :param data: Data dictionary or URL-encoded string to send
        :return: API response
        """
        # Apply keymap transformation if data is a dictionary
        if data is not None and isinstance(data, dict):
            data = self.get_urlencoded_data(data)
        return self.post(
            f"/{rest_path}?output_mode=json",
            payload=data,
        )
