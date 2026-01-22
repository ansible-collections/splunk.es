.. _splunk.es.splunk_response_plan_module:


******************************
splunk.es.splunk_response_plan
******************************

**Manage Splunk Enterprise Security response plans**


Version added: 5.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for creation, update, and deletion of Splunk Enterprise Security response plans (response templates).
- Response plan names are unique in Splunk ES, so ``name`` is used as the identifier.
- When ``state=present``, the module creates or updates the response plan.
- When ``state=absent``, the module deletes the response plan.
- Phases and tasks are matched by name for updates - existing IDs are preserved for items with matching names, and new IDs are generated for new items.
- **IMPORTANT - Declarative Approach:** This module uses a declarative approach where the playbook defines the complete desired state. Whatever you define is exactly what will exist after the module runs. Any existing phases, tasks, or searches that are NOT included in your playbook will be REMOVED. This is not a merge operation - it is a full replacement of the response plan structure.
- For example, if a response plan has phases A, B, C and you only define phase A in your playbook, phases B and C will be deleted. The same applies to tasks within phases and searches within tasks.




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
                        <div>The app portion of the Splunk API path for the response templates endpoint.</div>
                        <div>Override this if your environment uses a different app name.</div>
                </td>
            </tr>
            <tr>
                <td colspan="4">
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
                <td colspan="4">
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
                <td colspan="4">
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
                        <div>The description of the response plan.</div>
                </td>
            </tr>
            <tr>
                <td colspan="4">
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
                        <div>The name of the response plan.</div>
                        <div>This is the unique identifier and is always required.</div>
                        <div>Used to look up existing response plans for update or delete operations.</div>
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>phases</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of phases in the response plan.</div>
                        <div>Required when <code>state=present</code>.</div>
                        <div>Phases are matched by name for updates.</div>
                        <div><b>Note:</b> Only phases defined here will exist after update. Any existing phases not included in this list will be removed from the response plan.</div>
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
                        <div>The name of the phase.</div>
                        <div>Used as identifier for matching during updates.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>tasks</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of tasks in the phase.</div>
                        <div>Tasks are matched by name within their parent phase for updates.</div>
                        <div><b>Note:</b> Only tasks defined here will exist in the phase after update. Any existing tasks not included in this list will be removed.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
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
                        <div>The description of the task.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>is_note_required</b>
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
                        <div>Whether a note is required when completing the task.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
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
                        <div>The name of the task.</div>
                        <div>Used as identifier for matching during updates.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>owner</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"unassigned"</div>
                </td>
                <td>
                        <div>The owner of the task.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>searches</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>List of saved searches to attach to the task.</div>
                        <div>Searches are replaced entirely on update (not merged).</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
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
                        <div>The description of the search.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
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
                        <div>The name of the search.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>spl</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The SPL (Search Processing Language) query.</div>
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
                                    <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                    <li>absent</li>
                        </ul>
                </td>
                <td>
                        <div>The desired state of the response plan.</div>
                        <div>Use <code>present</code> to create or update the response plan.</div>
                        <div>Use <code>absent</code> to delete the response plan.</div>
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>template_status</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>published</li>
                                    <li><div style="color: blue"><b>draft</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>The status of the response plan template.</div>
                        <div>Use <code>draft</code> for work-in-progress plans.</div>
                        <div>Use <code>published</code> for plans ready for use.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Create a new response plan with phases and tasks
    - name: Create incident response plan
      splunk.es.splunk_response_plan:
        name: "Incident Response Plan"
        description: "Standard incident response procedure"
        template_status: published
        phases:
          - name: "Investigation"
            tasks:
              - name: "Initial Triage"
                description: "Perform initial assessment of the incident"
                is_note_required: true
                owner: admin
                searches:
                  - name: "Access Over Time"
                    description: "Check access patterns"
                    spl: "| tstats count from datamodel=Authentication by _time span=10m"
              - name: "Gather Evidence"
                description: "Collect relevant logs and artifacts"
                is_note_required: false
          - name: "Containment"
            tasks:
              - name: "Isolate Affected Systems"
                description: "Isolate compromised hosts from network"
                is_note_required: true

    # Create a draft response plan
    - name: Create draft response plan
      splunk.es.splunk_response_plan:
        name: "New Response Workflow"
        description: "Work in progress response plan"
        template_status: draft
        phases:
          - name: "Phase 1"
            tasks:
              - name: "Task 1"
                description: "First task"

    # Update an existing response plan (adds new task, updates existing)
    - name: Update response plan
      splunk.es.splunk_response_plan:
        name: "Incident Response Plan"
        description: "Updated incident response procedure"
        template_status: published
        phases:
          - name: "Investigation"
            tasks:
              - name: "Initial Triage"
                description: "Updated: Perform thorough initial assessment"
                is_note_required: true
              - name: "New Analysis Task"
                description: "This task will be created"
                is_note_required: false
          - name: "Containment"
            tasks:
              - name: "Isolate Affected Systems"
                description: "Isolate compromised hosts from network"

    # Delete a response plan by name
    - name: Delete response plan
      splunk.es.splunk_response_plan:
        name: "Incident Response Plan"
        state: absent

    # Example: Declarative update - removes phases/tasks not defined
    # If the response plan currently has phases "Investigation", "Containment", "Recovery"
    # but this playbook only defines "Investigation" and "Containment", then the
    # "Recovery" phase will be DELETED. Same applies to tasks within phases.
    - name: Update response plan (removes Recovery phase if it existed)
      splunk.es.splunk_response_plan:
        name: "Incident Response Plan"
        description: "Updated procedure - Recovery phase removed"
        template_status: published
        phases:
          - name: "Investigation"
            tasks:
              - name: "Initial Triage"
                description: "Perform initial assessment"
          - name: "Containment"
            tasks:
              - name: "Isolate Systems"
                description: "Isolate affected systems"

    # Create response plan with custom API path (for non-standard environments)
    - name: Create response plan with custom API path
      splunk.es.splunk_response_plan:
        name: "Custom Response Plan"
        description: "Response plan with custom API configuration"
        template_status: published
        api_namespace: "{{ es_namespace | default('servicesNS') }}"
        api_user: "{{ es_user | default('nobody') }}"
        api_app: "{{ es_app | default('missioncontrol') }}"
        phases:
          - name: "Phase 1"
            tasks:
              - name: "Task 1"
                description: "First task"



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
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">Response plan created successfully</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>response_plan</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The response plan result containing before/after states.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;before&#x27;: None, &#x27;after&#x27;: {&#x27;name&#x27;: &#x27;Incident Response Plan&#x27;, &#x27;description&#x27;: &#x27;Standard incident response procedure&#x27;, &#x27;template_status&#x27;: &#x27;published&#x27;, &#x27;phases&#x27;: [{&#x27;name&#x27;: &#x27;Investigation&#x27;, &#x27;tasks&#x27;: [{&#x27;name&#x27;: &#x27;Initial Triage&#x27;, &#x27;description&#x27;: &#x27;Perform initial assessment&#x27;, &#x27;is_note_required&#x27;: True, &#x27;owner&#x27;: &#x27;admin&#x27;, &#x27;searches&#x27;: [{&#x27;name&#x27;: &#x27;Access Over Time&#x27;, &#x27;description&#x27;: &#x27;Check access patterns&#x27;, &#x27;spl&#x27;: &#x27;| tstats count from datamodel=Authentication&#x27;}]}]}]}}</div>
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
                            <div>The response plan state after module execution (null if deleted).</div>
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
                <td>when response plan existed</td>
                <td>
                            <div>The response plan state before module execution (null if creating).</div>
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
