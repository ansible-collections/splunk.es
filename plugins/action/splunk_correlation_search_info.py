# Copyright 2024 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The action plugin file for splunk_correlation_search_info
"""

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.plugins.action import ActionBase
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)

from ansible_collections.splunk.es.plugins.module_utils.splunk import SplunkRequest
from ansible_collections.splunk.es.plugins.modules.splunk_correlation_search_info import (
    DOCUMENTATION,
)


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self.api_object = "servicesNS/nobody/SplunkEnterpriseSecuritySuite/saved/searches"

    def _check_argspec(self):
        aav = AnsibleArgSpecValidator(
            data=utils.remove_empties(self._task.args),
            schema=DOCUMENTATION,
            schema_format="doc",
            name=self._task.action,
        )
        valid, errors, self._task.args = aav.validate()
        if not valid:
            self._result["failed"] = True
            self._result["msg"] = errors

    def fail_json(self, msg):
        """Replace the AnsibleModule fail_json here
        :param msg: The message for the failure
        :type msg: str
        """
        msg = msg.replace("(basic.py)", self._task.action)
        raise AnsibleActionFail(msg)

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True
        self._result = super(ActionModule, self).run(tmp, task_vars)

        self._check_argspec()
        if self._result.get("failed"):
            return self._result

        conn = Connection(self._connection.socket_path)

        conn_request = SplunkRequest(
            action_module=self,
            connection=conn,
            not_rest_data_keys=["name"],
        )

        search_name = self._task.args.get("name")

        try:
            if search_name:
                # Query specific correlation search by name
                query_dict = conn_request.get_by_path(
                    f"{self.api_object}/{quote(search_name)}",
                )
            else:
                # Query all correlation searches
                query_dict = conn_request.get_by_path(self.api_object)

            self._result["changed"] = False
            self._result["correlation_searches"] = query_dict

        except Exception as e:
            # Handle 404 or other errors gracefully
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                self._result["changed"] = False
                self._result["correlation_searches"] = {}
            else:
                self.fail_json(
                    msg=f"Failed to query correlation search(es): {error_msg}",
                )

        return self._result

