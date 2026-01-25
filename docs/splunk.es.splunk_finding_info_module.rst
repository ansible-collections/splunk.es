.. _splunk.es.splunk_finding_info_module:


*****************************
splunk.es.splunk_finding_info
*****************************

**Gather information about Splunk Enterprise Security Findings**


Version added: 5.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for querying information about Splunk Enterprise Security Findings.
- Use this module to retrieve finding configurations without making changes.
- Query by ``ref_id`` to fetch a specific finding. Without ``earliest`` and ``latest``.
- Query by ``title`` to filter findings by exact title match.
- Use ``earliest`` and ``latest`` to control the time range of returned findings.
- By default, if ``earliest`` and ``latest`` are not specified, findings from the last 24 hours are returned.
- This default time (24 hours) range applies when querying by ``title`` or all findings (not by ``ref_id``).
- This module uses the httpapi connection plugin and does not require local Splunk SDK.




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
                        <b>Default:</b><br/><div style="color: blue">"SplunkEnterpriseSecuritySuite"</div>
                </td>
                <td>
                        <div>The app portion of the Splunk API path for the findings endpoint.</div>
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
                    <b>earliest</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The earliest time for findings to return.</div>
                        <div>All findings returned have a _time greater than or equal to this value.</div>
                        <div>Accepts relative time (e.g. <code>-30m</code>, <code>-7d</code>, <code>-1w</code>), epoch time, or ISO 8601 time.</div>
                        <div>If not provided, defaults to the last 24 hours (<code>-24h</code>).</div>
                        <div>Ignored when querying by <code>ref_id</code> (time is extracted from ref_id automatically).</div>
                        <div>Applies when querying by <code>title</code> or all findings.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>latest</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The latest time for findings to return.</div>
                        <div>All findings returned have a _time less than or equal to this value.</div>
                        <div>Accepts relative time (e.g. <code>-30m</code>, <code>now</code>), epoch time, or ISO 8601 time.</div>
                        <div>If not provided, defaults to the current time (<code>now</code>).</div>
                        <div>Ignored when querying by <code>ref_id</code> (time is extracted from ref_id automatically).</div>
                        <div>Applies when querying by <code>title</code> or all findings.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>limit</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Maximum number of findings to return.</div>
                        <div>If not specified, all matching findings are returned.</div>
                        <div>Use this to limit large result sets.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
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
                        <div>Reference ID (finding ID) to query a specific finding.</div>
                        <div>If specified, returns only the finding with this ID.</div>
                        <div>Takes precedence over <code>title</code> if both are provided.</div>
                        <div>The time is automatically extracted from the ref_id (format uuid@@notable@@time{timestamp}).</div>
                        <div>When querying by ref_id, the <code>earliest</code> and <code>latest</code> parameters are ignored.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
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
                        <div>Title name to filter findings.</div>
                        <div>Returns all findings with an exact title match.</div>
                        <div>Ignored if <code>ref_id</code> is provided.</div>
                        <div>The <code>earliest</code> and <code>latest</code> time filters still apply when querying by title.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: Query specific finding by ref_id (time extracted automatically from ref_id)
      splunk.es.splunk_finding_info:
        ref_id: "abc-123-def-456@@notable@@time1234567890"
      register: result

    - name: Display the finding info
      debug:
        var: result.findings

    - name: Query findings by title (from last 24 hours by default)
      splunk.es.splunk_finding_info:
        title: "Suspicious Login Activity"
      register: result

    - name: Query findings by title from the last 7 days
      splunk.es.splunk_finding_info:
        title: "Suspicious Login Activity"
        earliest: "-7d"
      register: result

    - name: Display findings with matching title
      debug:
        var: result.findings

    - name: Query all findings (from last 24 hours by default)
      splunk.es.splunk_finding_info:
      register: all_findings

    - name: Display all findings
      debug:
        var: all_findings.findings

    - name: Query all findings from the last 7 days
      splunk.es.splunk_finding_info:
        earliest: "-7d"
        latest: "now"
      register: all_findings

    - name: Query all findings from the last 30 days
      splunk.es.splunk_finding_info:
        earliest: "-30d"
      register: all_findings

    - name: Query findings with a limit on results
      splunk.es.splunk_finding_info:
        earliest: "-7d"
        limit: 100
      register: limited_findings

    - name: Query findings from a specific time range (ISO 8601)
      splunk.es.splunk_finding_info:
        earliest: "2026-01-01T00:00:00"
        latest: "2026-01-07T23:59:59"
      register: all_findings

    - name: Filter findings by status using Jinja2
      splunk.es.splunk_finding_info:
        earliest: "-7d"
      register: all_findings

    # Query findings with custom API path (for non-standard environments)
    - name: Query findings with custom API path
      splunk.es.splunk_finding_info:
        earliest: "-7d"
        api_namespace: "{{ es_namespace | default('servicesNS') }}"
        api_user: "{{ es_user | default('nobody') }}"
        api_app: "{{ es_app | default('SplunkEnterpriseSecuritySuite') }}"
      register: custom_findings



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
                    <b>findings</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>List of findings matching the query</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;ref_id&#x27;: &#x27;abc-123-def-456&#x27;, &#x27;title&#x27;: &#x27;Suspicious Login Activity&#x27;, &#x27;description&#x27;: &#x27;Multiple failed login attempts detected&#x27;, &#x27;security_domain&#x27;: &#x27;access&#x27;, &#x27;entity&#x27;: &#x27;testuser&#x27;, &#x27;entity_type&#x27;: &#x27;user&#x27;, &#x27;finding_score&#x27;: 50, &#x27;owner&#x27;: &#x27;admin&#x27;, &#x27;status&#x27;: &#x27;new&#x27;, &#x27;urgency&#x27;: &#x27;high&#x27;, &#x27;disposition&#x27;: &#x27;undetermined&#x27;}]</div>
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
                            <div>Description of the finding</div>
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
                            <div>Disposition of the finding</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>entity</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The risk object (entity) associated with the finding</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>entity_type</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Type of the risk object (user or system)</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>finding_score</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">integer</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Risk score of the finding</div>
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
                            <div>Owner of the finding</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>ref_id</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>The unique reference ID of the finding</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>security_domain</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Security domain of the finding</div>
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
                            <div>Status of the finding</div>
                    <br/>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>title</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>Title of the finding</div>
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
                            <div>Urgency level of the finding</div>
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
