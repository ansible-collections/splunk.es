.. _splunk.es.splunk_investigation_type_module:


***********************************
splunk.es.splunk_investigation_type
***********************************

**Manage Splunk Enterprise Security investigation types**


Version added: 5.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for creation and update of Splunk Enterprise Security investigation types.
- Investigation type names are unique in Splunk ES, so ``name`` is used as the identifier.
- The module creates the investigation type if it does not exist, or updates it if it does.
- Response plans can be associated with investigation types via ``response_plan_ids``.
- **Note:** Investigation types cannot be deleted via the Splunk API, so this module only supports create and update operations.
- **IMPORTANT - Declarative Approach:** The ``response_plan_ids`` parameter is declarative. Whatever response plan IDs you define will be exactly what is associated with the investigation type after the module runs. Any existing associations NOT included in your playbook will be REMOVED.




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
                        <div>The app portion of the Splunk API path for the incident types endpoint.</div>
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
                        <div>The description of the investigation type.</div>
                </td>
            </tr>
            <tr>
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
                        <div>The name of the investigation type.</div>
                        <div>This is the unique identifier and is always required.</div>
                        <div>The name cannot be changed after creation.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>response_plan_ids</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of response plan tempalte UUIDs to associate with this investigation type.</div>
                        <div>Use the <code>splunk_response_plan_info</code> module to get response plan template IDs.</div>
                        <div>If not specified or empty, no response plans will be associated.</div>
                        <div><b>Note:</b> This is declarative - only the IDs listed here will be associated. Any existing associations not in this list will be removed.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Create a new investigation type
    - name: Create investigation type
      splunk.es.splunk_investigation_type:
        name: "Insider Threat"
        description: "Investigation type for insider threat incidents"

    # Create investigation type with response plan associations
    - name: Create investigation type with response plans
      splunk.es.splunk_investigation_type:
        name: "Malware Incident"
        description: "Investigation type for malware-related incidents"
        response_plan_ids:
          - "3415de6d-cdfb-4bdb-a21d-693cde38f1e8"
          - "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    # Update investigation type description
    - name: Update investigation type description
      splunk.es.splunk_investigation_type:
        name: "Insider Threat"
        description: "Updated description for insider threat investigations"

    # Update response plan associations (replaces existing associations)
    - name: Update investigation type response plans
      splunk.es.splunk_investigation_type:
        name: "Malware Incident"
        description: "Investigation type for malware-related incidents"
        response_plan_ids:
          - "new-uuid-1234-5678-abcd-ef1234567890"

    # Remove all response plan associations
    - name: Remove all response plans from investigation type
      splunk.es.splunk_investigation_type:
        name: "Malware Incident"
        description: "Investigation type for malware-related incidents"
        response_plan_ids: []

    # Create investigation type with custom API path
    - name: Create investigation type with custom API path
      splunk.es.splunk_investigation_type:
        name: "Custom Investigation Type"
        description: "Investigation type with custom API configuration"
        api_namespace: "{{ es_namespace | default('servicesNS') }}"
        api_user: "{{ es_user | default('nobody') }}"
        api_app: "{{ es_app | default('missioncontrol') }}"



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
                    <b>investigation_type</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The investigation type result containing before/after states.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;before&#x27;: None, &#x27;after&#x27;: {&#x27;name&#x27;: &#x27;Malware Incident&#x27;, &#x27;description&#x27;: &#x27;Investigation type for malware-related incidents&#x27;, &#x27;response_plan_ids&#x27;: [&#x27;3415de6d-cdfb-4bdb-a21d-693cde38f1e8&#x27;]}}</div>
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
                            <div>The investigation type state after module execution.</div>
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
                <td>when investigation type existed</td>
                <td>
                            <div>The investigation type state before module execution (null if creating).</div>
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
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">Investigation type created successfully</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Ron Gershburg (@rgershbu)
