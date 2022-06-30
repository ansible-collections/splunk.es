.. _splunk.es.splunk_data_inputs_monitors_module:


*************************************
splunk.es.splunk_data_inputs_monitors
*************************************

**Manage Splunk Data Inputs of type Monitor**


Version added: 2.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for addition or deletion of File and Directory Monitor Data Inputs in Splunk.
- Tested against Splunk Enterprise Server 8.2.3




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="2">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="2">
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
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>blacklist</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify a regular expression for a file path. The file path that matches this regular expression is not indexed.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>check_index</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>If set to <code>True</code>, the index value is checked to ensure that it is the name of a valid index.</div>
                        <div>This parameter is not returned back by Splunk while obtaining object information. It is therefore left out while performing idempotency checks</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>check_path</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>If set to <code>True</code>, the name value is checked to ensure that it exists.</div>
                        <div>This parameter is not returned back by Splunk while obtaining object information. It is therefore left out while performing idempotency checks</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>crc_salt</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>A string that modifies the file tracking identity for files in this input. The magic value &lt;SOURCE&gt; invokes special behavior (see admin documentation).</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
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
                        <div>Indicates if input monitoring is disabled.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>follow_tail</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>If set to <code>True</code>, files that are seen for the first time is read from the end.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>host</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"$decideOnStartup"</div>
                </td>
                <td>
                        <div>The value to populate in the host field for events from this data input.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>host_regex</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify a regular expression for a file path. If the path for a file matches this regular expression, the captured value is used to populate the host field for events from this data input. The regular expression must have one capture group.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>host_segment</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Use the specified slash-separate segment of the filepath as the host field value.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>ignore_older_than</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify a time value. If the modification time of a file being monitored falls outside of this rolling time window, the file is no longer being monitored.</div>
                        <div>This parameter is not returned back by Splunk while obtaining object information. It is therefore left out while performing idempotency checks</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>index</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"default"</div>
                </td>
                <td>
                        <div>Which index events from this input should be stored in. Defaults to default.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
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
                        <div>The file or directory path to monitor on the system.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>recursive</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Setting this to False prevents monitoring of any subdirectories encountered within this data input.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>rename_source</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The value to populate in the source field for events from this data input. The same source should not be used for multiple data inputs.</div>
                        <div>This parameter is not returned back by Splunk while obtaining object information. It is therefore left out while performing idempotency checks</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>sourcetype</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The value to populate in the sourcetype field for incoming events.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>time_before_close</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>When Splunk software reaches the end of a file that is being read, the file is kept open for a minimum of the number of seconds specified in this value. After this period has elapsed, the file is checked again for more data.</div>
                        <div>This parameter is not returned back by Splunk while obtaining object information. It is therefore left out while performing idempotency checks</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>whitelist</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify a regular expression for a file path. Only file paths that match this regular expression are indexed.</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
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
                <td colspan="2">
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

    # _________________________________________________________________
    # Using gathered

    - name: gather config for specified data inputs monitors
      splunk.es.data_inputs_monitors:
        config:
          - name: "/var/log"
          - name: "/var"
        state: gathered
    #
    # Output:
    #
    # "changed": false,
    # "gathered": [
    #     {
    #         "blacklist": "//var/log/[a-z0-9]/gm",
    #         "crc_salt": "<SOURCE>",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "host_regex": "/(test_host)/gm",
    #         "host_segment": 3,
    #         "index": "default",
    #         "name": "/var/log",
    #         "recursive": true,
    #         "sourcetype": "test_source",
    #         "whitelist": "//var/log/[0-9]/gm"
    #     },
    #     { } # there is no configuration associated with "/var"
    # ]
    #
    # ------------------------------
    # _________________________________________________________________
    # Using merged
    - name: Example adding config with splunk.es.data_inputs_monitors
      splunk.es.data_inputs_monitors:
        config:
          - name: "/var/log"
            blacklist: "//var/log/[a-z]/gm"
            check_index: True
            check_path: True
            crc_salt: <SOURCE>
            rename_source: "test"
            whitelist: "//var/log/[0-9]/gm"
        state: merged
    #
    # Output:
    #
    # "after": [
    #     {
    #         "blacklist": "//var/log/[a-z]/gm",
    #         "crc_salt": "<SOURCE>",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "host_regex": "/(test_host)/gm",
    #         "host_segment": 3,
    #         "index": "default",
    #         "name": "/var/log",
    #         "recursive": true,
    #         "sourcetype": "test_source",
    #         "whitelist": "//var/log/[0-9]/gm"
    #     }
    # ],
    # "before": [
    #     {
    #         "blacklist": "//var/log/[a-z0-9]/gm",
    #         "crc_salt": "<SOURCE>",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "host_regex": "/(test_host)/gm",
    #         "host_segment": 3,
    #         "index": "default",
    #         "name": "/var/log",
    #         "recursive": true,
    #         "sourcetype": "test_source",
    #         "whitelist": "//var/log/[0-9]/gm"
    #     }
    # ],
    # "changed": true
    #
    # ------------------------------
    # _________________________________________________________________
    # Using replaced

    - name: Example replacing config with splunk.es.data_inputs_monitors
      splunk.es.data_inputs_monitors:
        config:
          - name: "/var/log"
            blacklist: "//var/log/[a-z0-9]/gm"
            crc_salt: <SOURCE>
            index: default
        state: replaced
    #
    # Output:
    #
    # "after": [
    #     {
    #         "blacklist": "//var/log/[a-z0-9]/gm",
    #         "crc_salt": "<SOURCE>",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "/var/log"
    #     }
    # ],
    # "before": [
    #     {
    #         "blacklist": "//var/log/[a-z0-9]/gm",
    #         "crc_salt": "<SOURCE>",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "host_regex": "/(test_host)/gm",
    #         "host_segment": 3,
    #         "index": "default",
    #         "name": "/var/log",
    #         "recursive": true,
    #         "sourcetype": "test_source",
    #         "whitelist": "//var/log/[0-9]/gm"
    #     }
    # ],
    # "changed": true
    #
    # ------------------------------
    # _________________________________________________________________
    # Using deleted
    - name: Example deleting config with splunk.es.data_inputs_monitors
      splunk.es.data_inputs_monitors:
        config:
          - name: "/var/log"
        state: deleted
    #
    # Output:
    #
    # "after": [],
    # "before": [
    #     {
    #         "blacklist": "//var/log/[a-z0-9]/gm",
    #         "crc_salt": "<SOURCE>",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "/var/log"
    #     }
    # ],
    # "changed": true
    #




Status
------


Authors
~~~~~~~

- Ansible Security Automation Team (@pranav-bhatt) <https://github.com/ansible-security>
