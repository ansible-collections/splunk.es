.. _splunk.es.splunk_finding_module:


************************
splunk.es.splunk_finding
************************

**Manage Splunk Enterprise Security findings**


Version added: 3.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for creation and update of Splunk Enterprise Security findings.
- When ``ref_id`` is not provided, a new finding is always created (no idempotency check).
- When ``ref_id`` is provided, the module will check if the finding exists and update it.
- Update operations use a different API endpoint and only support updating ``owner``, ``status``, ``urgency``, and ``disposition``.
- Tested against Splunk Enterprise Server with Splunk Enterprise Security installed.




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
                    <b>api_app</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"SplunkEnterpriseSecuritySuite"</div>
                </td>
                <td>
                        <div>The app portion of the Splunk API path for the findings endpoint.</div>
                        <div>Override this if your environment uses a different app name.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                <td colspan="2">
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
                        <div>Description of the finding.</div>
                        <div>Required when creating a new finding.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                        <div>Disposition of the finding.</div>
                        <div>Can be updated on existing findings.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>entity</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The risk object (entity) associated with the finding.</div>
                        <div>Required when creating a new finding.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>entity_type</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>user</li>
                                    <li>system</li>
                        </ul>
                </td>
                <td>
                        <div>The type of the risk object (entity).</div>
                        <div>Required when creating a new finding.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>fields</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of custom fields to add to the finding.</div>
                        <div>Only used when creating new findings.</div>
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
                        <div>Name of the custom field.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>value</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Value of the custom field.</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>finding_score</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The risk score for the finding.</div>
                        <div>Required when creating a new finding.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                        <div>Owner of the finding.</div>
                        <div>Can be updated on existing findings.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>ref_id</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Reference ID (finding ID / event_id) of an existing finding.</div>
                        <div>Format is typically <code>uuid@@notable@@time{timestamp}</code> (e.g., <code>2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865</code>).</div>
                        <div>If provided, the module will verify the finding exists and update it.</div>
                        <div>If not provided, a new finding is created.</div>
                        <div>When updating, only <code>owner</code>, <code>status</code>, <code>urgency</code>, and <code>disposition</code> can be modified.</div>
                </td>
            </tr>
            <tr>
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
                                    <li>threat</li>
                                    <li>identity</li>
                                    <li>audit</li>
                        </ul>
                </td>
                <td>
                        <div>Security domain for the finding.</div>
                        <div>Required when creating a new finding.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                        <div>Status of the finding.</div>
                        <div>Can be updated on existing findings.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>title</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Title of the finding.</div>
                        <div>Required when creating a new finding (without <code>ref_id</code>).</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                        </ul>
                </td>
                <td>
                        <div>Urgency level of the finding.</div>
                        <div>Can be updated on existing findings.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Create a new finding (no ref_id - always creates new)
    - name: Create a finding
      splunk.es.splunk_finding:
        title: "Suspicious Login Activity"
        description: "Multiple failed login attempts detected"
        security_domain: access
        entity: "testuser"
        entity_type: user
        finding_score: 50
        owner: admin
        status: new
        urgency: high
        disposition: undetermined

    # Create a finding with custom fields
    - name: Create a finding with custom fields
      splunk.es.splunk_finding:
        title: "Malware Detection"
        description: "Potential malware detected on endpoint"
        security_domain: endpoint
        entity: "server01"
        entity_type: system
        finding_score: 80
        owner: admin
        status: new
        urgency: critical
        disposition: true_positive
        fields:
          - name: custom_col_a
            value: "value1"
          - name: custom_col_b
            value: "value2"

    # Update an existing finding by ref_id (only owner, status, urgency, disposition can be updated)
    - name: Update finding status
      splunk.es.splunk_finding:
        ref_id: "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
        status: resolved
        disposition: true_positive

    # Update finding owner
    - name: Assign finding to admin
      splunk.es.splunk_finding:
        ref_id: "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
        owner: admin

    # Create a finding with custom API path (for non-standard environments)
    - name: Create a finding with custom API path
      splunk.es.splunk_finding:
        title: "Custom Environment Finding"
        description: "Finding created with custom API path"
        security_domain: network
        entity: "firewall01"
        entity_type: system
        finding_score: 60
        api_namespace: "{{ es_namespace | default('servicesNS') }}"
        api_user: "{{ es_user | default('nobody') }}"
        api_app: "{{ es_app | default('SplunkEnterpriseSecuritySuite') }}"



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
                    <b>finding</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The finding result containing before/after states.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;before&#x27;: None, &#x27;after&#x27;: {&#x27;title&#x27;: &#x27;Suspicious Login Activity&#x27;, &#x27;description&#x27;: &#x27;Multiple failed login attempts detected&#x27;, &#x27;security_domain&#x27;: &#x27;access&#x27;, &#x27;entity&#x27;: &#x27;testuser&#x27;, &#x27;entity_type&#x27;: &#x27;user&#x27;, &#x27;finding_score&#x27;: 50, &#x27;owner&#x27;: &#x27;admin&#x27;, &#x27;status&#x27;: &#x27;new&#x27;, &#x27;urgency&#x27;: &#x27;high&#x27;, &#x27;disposition&#x27;: &#x27;undetermined&#x27;}}</div>
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
                            <div>The finding state after module execution.</div>
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
                <td>when finding existed</td>
                <td>
                            <div>The finding state before module execution (if existed).</div>
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
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">Finding created/updated successfully</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Ansible Security Automation Team (@ansible-security) <https://github.com/ansible-security>
