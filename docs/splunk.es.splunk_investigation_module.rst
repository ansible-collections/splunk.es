.. _splunk.es.splunk_investigation_module:


******************************
splunk.es.splunk_investigation
******************************

**Manage Splunk Enterprise Security investigations**


Version added: 5.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for creation and update of Splunk Enterprise Security investigations.
- When ``investigation_ref_id`` is not provided, a new investigation is created.
- When ``investigation_ref_id`` is provided, the module will update the existing investigation.
- Update operations can modify all fields except ``name``.




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
                    <b>description</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The description of the investigation.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>disposition</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>unassigned</li>
                                    <li>true_positive</li>
                                    <li>benign_positive</li>
                                    <li>false_positive</li>
                                    <li>false_positive_inaccurate_data</li>
                                    <li>other</li>
                                    <li>undetermined</li>
                        </ul>
                </td>
                <td>
                        <div>The disposition of the investigation.</div>
                        <div>Can be updated on existing investigations.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>finding_ids</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of finding IDs (event_ids) to attach to the investigation.</div>
                        <div>When updating, findings are added to the investigation via a separate API call.</div>
                        <div>Finding IDs can only be added, removal is not supported.</div>
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
                        <div>Reference ID of an existing investigation.</div>
                        <div>If provided, the module will update the existing investigation.</div>
                        <div>If not provided, a new investigation is created.</div>
                        <div>When updating, all fields except <code>name</code> can be modified.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>investigation_type</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The type of the investigation.</div>
                        <div>If not specified, the default investigation type is used.</div>
                        <div>Can be updated on existing investigations.</div>
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
                        <div>The name of the investigation.</div>
                        <div>Required when creating a new investigation (without <code>investigation_ref_id</code>).</div>
                        <div>Cannot be updated after creation.</div>
                        <div>Note that names are not unique - multiple investigations can have the same name.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>owner</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The owner of the investigation.</div>
                        <div>Use <code>admin</code> for the administrator user.</div>
                        <div>Use <code>unassigned</code> to leave the investigation unassigned.</div>
                        <div>Can be updated on existing investigations.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>sensitivity</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>white</li>
                                    <li>green</li>
                                    <li>amber</li>
                                    <li>red</li>
                                    <li>unassigned</li>
                        </ul>
                </td>
                <td>
                        <div>The sensitivity of the investigation.</div>
                        <div>Can be updated on existing investigations.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>status</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>unassigned</li>
                                    <li>new</li>
                                    <li>in_progress</li>
                                    <li>pending</li>
                                    <li>resolved</li>
                                    <li>closed</li>
                        </ul>
                </td>
                <td>
                        <div>The status of the investigation.</div>
                        <div>Can be updated on existing investigations.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>urgency</b>
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
                                    <li>high</li>
                                    <li>critical</li>
                                    <li>unknown</li>
                        </ul>
                </td>
                <td>
                        <div>The urgency of the investigation.</div>
                        <div>Can be updated on existing investigations.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Create a new investigation
    - name: Create an investigation
      splunk.es.splunk_investigation:
        name: "Security Incident 2026-01"
        description: "Investigation into suspicious login activity"
        status: new
        owner: admin
        urgency: high
        sensitivity: amber
        disposition: undetermined

    # Create an investigation with findings attached
    - name: Create investigation with findings
      splunk.es.splunk_investigation:
        name: "Malware Investigation"
        description: "Investigation into potential malware detection"
        status: new
        owner: admin
        urgency: critical
        sensitivity: red
        finding_ids:
          - "A265ED94-AE9E-428C-91D2-64BB956EB7CB@@notable@@62eaebb8c0dd2574fc0b3503a9586cd9"

    # Create an investigation with a specific type
    - name: Create investigation with investigation type
      splunk.es.splunk_investigation:
        name: "Phishing Investigation"
        description: "Investigation into phishing attempt"
        status: new
        owner: admin
        urgency: high
        investigation_type: "phishing"

    # Update an existing investigation status
    - name: Update investigation status
      splunk.es.splunk_investigation:
        investigation_ref_id: "inv-12345-abcde"
        status: in_progress
        owner: analyst1

    # Update investigation disposition
    - name: Close investigation as resolved
      splunk.es.splunk_investigation:
        investigation_ref_id: "inv-12345-abcde"
        status: resolved
        disposition: true_positive
        urgency: low

    # Add findings to an existing investigation
    - name: Add findings to investigation
      splunk.es.splunk_investigation:
        investigation_ref_id: "inv-12345-abcde"
        finding_ids:
          - "B376FE05-BF9F-539D-A2E3-75CC067FC8DC@@notable@@73fbccc9d1ee3685gd1c4614b0697de0"



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
                    <b>changed</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>Whether any changes were made.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">True</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>investigation</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The investigation result containing before/after states.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;before&#x27;: None, &#x27;after&#x27;: {&#x27;name&#x27;: &#x27;Security Incident 2026-01&#x27;, &#x27;description&#x27;: &#x27;Investigation into suspicious login activity&#x27;, &#x27;status&#x27;: &#x27;new&#x27;, &#x27;owner&#x27;: &#x27;admin&#x27;, &#x27;urgency&#x27;: &#x27;high&#x27;, &#x27;sensitivity&#x27;: &#x27;amber&#x27;, &#x27;disposition&#x27;: &#x27;undetermined&#x27;, &#x27;investigation_type&#x27;: &#x27;phishing&#x27;}}</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>after</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The investigation state after module execution.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>before</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>when investigation existed</td>
                <td>
                            <div>The investigation state before module execution (if existed).</div>
                    <br/>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>msg</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>Message describing the result.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">Investigation created/updated successfully</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Ron Gershburg (@rgershbu)
