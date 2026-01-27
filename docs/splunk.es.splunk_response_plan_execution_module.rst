.. _splunk.es.splunk_response_plan_execution_module:


****************************************
splunk.es.splunk_response_plan_execution
****************************************

**Apply response plans to investigations and manage tasks**


Version added: 5.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module applies or removes response plans from Splunk Enterprise Security investigations.
- It also manages task lifecycle within applied response plans (start, end, change owner).
- The ``response_plan`` parameter accepts either a UUID or a name.
- When ``state=present``, the response plan is applied to the investigation.
- When ``state=absent``, the response plan is removed from the investigation.
- Use the ``tasks`` parameter to manage individual task statuses and owners within the applied plan.




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
                        <b>Default:</b><br/><div style="color: blue">"missioncontrol"</div>
                </td>
                <td>
                        <div>The app portion of the Splunk API path.</div>
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
                    <b>investigation_ref_id</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The investigation UUID to apply or manage response plans.</div>
                        <div>This is the unique identifier of the investigation in Splunk ES.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>response_plan</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The response plan template to apply or remove.</div>
                        <div>Accepts either a UUID (e.g., &quot;2dc5530d-8bb0-4a4f-9b53-74745bf4ea6a&quot;) or a name (e.g., &quot;Incident Response Plan&quot;).</div>
                        <div>If UUID format is detected, it is used directly as the template ID.</div>
                        <div>If not a UUID, the module performs an API lookup to resolve the name to an ID.</div>
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
                                    <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                    <li>absent</li>
                        </ul>
                </td>
                <td>
                        <div>The desired state of the response plan on the investigation.</div>
                        <div>Use <code>present</code> to apply the response plan to the investigation or update the tasks.</div>
                        <div>Use <code>absent</code> to remove the response plan from the investigation.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                        <div>List of tasks to manage within the applied response plan.</div>
                        <div>Each task is identified by phase name and task name.</div>
                        <div>You can set the task status (started/ended) and/or change the owner.</div>
                        <div>Tasks are only managed when <code>state=present</code>.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
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
                        <div>The owner/assignee of the task.</div>
                        <div>Use <code>admin</code> for the administrator user.</div>
                        <div>Use <code>unassigned</code> to remove the current owner or leave unassigned.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>phase_name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The name of the phase containing the task.</div>
                        <div>Used to look up the phase ID within the applied response plan.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
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
                                    <li>started</li>
                                    <li>ended</li>
                                    <li>reopened</li>
                        </ul>
                </td>
                <td>
                        <div>The desired status of the task.</div>
                        <div>Use <code>started</code> to mark the task as in progress.</div>
                        <div>Use <code>ended</code> to mark the task as completed.</div>
                        <div>Use <code>reopened</code> to reopen a completed task.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>task_name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The name of the task to manage.</div>
                        <div>Used to look up the task ID within the phase.</div>
                </td>
            </tr>

    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Apply a response plan to an investigation by name
    - name: Apply response plan to investigation
      splunk.es.splunk_response_plan_execution:
        investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
        response_plan: "Incident Response Plan"
        state: present

    # Apply a response plan by UUID (no lookup needed)
    - name: Apply response plan by ID
      splunk.es.splunk_response_plan_execution:
        investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
        response_plan: "2dc5530d-8bb0-4a4f-9b53-74745bf4ea6a"
        state: present

    # Apply response plan and start a task
    - name: Apply response plan and start initial triage
      splunk.es.splunk_response_plan_execution:
        investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
        response_plan: "Incident Response Plan"
        state: present
        tasks:
          - phase_name: "Investigation Phase"
            task_name: "Initial Triage"
            status: started
            owner: admin

    # Manage multiple tasks in an applied response plan
    - name: Update multiple task statuses
      splunk.es.splunk_response_plan_execution:
        investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
        response_plan: "Incident Response Plan"
        state: present
        tasks:
          - phase_name: "Investigation Phase"
            task_name: "Initial Triage"
            status: ended
            owner: admin
          - phase_name: "Investigation Phase"
            task_name: "Gather Evidence"
            status: started
            owner: analyst1
          - phase_name: "Containment Phase"
            task_name: "Isolate Systems"
            owner: unassigned

    # Remove a response plan from an investigation
    - name: Remove response plan from investigation
      splunk.es.splunk_response_plan_execution:
        investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
        response_plan: "Incident Response Plan"
        state: absent

    # Apply response plan with custom API configuration
    - name: Apply response plan with custom API path
      splunk.es.splunk_response_plan_execution:
        investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
        response_plan: "Custom Response Plan"
        state: present
        api_namespace: "{{ es_namespace | default('servicesNS') }}"
        api_user: "{{ es_user | default('nobody') }}"
        api_app: "{{ es_app | default('missioncontrol') }}"



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="3">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="3">
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
                <td colspan="3">
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
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">Response plan applied successfully</div>
                </td>
            </tr>
            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>response_plan_execution</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The response plan execution result containing before/after states.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;before&#x27;: {&#x27;applied&#x27;: False}, &#x27;after&#x27;: {&#x27;applied&#x27;: True, &#x27;applied_plan_id&#x27;: &#x27;b9ef7dce-6dcd-4900-b5d5-982fc194554a&#x27;, &#x27;response_plan_id&#x27;: &#x27;2dc5530d-8bb0-4a4f-9b53-74745bf4ea6a&#x27;}, &#x27;tasks_updated&#x27;: [{&#x27;phase_name&#x27;: &#x27;Investigation Phase&#x27;, &#x27;task_name&#x27;: &#x27;Initial Triage&#x27;, &#x27;status&#x27;: &#x27;started&#x27;, &#x27;owner&#x27;: &#x27;admin&#x27;, &#x27;changed&#x27;: True}]}</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>after</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The state after module execution.</div>
                    <br/>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>applied</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Whether the response plan is applied after execution.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>applied_plan_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The ID of the applied response plan instance (if applied).</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>response_plan_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The response plan template ID.</div>
                    <br/>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>before</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The state before module execution.</div>
                    <br/>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>applied</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Whether the response plan was applied before execution.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>applied_plan_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The ID of the applied response plan instance (if applied).</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>response_plan_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The response plan template ID.</div>
                    <br/>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>tasks_updated</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>when tasks parameter is provided</td>
                <td>
                            <div>List of tasks that were updated (when tasks parameter is used).</div>
                    <br/>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>changed</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Whether this specific task was changed.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
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
                            <div>The task owner after update.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>phase_name</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The phase name containing the task.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
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
                            <div>The task status after update.</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>task_name</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The task name.</div>
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
