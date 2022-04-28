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
The module file for data_inputs_networks
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils.six.moves.urllib.parse import quote_plus

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
from ansible_collections.splunk.es.plugins.modules.data_inputs_networks import (
    DOCUMENTATION,
)


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self.api_object = "servicesNS/nobody/search/data/inputs"
        self.key_transform = {
            "name": "name",
            "connection_host": "connection_host",
            "disabled": "disabled",
            "index": "index",
            "host": "host",
            "name": "name",
            "no_appending_timestamp": "no_appending_timestamp",
            "no_priority_stripping": "no_priority_stripping",
            "rawTcpDoneTimeout": "raw_tcp_done_timeout",
            "restrictToHost": "restrict_to_host",
            "queue": "queue",
            "SSL": "ssl",
            "source": "source",
            "sourcetype": "sourcetype",
            "token": "token",
            "password": "password",
            "requireClientCert": "require_client_cert",
            "rootCA": "root_ca",
            "serverCert": "server_cert",
            "cipherSuite": "cipher_suite",
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

    def map_params_to_object(self, config, datatype=None):
        res = {}

        res["name"] = config["name"]
        res.update(map_params_to_obj(config["content"], self.key_transform))

        # API returns back "index", even though it can't be set within /tcp/cooked
        if datatype:
            if datatype == "cooked":
                res.pop("index")
            elif datatype == "splunktcptoken":
                res.pop("index")
                res.pop("host")
                res.pop("disabled")

        return res

    # This function is meant to construct the URL and handle GET, POST and DELETE calls
    # depending on th context. The URLs constructed and handled are:
    # /tcp/raw[/{name}]
    # /tcp/cooked[/{name}]
    # /tcp/splunktcptoken[/{name}]
    # /tcp/ssl[/{name}]
    # /udp[/{name}]
    def request_by_path(self, conn_request, protocol, datatype=None, name=None, req_type="get", payload=None):
        query_dict = None
        url = ""
        if protocol == "tcp":
            if not datatype:
                raise AnsibleActionFail("No datatype specified for TCP input")

            # In all cases except "ssl" datatype, creation of objects is handled
            # by a POST request to the parent directory. Therefore name shouldn't
            # be included in the URL.
            if not name or (req_type == "post_create" and datatype != "ssl"):
                name = ""

            url = "{0}/{1}/{2}/{3}".format(
                self.api_object,
                protocol,
                datatype,
                quote_plus(str(name)),
            )
            # if no "name" was provided
            if url[-1] == "/":
                url = url[:-1]

        elif protocol == "udp":
            if datatype:
                raise AnsibleActionFail("Datatype specified for UDP input")
            if not name or req_type == "post_create":
                name = ""

            url = "{0}/{1}/{2}".format(
                self.api_object,
                protocol,
                quote_plus(str(name)),
            )
            # if no "name" was provided
            if url[-1] == "/":
                url = url[:-1]
        else:
            raise AnsibleActionFail("Incompatible protocol specified. Please specify 'tcp' or 'udp'")

        if req_type == "get":
            query_dict = conn_request.get_by_path(url)
        elif req_type == "post_create":
            query_dict = conn_request.create_update(url, data=payload)
        elif req_type == "post_update":
            payload.pop("name")
            query_dict = conn_request.create_update(url, data=payload)
        elif req_type == "delete":
            query_dict = conn_request.delete_by_path(url)

        return query_dict

    def search_for_resource_name(self, conn_request, protocol, datatype, name):
        query_dict = self.request_by_path(
            conn_request,
            protocol,
            datatype,
            name,
        )

        search_result = {}

        if query_dict:
            search_result = self.map_params_to_object(query_dict["entry"][0], datatype)

            # Adding back protocol and datatype fields for better clarity
            search_result["protocol"] = protocol
            search_result["datatype"] = datatype

        return search_result

    def delete_module_api_config(self, conn_request, config):
        before = []
        after = None
        changed = False
        for want_conf in config:
            search_by_name = self.search_for_resource_name(
                conn_request,
                want_conf["protocol"],
                want_conf.get("datatype"),
                want_conf["name"],
            )
            if search_by_name:
                before.append(search_by_name)
                self.request_by_path(
                    conn_request,
                    want_conf["protocol"],
                    want_conf.get("datatype"),
                    want_conf["name"],
                    req_type="delete",
                )
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
            "datatype",
            "protocol",
        ]
        for want_conf in config:
            old_name = ""
            remove_from_diff_compare = [
                "datatype",
                "protocol",
            ]

            protocol = want_conf["protocol"]
            datatype = want_conf.get("datatype")

            if not want_conf.get("name"):
                raise AnsibleActionFail("No name specified for merge action")
            else:
                # Int values confuse diff
                want_conf["name"] = str(want_conf["name"])

                old_name = want_conf["name"]

                # If "restrictToHost" parameter is set, the value of this parameter is appended
                # to the numerical name meant to represent port number
                if want_conf.get("restrict_to_host") and want_conf["restrict_to_host"] not in want_conf["name"]:
                    want_conf["name"] = "{0}:{1}".format(want_conf["restrict_to_host"], want_conf["name"])

                # If datatype is "splunktcptoken", the value "splunktcptoken://" is appended
                # to the name
                elif datatype and datatype == "splunktcptoken" and "splunktcptoken://" not in want_conf["name"]:
                    want_conf["name"] = "{0}{1}".format("splunktcptoken://", want_conf["name"])

            name = want_conf["name"]

            # If the "restrictToHost" option is enabled, but the object doesn't exist
            # the "restrictToHost" value should not be prepended to the name otherwise
            # Splunk returns 400
            have_conf = None
            try:
                have_conf = self.search_for_resource_name(
                    conn_request,
                    protocol,
                    datatype,
                    name,
                )
            except:
                want_conf["name"] = old_name
                have_conf = self.search_for_resource_name(
                    conn_request,
                    protocol,
                    datatype,
                    old_name,
                )

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
                            api_response = self.request_by_path(
                                conn_request,
                                protocol,
                                datatype,
                                name,
                                req_type="post_update",
                                payload=payload,
                            )
                            response_json = self.map_params_to_object(api_response["entry"][0], datatype)

                            # Adding back protocol and datatype fields for better clarity
                            response_json["protocol"] = protocol
                            if datatype:
                                response_json["datatype"] = datatype

                            after.append(response_json)
                        elif self._task.args["state"] == "replaced":
                            api_response = self.request_by_path(
                                conn_request,
                                protocol,
                                datatype,
                                name,
                                req_type="delete",
                            )
                            changed = True

                            payload = map_obj_to_params(want_conf, self.key_transform)
                            api_response = self.request_by_path(
                                conn_request,
                                payload,
                                datatype,
                                name,
                                req_type="post_create",
                                payload=payload,
                            )
                            response_json = self.map_params_to_object(api_response["entry"][0], datatype)

                            # Adding back protocol and datatype fields for better clarity
                            response_json["protocol"] = protocol
                            if datatype:
                                response_json["datatype"] = datatype

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
                api_response = self.request_by_path(
                    conn_request,
                    protocol,
                    datatype,
                    name,
                    req_type="post_create",
                    payload=payload,
                )
                response_json = self.map_params_to_object(api_response["entry"][0], datatype)

                # Adding back protocol and datatype fields for better clarity
                response_json["protocol"] = protocol
                if datatype:
                    response_json["datatype"] = datatype

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
                    if item.get("name"):
                        self._result["gathered"].append(
                            self.search_for_resource_name(
                                conn_request,
                                item["protocol"],
                                item.get("datatype"),
                                item.get("name"),
                            )
                        )
                    else:
                        response_list = self.request_by_path(
                            conn_request,
                            item["protocol"],
                            item.get("datatype"),
                            None,
                        )["entry"]
                        self._result["gathered"] = []
                        for response_dict in response_list:
                            self._result["gathered"].append(
                                self.map_params_to_object(response_dict),
                            )
            else:
                raise AnsibleActionFail("No protocol specified")

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
