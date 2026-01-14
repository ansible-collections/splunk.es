.. _splunk.es.splunk_correlation_search_info_module:


****************************************
splunk.es.splunk_correlation_search_info
****************************************

**Gather information about Splunk Enterprise Security Correlation Searches**


Version added: 3.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for querying information about Splunk Enterprise Security Correlation Searches.
- Use this module to retrieve correlation search configurations without making changes.
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
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name of correlation search to query.</div>
                        <div>If not specified, returns all correlation searches.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: Query specific correlation search by name
      splunk.es.splunk_correlation_search_info:
        name: "Brute Force Access Behavior Detected"
      register: result

    - name: Display the correlation search info
      debug:
        var: result.correlation_searches

    - name: Query all correlation searches
      splunk.es.splunk_correlation_search_info:
      register: all_searches

    - name: Display all correlation searches
      debug:
        var: all_searches.correlation_searches

    - name: Find searches containing specific keyword
      splunk.es.splunk_correlation_search_info:
      register: all_searches

    - set_fact:
        filtered_searches: "{{ all_searches.correlation_searches |
                              selectattr('name', 'search', 'Brute Force') | list }}"



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
                    <b>correlation_searches</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>Information about correlation search(es)</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;entry&#x27;: [{&#x27;name&#x27;: &#x27;Brute Force Access Behavior Detected&#x27;, &#x27;content&#x27;: {&#x27;description&#x27;: &#x27;Detects brute force behavior&#x27;, &#x27;search&#x27;: &#x27;| from datamodel:Authentication&#x27;, &#x27;disabled&#x27;: 0}}]}</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder">&nbsp;</td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>entry</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td></td>
                <td>
                            <div>List of correlation search entries</div>
                    <br/>
                </td>
            </tr>

    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Ansible Security Automation Team (@ansible-security)
