# -*- coding: utf-8 -*-

# (c) 2018, Adam Miller (admiller@redhat.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleActionFail
from ansible.module_utils.urls import CertificateError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.connection import Connection
from ansible.module_utils._text import to_text
from ansible.module_utils.six import iteritems


def parse_splunk_args(module):
    """
    Get the valid fields that should be passed to the REST API as urlencoded
    data so long as the argument specification to the module follows the
    convention:
        1) name field is Required to be passed as data to REST API
        2) all module argspec items that should be passed to data are not
            Required by the module and are set to default=None
    """
    try:
        splunk_data = {}
        for argspec in module.argument_spec:
            if "default" in module.argument_spec[argspec] and module.argument_spec[argspec]["default"] is None and module.params[argspec] is not None:
                splunk_data[argspec] = module.params[argspec]
        return splunk_data
    except TypeError as e:
        module.fail_json(msg="Invalid data type provided for splunk module_util.parse_splunk_args: {0}".format(e))


def remove_get_keys_from_payload_dict(payload_dict, remove_key_list):
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
    for k, v in iteritems(key_transform):
        if k in module_params and (module_params.get(k) or module_params.get(k) == 0 or module_params.get(k) is False):
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
    for k, v in iteritems(key_transform):
        if v in module_return_params and (module_return_params.get(v) or module_return_params.get(v) == 0 or module_return_params.get(v) is False):
            temp[k] = module_return_params.pop(v)
    return temp


class SplunkRequest(object):
    def __init__(self, conn, headers=None, keymap=None, not_rest_data_keys=None):

        self.module = conn
        self.connection = Connection(self.module._socket_path)

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
            code, response = self.connection.send_request(method, uri, payload=payload)
        except ConnectionError as e:
            raise AnsibleActionFail("connection error occurred: {0}".format(e))
        except CertificateError as e:
            raise AnsibleActionFail("certificate error occurred: {0}".format(e))
        except ValueError as e:
            raise AnsibleActionFail("certificate not found: {0}".format(e))

        if code == 404:
            if to_text("Object not found") in to_text(response) or to_text("Could not find object") in to_text(response):
                return {}

        if not (code >= 200 and code < 300):
            raise AnsibleActionFail("Splunk httpapi returned error {0} with message {1}".format(code, response))

        return response

    def get(self, url, **kwargs):
        return self._httpapi_error_handle("GET", url, **kwargs)

    def put(self, url, **kwargs):
        return self._httpapi_error_handle("PUT", url, **kwargs)

    def post(self, url, **kwargs):
        return self._httpapi_error_handle("POST", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._httpapi_error_handle("DELETE", url, **kwargs)

    def get_data(self, config):
        """
        Get the valid fields that should be passed to the REST API as urlencoded
        data so long as the argument specification to the module follows the
        convention:
            - the key to the argspec item does not start with splunk_
            - the key does not exist in the not_data_keys list
        """
        try:
            splunk_data = {}
            # for param in self.module.params:
            #     if (self.module.params[param]) is not None and (param not in self.not_rest_data_keys):
            #         if param in self.keymap:
            #             splunk_data[self.keymap[param]] = self.module.params[param]
            #         else:
            #             splunk_data[param] = self.module.params[param]

            for param in config:
                if (config[param]) is not None and (param not in self.not_rest_data_keys):
                    if param in self.keymap:
                        splunk_data[self.keymap[param]] = config[param]
                    else:
                        splunk_data[param] = config[param]
            return splunk_data

        except TypeError as e:
            raise AnsibleActionFail("invalid data type provided: {0}".format(e))

    def get_urlencoded_data(self, config):
        return urlencode(self.get_data(config))

    def get_by_path(self, rest_path):
        """
        GET attributes of a monitor by rest path
        """

        return self.get("/{0}?output_mode=json".format(rest_path))

    def delete_by_path(self, rest_path):
        """
        DELETE attributes of a monitor by rest path
        """

        return self.delete("/{0}?output_mode=json".format(rest_path))

    def create_update(self, rest_path, data=None):
        """
        Create or Update a file/directory monitor data input in Splunk
        """
        if data is not None:
            data = self.get_urlencoded_data(data)
        return self.post("/{0}?output_mode=json".format(rest_path), payload=data)
