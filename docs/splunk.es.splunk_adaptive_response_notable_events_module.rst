.. _splunk.es.splunk_adaptive_response_notable_events_module:


*************************************************
splunk.es.splunk_adaptive_response_notable_events
*************************************************

**Manage Adaptive Responses notable events resource module**


Version added: 2.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for creation, deletion, and modification of Splunk Enterprise Security Notable Event Adaptive Responses that are associated with a correlation search
- Tested against Splunk Enterprise Server 8.2.3




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="3">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>config</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Configure file and directory monitoring on the system</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>correlation_search_name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name of correlation search to associate this notable event adaptive response with</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>default_owner</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Default owner of the notable event, if unset it will default to Splunk System Defaults</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>default_status</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>unassigned</li>
                                    <li>new</li>
                                    <li>in progress</li>
                                    <li>pending</li>
                                    <li>resolved</li>
                                    <li>closed</li>
                        </ul>
                </td>
                <td>
                        <div>Default status of the notable event, if unset it will default to Splunk System Defaults</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>description</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Description of the notable event, this will populate the description field for the web console</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>drilldown_earliest_offset</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"$info_min_time$"</div>
                </td>
                <td>
                        <div>Set the amount of time before the triggering event to search for related events. For example, 2h. Use &#x27;$info_min_time$&#x27; to set the drill-down time to match the earliest time of the search</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>drilldown_latest_offset</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"$info_max_time$"</div>
                </td>
                <td>
                        <div>Set the amount of time after the triggering event to search for related events. For example, 1m. Use &#x27;$info_max_time$&#x27; to set the drill-down time to match the latest time of the search</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>drilldown_name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name for drill down search, Supports variable substitution with fields from the matching event.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>drilldown_search</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Drill down search, Supports variable substitution with fields from the matching event.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>extract_artifacts</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Assets and identities to be extracted</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>asset</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>src</li>
                                    <li>dest</li>
                                    <li>dvc</li>
                                    <li>orig_host</li>
                        </ul>
                </td>
                <td>
                        <div>list of assets to extract, select any one or many of the available choices</div>
                        <div>defaults to all available choices</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>file</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>list of files to extract</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>identity</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>user</li>
                                    <li>src_user</li>
                                    <li>src_user_id</li>
                                    <li>user_id</li>
                                    <li>src_user_role</li>
                                    <li>user_role</li>
                                    <li>vendor_account</li>
                        </ul>
                </td>
                <td>
                        <div>list of identity fields to extract, select any one or many of the available choices</div>
                        <div>defaults to &#x27;user&#x27; and &#x27;src_user&#x27;</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>url</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>list of URLs to extract</div>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>investigation_profiles</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Investigation profile to associate the notable event with.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name of notable event</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>next_steps</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of adaptive responses that should be run next</div>
                        <div>Describe next steps and response actions that an analyst could take to address this threat.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>recommended_actions</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of adaptive responses that are recommended to be run next</div>
                        <div>Identifying Recommended Adaptive Responses will highlight those actions for the analyst when looking at the list of response actions available, making it easier to find them among the longer list of available actions.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>security_domain</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>access</li>
                                    <li>endpoint</li>
                                    <li>network</li>
                                    <li><div style="color: blue"><b>threat</b>&nbsp;&larr;</div></li>
                                    <li>identity</li>
                                    <li>audit</li>
                        </ul>
                </td>
                <td>
                        <div>Splunk Security Domain</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>severity</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>informational</li>
                                    <li>low</li>
                                    <li>medium</li>
                                    <li><div style="color: blue"><b>high</b>&nbsp;&larr;</div></li>
                                    <li>critical</li>
                                    <li>unknown</li>
                        </ul>
                </td>
                <td>
                        <div>Severity rating</div>
                </td>
            </tr>

            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>running_config</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The module, by default, will connect to the remote device and retrieve the current running-config to use as a base for comparing against the contents of source. There are times when it is not desirable to have the task get the current running-config for every task in a playbook.  The <em>running_config</em> argument allows the implementer to pass in the configuration to use as the base config for comparison. This value of this option should be the output received from device by executing command.</div>
                </td>
            </tr>
            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>merged</b>&nbsp;&larr;</div></li>
                                    <li>replaced</li>
                                    <li>deleted</li>
                                    <li>gathered</li>
                        </ul>
                </td>
                <td>
                        <div>The state the configuration should be left in</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Using gathered
    # --------------

    - name: Gather adaptive response notable events config
      splunk.es.splunk_adaptive_response_notable_events:
        config:
          - correlation_search_name: Ansible Test
          - correlation_search_name: Ansible Test 2
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "correlation_search_name": "Ansible Test",
    #         "description": "test notable event",
    #         "drilldown_earliest_offset": "$info_min_time$",
    #         "drilldown_latest_offset": "$info_max_time$",
    #         "drilldown_name": "test_drill_name",
    #         "drilldown_search": "test_drill",
    #         "extract_artifacts": {
    #             "asset": [
    #                 "src",
    #                 "dest",
    #                 "dvc",
    #                 "orig_host"
    #             ],
    #             "identity": [
    #                 "src_user",
    #                 "user",
    #                 "src_user_id",
    #                 "src_user_role",
    #                 "user_id",
    #                 "user_role",
    #                 "vendor_account"
    #             ]
    #         },
    #         "investigation_profiles": [
    #             "test profile 1",
    #             "test profile 2",
    #             "test profile 3"
    #         ],
    #         "next_steps": [
    #             "makestreams",
    #             "nbtstat",
    #             "nslookup"
    #         ],
    #         "name": "ansible_test_notable",
    #         "recommended_actions": [
    #             "email",
    #             "logevent",
    #             "makestreams",
    #             "nbtstat"
    #         ],
    #         "security_domain": "threat",
    #         "severity": "high"
    #     },
    #     { } # there is no configuration associated with "/var"
    # ]

    # Using merged
    # ------------

    - name: Example to add config
      splunk.es.splunk_adaptive_response_notable_events:
        config:
          - correlation_search_name: Ansible Test
            description: test notable event
            drilldown_earliest_offset: $info_min_time$
            drilldown_latest_offset: $info_max_time$
            extract_artifacts:
              asset:
                - src
                - dest
              identity:
                - src_user
                - user
                - src_user_id
            next_steps:
              - makestreams
            name: ansible_test_notable
            recommended_actions:
              - email
              - logevent
            security_domain: threat
            severity: high
        state: merged

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "correlation_search_name": "Ansible Test",
    #         "description": "test notable event",
    #         "drilldown_earliest_offset": "$info_min_time$",
    #         "drilldown_latest_offset": "$info_max_time$",
    #         "drilldown_name": "test_drill_name",
    #         "drilldown_search": "test_drill",
    #         "extract_artifacts": {
    #             "asset": [
    #                 "src",
    #                 "dest",
    #                 "dvc",
    #                 "orig_host"
    #             ],
    #             "identity": [
    #                 "src_user",
    #                 "user",
    #                 "src_user_id",
    #                 "src_user_role",
    #                 "user_id",
    #                 "user_role",
    #                 "vendor_account"
    #             ]
    #         },
    #         "investigation_profiles": [
    #             "test profile 1",
    #             "test profile 2",
    #             "test profile 3"
    #         ],
    #         "next_steps": [
    #             "makestreams",
    #             "nbtstat",
    #             "nslookup"
    #         ],
    #         "name": "ansible_test_notable",
    #         "recommended_actions": [
    #             "email",
    #             "logevent",
    #             "makestreams",
    #             "nbtstat"
    #         ],
    #         "security_domain": "threat",
    #         "severity": "high"
    #     }
    # ],
    # "before": [],

    # Using replaced
    # --------------

    - name: Example to Replace the config
      splunk.es.splunk_adaptive_response_notable_events:
        config:
          - correlation_search_name: Ansible Test
            description: test notable event
            drilldown_earliest_offset: $info_min_time$
            drilldown_latest_offset: $info_max_time$
            extract_artifacts:
              asset:
                - src
                - dest
              identity:
                - src_user
                - user
                - src_user_id
            next_steps:
              - makestreams
            name: ansible_test_notable
            recommended_actions:
              - email
              - logevent
            security_domain: threat
            severity: high
        state: replaced

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "correlation_search_name": "Ansible Test",
    #         "description": "test notable event",
    #         "drilldown_earliest_offset": "$info_min_time$",
    #         "drilldown_latest_offset": "$info_max_time$",
    #         "extract_artifacts": {
    #             "asset": [
    #                 "src",
    #                 "dest"
    #             ],
    #             "identity": [
    #                 "src_user",
    #                 "user",
    #                 "src_user_id"
    #             ]
    #         },
    #         "next_steps": [
    #             "makestreams"
    #         ],
    #         "name": "ansible_test_notable",
    #         "recommended_actions": [
    #             "email",
    #             "logevent"
    #         ],
    #         "security_domain": "threat",
    #         "severity": "high"
    #     }
    # ],
    # "before": [
    #     {
    #         "correlation_search_name": "Ansible Test",
    #         "description": "test notable event",
    #         "drilldown_earliest_offset": "$info_min_time$",
    #         "drilldown_latest_offset": "$info_max_time$",
    #         "drilldown_name": "test_drill_name",
    #         "drilldown_search": "test_drill",
    #         "extract_artifacts": {
    #             "asset": [
    #                 "src",
    #                 "dest",
    #                 "dvc",
    #                 "orig_host"
    #             ],
    #             "identity": [
    #                 "src_user",
    #                 "user",
    #                 "src_user_id",
    #                 "src_user_role",
    #                 "user_id",
    #                 "user_role",
    #                 "vendor_account"
    #             ]
    #         },
    #         "investigation_profiles": [
    #             "test profile 1",
    #             "test profile 2",
    #             "test profile 3"
    #         ],
    #         "next_steps": [
    #             "makestreams",
    #             "nbtstat",
    #             "nslookup"
    #         ],
    #         "name": "ansible_test_notable",
    #         "recommended_actions": [
    #             "email",
    #             "logevent",
    #             "makestreams",
    #             "nbtstat"
    #         ],
    #         "security_domain": "threat",
    #         "severity": "high"
    #     }
    # ],

    # USING DELETED
    # -------------

    - name: Example to remove the config
      splunk.es.splunk_adaptive_response_notable_events:
        config:
          - correlation_search_name: Ansible Test
        state: deleted

    # RUN output:
    # -----------

    # "after": [],
    # "before": [
    #     {
    #         "correlation_search_name": "Ansible Test",
    #         "description": "test notable event",
    #         "drilldown_earliest_offset": "$info_min_time$",
    #         "drilldown_latest_offset": "$info_max_time$",
    #         "drilldown_name": "test_drill_name",
    #         "drilldown_search": "test_drill",
    #         "extract_artifacts": {
    #             "asset": [
    #                 "src",
    #                 "dest",
    #                 "dvc",
    #                 "orig_host"
    #             ],
    #             "identity": [
    #                 "src_user",
    #                 "user",
    #                 "src_user_id",
    #                 "src_user_role",
    #                 "user_id",
    #                 "user_role",
    #                 "vendor_account"
    #             ]
    #         },
    #         "investigation_profiles": [
    #             "test profile 1",
    #             "test profile 2",
    #             "test profile 3"
    #         ],
    #         "next_steps": [
    #             "makestreams",
    #             "nbtstat",
    #             "nslookup"
    #         ],
    #         "name": "ansible_test_notable",
    #         "recommended_actions": [
    #             "email",
    #             "logevent",
    #             "makestreams",
    #             "nbtstat"
    #         ],
    #         "security_domain": "threat",
    #         "severity": "high"
    #     }
    # ]



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>after</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when changed</td>
                <td>
                            <div>The configuration as structured data after module completion.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">The configuration returned will always be in the same format of the parameters above.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>before</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The configuration as structured data prior to module invocation.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">The configuration returned will always be in the same format of the parameters above.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>gathered</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>when state is <em>gathered</em></td>
                <td>
                            <div>Facts about the network resource gathered from the remote device as structured data.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">This output will always be in the same format as the module argspec.</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Ansible Security Automation Team (@pranav-bhatt) <https://github.com/ansible-security>
