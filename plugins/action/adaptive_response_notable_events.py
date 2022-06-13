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
The module file for adaptive_response_notable_events
"""

from __future__ import absolute_import, division, print_function
from curses import meta

__metaclass__ = type

import json

# TODO: remove this import
from icecream import ic

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils.six.moves.urllib.parse import (
    quote_plus,
    quote,
    urlencode,
)
from ansible.module_utils.connection import Connection

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.splunk.es.plugins.module_utils.splunk import (
    SplunkRequest,
    map_obj_to_params,
    map_params_to_obj,
    remove_get_keys_from_payload_dict,
    set_defaults,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)
from ansible_collections.splunk.es.plugins.modules.adaptive_response_notable_events import (
    DOCUMENTATION,
)


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self.api_object = (
            "servicesNS/nobody/SplunkEnterpriseSecuritySuite/saved/searches"
        )
        self.module_name = "adaptive_response_notable_events"
        self.key_transform = {
            "action.notable.param.default_owner": "default_owner",
            "action.notable.param.default_status": "default_status",
            "action.notable.param.drilldown_name": "drilldown_name",
            "action.notable.param.drilldown_search": "drilldown_search",
            "action.notable.param.drilldown_earliest_offset": "drilldown_earliest_offset",
            "action.notable.param.drilldown_latest_offset": "drilldown_latest_offset",
            "action.notable.param.extract_artifacts": "extract_artifacts",
            "action.notable.param.investigation_profiles": "investigation_profiles",
            "action.notable.param.next_steps": "next_steps",
            "action.notable.param.recommended_actions": "recommended_actions",
            "action.notable.param.rule_description": "description",
            "action.notable.param.rule_title": "name",
            "action.notable.param.security_domain": "security_domain",
            "action.notable.param.severity": "severity",
            "name": "correlation_search_name",
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
        res["correlation_search_name"] = config["name"]

        res.update(map_params_to_obj(config["content"], self.key_transform))

        if "extract_artifacts" in res:
            res["extract_artifacts"] = json.loads(res["extract_artifacts"])

        if "default_status" in res:
            mapping = {
                "0": "unassigned",
                "1": "new",
                "2": "in progress",
                "3": "pending",
                "4": "resolved",
                "5": "closed",
            }
            res["default_status"] = mapping[res["default_status"]]

        # need to store correlation search details for populating future request payloads
        metadata = {}
        metadata["search"] = config["content"]["search"]
        if "actions" in config["content"]:
            if config["content"]["actions"] == "notable":
                pass
            elif (
                len(config["content"]["actions"].split(",")) > 0
                and "notable" not in config["content"]["actions"]
            ):
                metadata["actions"] = (
                    config["content"]["actions"] + ", notable"
                )
            else:
                metadata["actions"] = "notable"

        return res, metadata

    def map_objects_to_params(self, metadata, want_conf):
        res = {}

        res["search"] = metadata["search"]
        res["actions"] = metadata["actions"]

        if "extract_artifacts" in res:
            res["extract_artifacts"] = json.dumps(res["extract_artifacts"])

        if "default_status" in res:
            mapping = {
                "unassigned": "0",
                "new": "1",
                "in progress": "2",
                "pending": "3",
                "resolved": "4",
                "closed": "5",
            }
            res["default_status"] = mapping[res["default_status"]]

        res = map_obj_to_params(want_conf, self.key_transform)

        ic(res)

        return res

    def search_for_resource_name(self, conn_request, correlation_search_name):
        query_dict = conn_request.get_by_path(
            "{0}/{1}".format(
                self.api_object,
                quote(correlation_search_name),
            )
        )

        search_result = {}

        if query_dict:
            search_result, metadata = self.map_params_to_object(
                query_dict["entry"][0]
            )
        else:
            raise AnsibleActionFail(
                "Correlation Search '{0}' doesn't exist".format(
                    correlation_search_name
                )
            )

        return search_result, metadata

    def delete_module_api_config(self, conn_request, config):
        before = []
        after = None
        changed = False
        for want_conf in config:
            search_by_name, metadata = self.search_for_resource_name(
                conn_request, want_conf["correlation_search_name"]
            )
            if search_by_name:
                before.append(search_by_name)
                conn_request.delete_by_path(
                    "{0}/{1}".format(
                        self.api_object,
                        quote(want_conf["correlation_search_name"]),
                    )
                )
                changed = True
                after = []

        res_config = {}
        res_config["after"] = after
        res_config["before"] = before

        return res_config, changed

    def configure_module_api(self, conn_request, config):
        before = []
        after = []
        changed = False
        # Add to the THIS list for the value which needs to be excluded
        # from HAVE params when compared to WANT param like 'ID' can be
        # part of HAVE param but may not be part of your WANT param
        defaults = {
            "drilldown_earliest_offset": "$info_min_time$",
            "drilldown_latest_offset": "$info_max_time$",
            "extract_artifacts": {
                "asset": [
                    "src",
                    "dest",
                    "dvc",
                    "orig_host",
                ],
                "identity": [
                    "src_user",
                    "user",
                    "src_user_id",
                    "src_user_role",
                    "user_id",
                    "user_role",
                    "vendor_account",
                ],
            },
            "investigation_profiles": "{}",
        }
        remove_from_diff_compare = []
        for want_conf in config:
            have_conf, metadata = self.search_for_resource_name(
                conn_request, want_conf["correlation_search_name"]
            )

            if "name" in have_conf:
                want_conf = set_defaults(want_conf, defaults)
                want_conf = utils.remove_empties(want_conf)
                diff = utils.dict_diff(have_conf, want_conf)

                # Check if have_conf has extra parameters
                if self._task.args["state"] == "replaced":
                    diff2 = utils.dict_diff(want_conf, have_conf)
                    if len(diff) or len(diff2):
                        diff.update(diff2)

                if diff:
                    diff = remove_get_keys_from_payload_dict(
                        diff, remove_from_diff_compare
                    )
                    if diff:
                        before.append(have_conf)
                        if self._task.args["state"] == "merged":

                            want_conf = utils.remove_empties(
                                utils.dict_merge(have_conf, want_conf)
                            )
                            want_conf = remove_get_keys_from_payload_dict(
                                want_conf, remove_from_diff_compare
                            )
                            changed = True

                            payload = self.map_objects_to_params(
                                metadata, want_conf
                            )
                            url = "{0}/{1}".format(
                                self.api_object,
                                quote_plus(payload.pop("name")),
                            )
                            api_response = conn_request.create_update(
                                url,
                                data=payload,
                            )
                            (
                                response_json,
                                metadata,
                            ) = self.map_params_to_object(
                                api_response["entry"][0]
                            )

                            after.append(response_json)
                        elif self._task.args["state"] == "replaced":
                            conn_request.delete_by_path(
                                "{0}/{1}".format(
                                    self.api_object,
                                    quote_plus(want_conf["name"]),
                                )
                            )
                            changed = True

                            payload = self.map_objects_to_params(
                                metadata, want_conf, self.key_transform
                            )
                            url = "{0}".format(self.api_object)
                            api_response = conn_request.create_update(
                                url,
                                data=payload,
                            )
                            (
                                response_json,
                                metadata,
                            ) = self.map_params_to_object(
                                api_response["entry"][0]
                            )

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

                payload = self.map_objects_to_params(metadata, want_conf)
                url = "{0}".format(self.api_object)
                api_response = conn_request.create_update(
                    url,
                    data=payload,
                )
                response_json, metadata = self.map_params_to_object(
                    api_response["entry"][0]
                )

                after.extend(before)
                after.append(response_json)
        if not changed:
            after = None

        res_config = {}
        res_config["after"] = after
        res_config["before"] = before

        return res_config, changed

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True
        self._result = super(ActionModule, self).run(tmp, task_vars)

        self._check_argspec()
        if self._result.get("failed"):
            return self._result

        self._result[self.module_name] = {}

        # config is retrieved as a string; need to deserialise
        config = self._task.args.get("config")

        conn = Connection(self._connection.socket_path)

        conn_request = SplunkRequest(
            connection=conn,
            not_rest_data_keys=["state"],
            task_vars=task_vars,
        )

        if self._task.args["state"] == "gathered":
            if config:
                self._result["changed"] = False
                self._result[self.module_name]["gathered"] = []
                for item in config:
                    self._result[self.module_name]["gathered"].append(
                        self.search_for_resource_name(
                            conn_request, item["correlation_search_name"]
                        )[0]
                    )

        elif (
            self._task.args["state"] == "merged"
            or self._task.args["state"] == "replaced"
        ):
            (
                self._result[self.module_name],
                self._result["changed"],
            ) = self.configure_module_api(conn_request, config)
            if self._result[self.module_name]["after"] is None:
                self._result[self.module_name].pop("after")

        elif self._task.args["state"] == "deleted":
            (
                self._result[self.module_name],
                self._result["changed"],
            ) = self.delete_module_api_config(conn_request, config)
            if self._result[self.module_name]["after"] is None:
                self._result[self.module_name].pop("after")

        return self._result
