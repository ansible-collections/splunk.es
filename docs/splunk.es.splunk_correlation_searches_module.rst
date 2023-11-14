.. _splunk.es.splunk_correlation_searches_module:


*************************************
splunk.es.splunk_correlation_searches
*************************************

**Splunk Enterprise Security Correlation searches resource module**


Version added: 2.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for creation, deletion, and modification of Splunk Enterprise Security correlation searches
- Tested against Splunk Enterprise Server v8.2.3 with Splunk Enterprise Security v7.0.1 installed on it.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="4">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="4">
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
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>annotations</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Add context from industry standard cyber security mappings in Splunk Enterprise Security or custom annotations</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>cis20</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify CIS20 annotations</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>custom</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify custom framework and custom annotations</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>custom_annotations</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify annotations associated with custom framework</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>framework</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify annotation framework</div>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>kill_chain_phases</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify Kill 10 annotations</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>mitre_attack</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify MITRE ATTACK annotations</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>nist</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify NIST annotations</div>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>app</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"SplunkEnterpriseSecuritySuite"</div>
                </td>
                <td>
                        <div>Splunk app to associate the correlation seach with</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>cron_schedule</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"*/5 * * * *"</div>
                </td>
                <td>
                        <div>Enter a cron-style schedule.</div>
                        <div>For example <code>&#x27;*/5 * * * *&#x27;</code> (every 5 minutes) or <code>&#x27;0 21 * * *&#x27;</code> (every day at 9 PM).</div>
                        <div>Real-time searches use a default schedule of <code>&#x27;*/5 * * * *&#x27;</code>.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
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
                        <div>Description of the coorelation search, this will populate the description field for the web console</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>disabled</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Disable correlation search</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name of correlation search</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>schedule_priority</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>default</b>&nbsp;&larr;</div></li>
                                    <li>higher</li>
                                    <li>highest</li>
                        </ul>
                </td>
                <td>
                        <div>Raise the scheduling priority of a report. Set to &quot;Higher&quot; to prioritize it above other searches of the same scheduling mode, or &quot;Highest&quot; to prioritize it above other searches regardless of mode. Use with discretion.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>schedule_window</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"0"</div>
                </td>
                <td>
                        <div>Let report run at any time within a window that opens at its scheduled run time, to improve efficiency when there are many concurrently scheduled reports. The &quot;auto&quot; setting automatically determines the best window width for the report.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>scheduling</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>realtime</b>&nbsp;&larr;</div></li>
                                    <li>continuous</li>
                        </ul>
                </td>
                <td>
                        <div>Controls the way the scheduler computes the next execution time of a scheduled search.</div>
                        <div>Learn more: https://docs.splunk.com/Documentation/Splunk/7.2.3/Report/Configurethepriorityofscheduledreports#Real-time_scheduling_and_continuous_scheduling</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>search</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>SPL search string</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>suppress_alerts</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>To suppress alerts from this correlation search or not</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>throttle_fields_to_group_by</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Type the fields to consider for matching events for throttling.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>throttle_window_duration</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>How much time to ignore other events that match the field values specified in Fields to group by.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>time_earliest</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"-24h"</div>
                </td>
                <td>
                        <div>Earliest time using relative time modifiers.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>time_latest</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"now"</div>
                </td>
                <td>
                        <div>Latest time using relative time modifiers.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>trigger_alert</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>once</b>&nbsp;&larr;</div></li>
                                    <li>for each result</li>
                        </ul>
                </td>
                <td>
                        <div>Notable response actions and risk response actions are always triggered for each result. Choose whether the trigger is activated once or for each result.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>trigger_alert_when</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>number of events</b>&nbsp;&larr;</div></li>
                                    <li>number of results</li>
                                    <li>number of hosts</li>
                                    <li>number of sources</li>
                        </ul>
                </td>
                <td>
                        <div>Raise the scheduling priority of a report. Set to &quot;Higher&quot; to prioritize it above other searches of the same scheduling mode, or &quot;Highest&quot; to prioritize it above other searches regardless of mode. Use with discretion.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>trigger_alert_when_condition</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>greater than</b>&nbsp;&larr;</div></li>
                                    <li>less than</li>
                                    <li>equal to</li>
                                    <li>not equal to</li>
                                    <li>drops by</li>
                                    <li>rises by</li>
                        </ul>
                </td>
                <td>
                        <div>Conditional to pass to <code>trigger_alert_when</code></div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>trigger_alert_when_value</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"10"</div>
                </td>
                <td>
                        <div>Value to pass to <code>trigger_alert_when</code></div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>ui_dispatch_context</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Set an app to use for links such as the drill-down search in a notable event or links in an email adaptive response action. If None, uses the Application Context.</div>
                </td>
            </tr>

            <tr>
                <td colspan="4">
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
                <td colspan="4">
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

    - name: Gather correlation searches config
      splunk.es.splunk_correlation_searches:
        config:
          - name: Ansible Test
          - name: Ansible Test 2
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #       "annotations": {
    #           "cis20": [
    #               "test1"
    #           ],
    #           "custom": [
    #               {
    #                   "custom_annotations": [
    #                       "test5"
    #                   ],
    #                   "framework": "test_framework"
    #               }
    #           ],
    #           "kill_chain_phases": [
    #               "test3"
    #           ],
    #           "mitre_attack": [
    #               "test2"
    #           ],
    #           "nist": [
    #               "test4"
    #           ]
    #       },
    #       "app": "DA-ESS-EndpointProtection",
    #       "cron_schedule": "*/5 * * * *",
    #       "description": "test description",
    #       "disabled": false,
    #       "name": "Ansible Test",
    #       "schedule_priority": "default",
    #       "schedule_window": "0",
    #       "scheduling": "realtime",
    #       "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
    #                 'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
    #                 'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
    #                 'n.src" as "src" | where "count">=6',
    #       "suppress_alerts": false,
    #       "throttle_fields_to_group_by": [
    #           "test_field1"
    #       ],
    #       "throttle_window_duration": "5s",
    #       "time_earliest": "-24h",
    #       "time_latest": "now",
    #       "trigger_alert": "once",
    #       "trigger_alert_when": "number of events",
    #       "trigger_alert_when_condition": "greater than",
    #       "trigger_alert_when_value": "10",
    #       "ui_dispatch_context": "SplunkEnterpriseSecuritySuite"
    #     }
    # ]

    # Using merged
    # ------------

    - name: Merge and create new correlation searches configuration
      splunk.es.splunk_correlation_searches:
        config:
          - name: Ansible Test
            disabled: false
            description: test description
            app: DA-ESS-EndpointProtection
            annotations:
              cis20:
                - test1
              mitre_attack:
                - test2
              kill_chain_phases:
                - test3
              nist:
                - test4
              custom:
                - framework: test_framework
                  custom_annotations:
                    - test5
            ui_dispatch_context: SplunkEnterpriseSecuritySuite
            time_earliest: -24h
            time_latest: now
            cron_schedule: "*/5 * * * *"
            scheduling: realtime
            schedule_window: "0"
            schedule_priority: default
            trigger_alert: once
            trigger_alert_when: number of events
            trigger_alert_when_condition: greater than
            trigger_alert_when_value: "10"
            throttle_window_duration: 5s
            throttle_fields_to_group_by:
              - test_field1
            suppress_alerts: false
            search: >
                    '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
                    'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
                    'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
                    'n.src" as "src" | where "count">=6'
        state: merged

    # RUN output:
    # -----------

    # "after": [
    #     {
    #       "annotations": {
    #           "cis20": [
    #               "test1"
    #           ],
    #           "custom": [
    #               {
    #                   "custom_annotations": [
    #                       "test5"
    #                   ],
    #                   "framework": "test_framework"
    #               }
    #           ],
    #           "kill_chain_phases": [
    #               "test3"
    #           ],
    #           "mitre_attack": [
    #               "test2"
    #           ],
    #           "nist": [
    #               "test4"
    #           ]
    #       },
    #       "app": "DA-ESS-EndpointProtection",
    #       "cron_schedule": "*/5 * * * *",
    #       "description": "test description",
    #       "disabled": false,
    #       "name": "Ansible Test",
    #       "schedule_priority": "default",
    #       "schedule_window": "0",
    #       "scheduling": "realtime",
    #       "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
    #                 'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
    #                 'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
    #                 'n.src" as "src" | where "count">=6',
    #       "suppress_alerts": false,
    #       "throttle_fields_to_group_by": [
    #           "test_field1"
    #       ],
    #       "throttle_window_duration": "5s",
    #       "time_earliest": "-24h",
    #       "time_latest": "now",
    #       "trigger_alert": "once",
    #       "trigger_alert_when": "number of events",
    #       "trigger_alert_when_condition": "greater than",
    #       "trigger_alert_when_value": "10",
    #       "ui_dispatch_context": "SplunkEnterpriseSecuritySuite"
    #     },
    # ],
    # "before": [],

    # Using replaced
    # --------------

    - name: Replace existing correlation searches configuration
      splunk.es.splunk_correlation_searches:
        state: replaced
        config:
          - name: Ansible Test
            disabled: false
            description: test description
            app: SplunkEnterpriseSecuritySuite
            annotations:
              cis20:
                - test1
                - test2
              mitre_attack:
                - test3
                - test4
              kill_chain_phases:
                - test5
                - test6
              nist:
                - test7
                - test8
              custom:
                - framework: test_framework2
                  custom_annotations:
                    - test9
                    - test10
            ui_dispatch_context: SplunkEnterpriseSecuritySuite
            time_earliest: -24h
            time_latest: now
            cron_schedule: "*/5 * * * *"
            scheduling: continuous
            schedule_window: auto
            schedule_priority: default
            trigger_alert: once
            trigger_alert_when: number of events
            trigger_alert_when_condition: greater than
            trigger_alert_when_value: 10
            throttle_window_duration: 5s
            throttle_fields_to_group_by:
              - test_field1
              - test_field2
            suppress_alerts: true
            search: >
                    '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
                    'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
                    'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
                    'n.src" as "src" | where "count">=6'

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "annotations": {
    #             "cis20": [
    #                 "test1",
    #                 "test2"
    #             ],
    #             "custom": [
    #                 {
    #                     "custom_annotations": [
    #                         "test9",
    #                         "test10"
    #                     ],
    #                     "framework": "test_framework2"
    #                 }
    #             ],
    #             "kill_chain_phases": [
    #                 "test5",
    #                 "test6"
    #             ],
    #             "mitre_attack": [
    #                 "test3",
    #                 "test4"
    #             ],
    #             "nist": [
    #                 "test7",
    #                 "test8"
    #             ]
    #         },
    #         "app": "SplunkEnterpriseSecuritySuite",
    #         "cron_schedule": "*/5 * * * *",
    #         "description": "test description",
    #         "disabled": false,
    #         "name": "Ansible Test",
    #         "schedule_priority": "default",
    #         "schedule_window": "auto",
    #         "scheduling": "continuous",
    #         "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
    #                   'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
    #                   'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
    #                   'n.src" as "src" | where "count">=6',
    #         "suppress_alerts": true,
    #         "throttle_fields_to_group_by": [
    #             "test_field1",
    #             "test_field2"
    #         ],
    #         "throttle_window_duration": "5s",
    #         "time_earliest": "-24h",
    #         "time_latest": "now",
    #         "trigger_alert": "once",
    #         "trigger_alert_when": "number of events",
    #         "trigger_alert_when_condition": "greater than",
    #         "trigger_alert_when_value": "10",
    #         "ui_dispatch_context": "SplunkEnterpriseSecuritySuite"
    #     }
    # ],
    # "before": [
    #     {
    #         "annotations": {
    #             "cis20": [
    #                 "test1"
    #             ],
    #             "custom": [
    #                 {
    #                     "custom_annotations": [
    #                         "test5"
    #                     ],
    #                     "framework": "test_framework"
    #                 }
    #             ],
    #             "kill_chain_phases": [
    #                 "test3"
    #             ],
    #             "mitre_attack": [
    #                 "test2"
    #             ],
    #             "nist": [
    #                 "test4"
    #             ]
    #         },
    #         "app": "DA-ESS-EndpointProtection",
    #         "cron_schedule": "*/5 * * * *",
    #         "description": "test description",
    #         "disabled": false,
    #         "name": "Ansible Test",
    #         "schedule_priority": "default",
    #         "schedule_window": "0",
    #         "scheduling": "realtime",
    #         "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
    #                   'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
    #                   'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
    #                   'n.src" as "src" | where "count">=6',
    #         "suppress_alerts": false,
    #         "throttle_fields_to_group_by": [
    #             "test_field1"
    #         ],
    #         "throttle_window_duration": "5s",
    #         "time_earliest": "-24h",
    #         "time_latest": "now",
    #         "trigger_alert": "once",
    #         "trigger_alert_when": "number of events",
    #         "trigger_alert_when_condition": "greater than",
    #         "trigger_alert_when_value": "10",
    #         "ui_dispatch_context": "SplunkEnterpriseSecuritySuite"
    #     }
    # ]

    # Using deleted
    # -------------

    - name: Example to delete the corelation search
      splunk.es.splunk_correlation_searches:
        config:
          - name: Ansible Test
        state: deleted

    # RUN output:
    # -----------

    # "after": [],
    # "before": [
    #     {
    #       "annotations": {
    #           "cis20": [
    #               "test1"
    #           ],
    #           "custom": [
    #               {
    #                   "custom_annotations": [
    #                       "test5"
    #                   ],
    #                   "framework": "test_framework"
    #               }
    #           ],
    #           "kill_chain_phases": [
    #               "test3"
    #           ],
    #           "mitre_attack": [
    #               "test2"
    #           ],
    #           "nist": [
    #               "test4"
    #           ]
    #       },
    #       "app": "DA-ESS-EndpointProtection",
    #       "cron_schedule": "*/5 * * * *",
    #       "description": "test description",
    #       "disabled": false,
    #       "name": "Ansible Test",
    #       "schedule_priority": "default",
    #       "schedule_window": "0",
    #       "scheduling": "realtime",
    #       "search": '| tstats summariesonly=true values("Authentication.tag") as "tag",dc("Authentication.user") as "user_count",dc("Authent'
    #                 'ication.dest") as "dest_count",count from datamodel="Authentication"."Authentication" where nodename="Authentication.Fai'
    #                 'led_Authentication" by "Authentication.app","Authentication.src" | rename "Authentication.app" as "app","Authenticatio'
    #                 'n.src" as "src" | where "count">=6',
    #       "suppress_alerts": false,
    #       "throttle_fields_to_group_by": [
    #           "test_field1"
    #       ],
    #       "throttle_window_duration": "5s",
    #       "time_earliest": "-24h",
    #       "time_latest": "now",
    #       "trigger_alert": "once",
    #       "trigger_alert_when": "number of events",
    #       "trigger_alert_when_condition": "greater than",
    #       "trigger_alert_when_value": "10",
    #       "ui_dispatch_context": "SplunkEnterpriseSecuritySuite"
    #     },
    # ],



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
