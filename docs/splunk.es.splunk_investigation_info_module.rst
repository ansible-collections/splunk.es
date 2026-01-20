.. _splunk.es.splunk_investigation_info_module:


***********************************
splunk.es.splunk_investigation_info
***********************************

**Gather information about Splunk Enterprise Security Investigations**


Version added: 5.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for querying information about Splunk Enterprise Security Investigations.
- Use this module to retrieve investigation configurations without making changes.
- Query by ``investigation_ref_id`` to fetch a specific investigation.
- Query by ``name`` to filter investigations by exact name match.
- Use ``create_time_min`` and ``create_time_max`` to control the time range of returned investigations.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>api_app</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"missioncontrol"</div>
                </td>
                <td>
                        <div>The app portion of the Splunk API path for the investigations endpoint.</div>
                        <div>Override this if your environment uses a different app name.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>api_namespace</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"servicesNS"</div>
                </td>
                <td>
                        <div>The namespace portion of the Splunk API path.</div>
                        <div>Override this if your environment uses a different namespace.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>api_user</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"nobody"</div>
                </td>
                <td>
                        <div>The user portion of the Splunk API path.</div>
                        <div>Override this if your environment requires a different user context.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>create_time_max</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The maximum time during which investigations were created.</div>
                        <div>All investigations returned have a creation time less than or equal to this value.</div>
                        <div>Accepts relative time (e.g. <code>-30m</code>, <code>now</code>), epoch time, or ISO 8601 time.</div>
                        <div>If not provided, no maximum time filter is applied.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>create_time_min</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The minimum time during which investigations were created.</div>
                        <div>All investigations returned have a creation time greater than or equal to this value.</div>
                        <div>Accepts relative time (e.g. <code>-30m</code>, <code>-7d</code>, <code>-1w</code>), epoch time, or ISO 8601 time.</div>
                        <div>If not provided, no minimum time filter is applied.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>investigation_ref_id</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Reference ID (investigation ID) to query a specific investigation.</div>
                        <div>If specified, returns only the investigation with this ID.</div>
                        <div>Takes precedence over <code>name</code> if both are provided.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
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
                        <div>Name to filter investigations.</div>
                        <div>Returns all investigations with an exact name match.</div>
                        <div>Ignored if <code>investigation_ref_id</code> is provided.</div>
                        <div>The <code>create_time_min</code> and <code>create_time_max</code> time filters still apply when querying by name.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: Query specific investigation by ref_id
      splunk.es.splunk_investigation_info:
        investigation_ref_id: "abc-123-def-456"
      register: result

    - name: Display the investigation info
      debug:
        var: result.investigations

    - name: Query investigations by name
      splunk.es.splunk_investigation_info:
        name: "Security Incident 2026-01"
      register: result

    - name: Query investigations by name within a time range
      splunk.es.splunk_investigation_info:
        name: "Security Incident 2026-01"
        create_time_min: "-7d"
        create_time_max: "now"
      register: result

    - name: Display investigations with matching name
      debug:
        var: result.investigations

    - name: Query all investigations
      splunk.es.splunk_investigation_info:
      register: all_investigations

    - name: Display all investigations
      debug:
        var: all_investigations.investigations

    - name: Query investigations created in the last 7 days
      splunk.es.splunk_investigation_info:
        create_time_min: "-7d"
      register: recent_investigations

    - name: Query investigations created in the last 30 days
      splunk.es.splunk_investigation_info:
        create_time_min: "-30d"
      register: all_investigations

    - name: Query investigations from a specific time range (ISO 8601)
      splunk.es.splunk_investigation_info:
        create_time_min: "2026-01-01T00:00:00"
        create_time_max: "2026-01-07T23:59:59"
      register: all_investigations

    - name: Query investigations from a specific time range (epoch)
      splunk.es.splunk_investigation_info:
        create_time_min: "1676497520"
        create_time_max: "1676583920"
      register: all_investigations

    # Query investigations with custom API path (for non-standard environments)
    - name: Query investigations with custom API path
      splunk.es.splunk_investigation_info:
        create_time_min: "-7d"
        api_namespace: "{{ es_namespace | default('servicesNS') }}"
        api_user: "{{ es_user | default('nobody') }}"
        api_app: "{{ es_app | default('missioncontrol') }}"
      register: custom_investigations



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="2">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>investigations</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>List of investigations matching the query</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;investigation_ref_id&#x27;: &#x27;abc-123-def-456&#x27;, &#x27;name&#x27;: &#x27;Security Incident 2026-01&#x27;, &#x27;description&#x27;: &#x27;Investigation into suspicious login activity&#x27;, &#x27;status&#x27;: &#x27;new&#x27;, &#x27;disposition&#x27;: &#x27;undetermined&#x27;, &#x27;owner&#x27;: &#x27;admin&#x27;, &#x27;urgency&#x27;: &#x27;high&#x27;, &#x27;sensitivity&#x27;: &#x27;amber&#x27;, &#x27;finding_ids&#x27;: [&#x27;A265ED94-AE9E-428C-91D2-64BB956EB7CB@@notable@@62eaebb8c0dd2574fc0b3503a9586cd9&#x27;]}]</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>description</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Description of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>disposition</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Disposition of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>finding_ids</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>List of finding IDs attached to the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>investigation_ref_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The unique reference ID of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Name of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>owner</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Owner of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>sensitivity</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Sensitivity level of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>status</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Status of the investigation</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>urgency</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Urgency level of the investigation</div>
                    <br/>
                </td>
            </tr>

    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Ron Gershburg (@rgershbu)
