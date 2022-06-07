#
# Copyright 2022 Red Hat Inc.
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
The module file for deepsec_anti_malwares
"""

from __future__ import absolute_import, division, print_function
from asyncio import QueueEmpty
from urllib import response

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote_plus
from ansible.module_utils.six import iteritems

import q

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    map_obj_to_params,
    map_params_to_obj,
    remove_get_keys_from_payload_dict,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)
from ansible_collections.splunk.es.plugins.modules.data_inputs_monitors import (
    DOCUMENTATION,
)


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self.api_object = "servicesNS/nobody/search/data/inputs/monitor"
        self.key_transform = {
            "blacklist": "blacklist",
            "check-index": "check_index",  # not returned
            "check-path": "check_path",  # not returned
            "crc-salt": "crc_salt",
            "disabled": "disabled",
            "followTail": "follow_tail",
            "host": "host",
            "host_regex": "host_regex",
            "host_segment": "host_segment",
            "ignore-older-than": "ignore_older_than",  # not returned
            "index": "index",
            "name": "name",
            "recursive": "recursive",
            "rename-source": "rename_source",  # not returned
            "sourcetype": "sourcetype",
            "time-before-close": "time_before_close",  # not returned
            "whitelist": "whitelist",
        }

    def _check_argspec(self):
        aav = AnsibleArgSpecValidator(
            data=self._task.args,
            schema=DOCUMENTATION,
            schema_format="doc",
            name=self._task.action,
        )
        valid, errors, self._task.args = aav.validate()
        if not valid:
            self._result["failed"] = True
            self._result["msg"] = errors

    def map_params_to_object(self, config):
        res = {}
        res["name"] = config["name"]

        # splunk takes "crc-salt" as input parameter, and returns "crcSalt" in output
        # therefore we can't directly use mapping
        if config["content"].get("crcSalt"):
            config["content"]["crc-salt"] = config["content"]["crcSalt"]

        res.update(map_params_to_obj(config["content"], self.key_transform))

        return res

    def search_for_resource_name(self, conn_request, directory_name):
        query_dict = conn_request.get_by_path("{0}/{1}".format(self.api_object, quote_plus(directory_name)))

        search_result = {}

        if query_dict:
            search_result = self.map_params_to_object(query_dict["entry"][0])  # ["content"]

        return search_result

    def delete_module_api_config(self, conn_request, config):
        before = []
        after = None
        changed = False
        for want_conf in config:
            search_by_name = self.search_for_resource_name(conn_request, want_conf["name"])
            if search_by_name:
                before.append(search_by_name)
                conn_request.delete_by_path("{0}/{1}".format(self.api_object, quote_plus(want_conf["name"])))
                changed = True
                after = []

        return before, after, changed

    def configure_module_api(self, conn_request, config):
        before = []
        after = []
        changed = False
        # Add to the THIS list for the value which needs to be excluded
        # from HAVE params when compared to WANT param like 'ID' can be
        # part of HAVE param but may not be part of your WANT param
        remove_from_diff_compare = [
            "check_path",
            "check_index",
            "ignore_older_than",
            "time_before_close",
            "rename_source",
        ]
        for want_conf in config:
            have_conf = self.search_for_resource_name(conn_request, want_conf["name"])
            if have_conf:
                want_conf = utils.remove_empties(want_conf)
                diff = utils.dict_diff(have_conf, want_conf)

                if diff:
                    diff = remove_get_keys_from_payload_dict(diff, remove_from_diff_compare)
                    if diff:
                        before.append(have_conf)
                        if self._task.args["state"] == "merged":

                            want_conf = utils.remove_empties(utils.dict_merge(have_conf, want_conf))
                            want_conf = remove_get_keys_from_payload_dict(want_conf, remove_from_diff_compare)
                            changed = True

                            payload = map_obj_to_params(want_conf, self.key_transform)
                            api_response = conn_request.create_update(
                                "{0}/{1}".format(self.api_object, quote_plus(payload.pop("name"))),
                                data=payload,
                            )
                            response_json = self.map_params_to_object(api_response["entry"][0])

                            after.append(response_json)
                        elif self._task.args["state"] == "replaced":
                            api_response = conn_request.delete_by_path("{0}/{1}".format(self.api_object, quote_plus(want_conf["name"])))
                            changed = True

                            payload = map_obj_to_params(want_conf, self.key_transform)
                            api_response = conn_request.create_update(
                                "{0}".format(self.api_object),
                                data=payload,
                            )
                            response_json = self.map_params_to_object(api_response["entry"][0])

                            after.append(response_json)
                    else:
                        before.append(have_conf)
                        after.append(have_conf)
                else:
                    before.append(have_conf)
                    after.append(have_conf)
            else:
                changed = True
                want_conf = utils.remove_empties(want_conf)

                payload = map_obj_to_params(want_conf, self.key_transform)
                api_response = conn_request.create_update(
                    "{0}".format(self.api_object),
                    data=payload,
                )
                response_json = self.map_params_to_object(api_response["entry"][0])

                after.extend(before)
                after.append(response_json)
        if not changed:
            after = None

        return before, after, changed

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._check_argspec()
        if self._result.get("failed"):
            return self._result

        # config is retrieved as a string; need to deserialise
        config = self._task.args.get("config")
        if config:
            if isinstance(config, dict):
                config = [config]

        conn_request = SplunkRequest(
            conn=self._connection,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            not_rest_data_keys=["state"],
        )

        if self._task.args["state"] == "gathered":
            if config:
                self._result["gathered"] = []
                for item in config:
                    self._result["gathered"].append(self.search_for_resource_name(conn_request, item["name"]))
            else:
                self._result["gathered"] = conn_request.get_by_path(self.api_object)["entry"]

        elif self._task.args["state"] == "merged" or self._task.args["state"] == "replaced":
            if config:
                self._result["before"], self._result["after"], self._result["changed"] = self.configure_module_api(conn_request, config)
                if not self._result["after"]:
                    self._result.pop("after")

        elif self._task.args["state"] == "deleted":
            if config:
                self._result["before"], self._result["after"], self._result["changed"] = self.delete_module_api_config(conn_request, config)
                if self._result["after"] == None:
                    self._result.pop("after")

        return self._result
