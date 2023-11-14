.. _splunk.es.splunk_data_inputs_network_module:


************************************
splunk.es.splunk_data_inputs_network
************************************

**Manage Splunk Data Inputs of type TCP or UDP resource module**


Version added: 2.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Module that allows to add/update or delete of TCP and UDP Data Inputs in Splunk.




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
                        <div>Manage and preview protocol input data.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>cipher_suite</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specifies list of acceptable ciphers to use in ssl.</div>
                        <div>Only obtained for TCP SSL configuration present on device.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>connection_host</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>ip</li>
                                    <li>dns</li>
                                    <li>none</li>
                        </ul>
                </td>
                <td>
                        <div>Set the host for the remote server that is sending data.</div>
                        <div><code>ip</code> sets the host to the IP address of the remote server sending data.</div>
                        <div><code>dns</code> sets the host to the reverse DNS entry for the IP address of the remote server sending data.</div>
                        <div><code>none</code> leaves the host as specified in inputs.conf, which is typically the Splunk system hostname.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>datatype</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>cooked</li>
                                    <li>raw</li>
                                    <li>splunktcptoken</li>
                                    <li>ssl</li>
                        </ul>
                </td>
                <td>
                        <div><code>cooked</code> lets one access cooked TCP input information and create new containers for managing cooked data.</div>
                        <div><code>raw</code> lets one manage raw tcp inputs from forwarders.</div>
                        <div><code>splunktcptoken</code> lets one manage receiver access using tokens.</div>
                        <div><code>ssl</code> Provides access to the SSL configuration of a Splunk server. This option does not support states <em>deleted</em> and <em>replaced</em>.</div>
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
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Indicates whether the input is disabled.</div>
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
                </td>
                <td>
                        <div>Host from which the indexer gets data.</div>
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
                </td>
                <td>
                        <div>default Index to store generated events.</div>
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
                        <div>The input port which receives raw data.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>no_appending_timestamp</b>
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
                        <div>If set to true, prevents Splunk software from prepending a timestamp and hostname to incoming events.</div>
                        <div>Only for UDP data input configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>no_priority_stripping</b>
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
                        <div>If set to true, Splunk software does not remove the priority field from incoming syslog events.</div>
                        <div>Only for UDP data input configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>password</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Server certificate password, if any.</div>
                        <div>Only for TCP SSL configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>protocol</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>tcp</li>
                                    <li>udp</li>
                        </ul>
                </td>
                <td>
                        <div>Choose whether to manage TCP or UDP inputs</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>queue</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>parsingQueue</li>
                                    <li>indexQueue</li>
                        </ul>
                </td>
                <td>
                        <div>Specifies where the input processor should deposit the events it reads. Defaults to parsingQueue.</div>
                        <div>Set queue to parsingQueue to apply props.conf and other parsing rules to your data. For more information about props.conf and rules for timestamping and linebreaking, refer to props.conf and the online documentation at &quot;Monitor files and directories with inputs.conf&quot;</div>
                        <div>Set queue to indexQueue to send your data directly into the index.</div>
                        <div>Only applicable for &quot;/tcp/raw&quot; and &quot;/udp&quot; APIs</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>raw_tcp_done_timeout</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specifies in seconds the timeout value for adding a Done-key.</div>
                        <div>If a connection over the port specified by name remains idle after receiving data for specified number of seconds, it adds a Done-key. This implies the last event is completely received.</div>
                        <div>Only for TCP raw input configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>require_client_cert</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Determines whether a client must authenticate.</div>
                        <div>Only for TCP SSL configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>restrict_to_host</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Allows for restricting this input to only accept data from the host specified here.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>root_ca</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Certificate authority list (root file).</div>
                        <div>Only for TCP SSL configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>server_cert</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Full path to the server certificate.</div>
                        <div>Only for TCP SSL configuration.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>source</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Sets the source key/field for events from this input. Defaults to the input file path.</div>
                        <div>Sets the source key initial value. The key is used during parsing/indexing, in particular to set the source field during indexing. It is also the source field used at search time. As a convenience, the chosen string is prepended with &#x27;source::&#x27;.</div>
                        <div>Note that Overriding the source key is generally not recommended. Typically, the input layer provides a more accurate string to aid in problem analysis and investigation, accurately recording the file from which the data was retrieved. Consider use of source types, tagging, and search wildcards before overriding this value.</div>
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
                        <div>Set the source type for events from this input.</div>
                        <div>&quot;sourcetype=&quot; is automatically prepended to &lt;string&gt;.</div>
                        <div>Defaults to audittrail (if signedaudit=true) or fschange (if signedaudit=false).</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>ssl</b>
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
                        <div>Enable or disble ssl for the data stream</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>token</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Token value to use for SplunkTcpToken. If unspecified, a token is generated automatically.</div>
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

    # Using gathered
    # --------------

    - name: Gathering information about TCP Cooked Inputs
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: cooked
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "connection_host": "ip",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "8101"
    #     },
    #     {
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "9997"
    #     },
    #     {
    #         "connection_host": "ip",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8101",
    #         "restrict_to_host": "default"
    #     }
    # ]


    - name: Gathering information about TCP Cooked Inputs by Name
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: cooked
            name: 9997
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "datatype": "cooked",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "name": "9997",
    #         "protocol": "tcp"
    #     }
    # ]


    - name: Gathering information about TCP Raw Inputs
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: raw
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "connection_host": "ip",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "8099",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 10
    #     },
    #     {
    #         "connection_host": "ip",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8100",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 10,
    #         "restrict_to_host": "default",
    #         "source": "test_source",
    #         "sourcetype": "test_source_type"
    #     }
    # ]

    - name: Gathering information about TCP Raw inputs by Name
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: raw
            name: 8099
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "raw",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "8099",
    #         "protocol": "tcp",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 10
    #     }
    # ]

    - name: Gathering information about TCP SSL configuration
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: ssl
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "cipher_suite": <cipher-suites>,
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "test_host"
    #     }
    # ]

    - name: Gathering information about TCP SplunkTcpTokens
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: splunktcptoken
        state: gathered

    # RUN output:
    # -----------

    # "gathered": [
    #     {
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "splunktcptoken://test_token1",
    #         "token": <token1>
    #     },
    #     {
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "splunktcptoken://test_token2",
    #         "token": <token2>
    #     }
    # ]

    # Using merged
    # ------------

    - name: To add the TCP raw config
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: raw
            name: 8100
            connection_host: ip
            disabled: true
            raw_tcp_done_timeout: 9
            restrict_to_host: default
            queue: parsingQueue
            source: test_source
            sourcetype: test_source_type
        state: merged

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "raw",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8100",
    #         "protocol": "tcp",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 9,
    #         "restrict_to_host": "default",
    #         "source": "test_source",
    #         "sourcetype": "test_source_type"
    #     }
    # ],
    # "before": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "raw",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8100",
    #         "protocol": "tcp",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 10,
    #         "restrict_to_host": "default",
    #         "source": "test_source",
    #         "sourcetype": "test_source_type"
    #     }
    # ]

    - name: To add the TCP cooked config
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: cooked
            name: 8101
            connection_host: ip
            disabled: false
            restrict_to_host: default
        state: merged

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "cooked",
    #         "disabled": false,
    #         "host": "$decideOnStartup",
    #         "name": "default:8101",
    #         "protocol": "tcp",
    #         "restrict_to_host": "default"
    #     }
    # ],
    # "before": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "cooked",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "name": "default:8101",
    #         "protocol": "tcp",
    #         "restrict_to_host": "default"
    #     }
    # ],

    - name: To add the Splunk TCP token
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: splunktcptoken
            name: test_token
        state: merged

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "datatype": "splunktcptoken",
    #         "name": "splunktcptoken://test_token",
    #         "protocol": "tcp",
    #         "token": <token>
    #     }
    # ],
    # "before": [],

    - name: To add the Splunk SSL
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: ssl
            name: test_host
            root_ca: {root CA directory}
            server_cert: {server cretificate directory}
        state: merged

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "cipher_suite": <cipher suite>,
    #         "datatype": "ssl",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "test_host",
    #         "protocol": "tcp"
    #     }
    # ],
    # "before": []


    # Using deleted
    # -------------

    - name: To Delete TCP Raw
      splunk.es.splunk_data_inputs_network:
        config:
          - protocol: tcp
            datatype: raw
            name: default:8100
        state: deleted

    # RUN output:
    # -----------

    # "after": [],
    # "before": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "raw",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8100",
    #         "protocol": "tcp",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 9,
    #         "restrict_to_host": "default",
    #         "source": "test_source",
    #         "sourcetype": "test_source_type"
    #     }
    # ]

    # Using replaced
    # --------------

    - name: Replace existing data inputs networks configuration
      register: result
      splunk.es.splunk_data_inputs_network:
        state: replaced
        config:
          - protocol: tcp
            datatype: raw
            name: 8100
            connection_host: ip
            disabled: true
            host: "$decideOnStartup"
            index: default
            queue: parsingQueue
            raw_tcp_done_timeout: 10
            restrict_to_host: default
            source: test_source
            sourcetype: test_source_type

    # RUN output:
    # -----------

    # "after": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "raw",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8100",
    #         "protocol": "tcp",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 9,
    #         "restrict_to_host": "default",
    #         "source": "test_source",
    #         "sourcetype": "test_source_type"
    #     }
    # ],
    # "before": [
    #     {
    #         "connection_host": "ip",
    #         "datatype": "raw",
    #         "disabled": true,
    #         "host": "$decideOnStartup",
    #         "index": "default",
    #         "name": "default:8100",
    #         "protocol": "tcp",
    #         "queue": "parsingQueue",
    #         "raw_tcp_done_timeout": 10,
    #         "restrict_to_host": "default",
    #         "source": "test_source",
    #         "sourcetype": "test_source_type"
    #     }
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
                            <div>The resulting configuration after module execution.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">This output will always be in the same format as the module argspec.</div>
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
                <td>when state is <em>merged</em>, <em>replaced</em>, <em>deleted</em></td>
                <td>
                            <div>The configuration prior to the module execution.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">This output will always be in the same format as the module argspec.</div>
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
