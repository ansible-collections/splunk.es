===================================================
Splunk Enterprise Security Collection Release Notes
===================================================

.. contents:: Topics

v6.0.0
======

Release Summary
---------------

This major release removes the ``ansible.netcommon`` collection dependency, bundling required utility functions locally and inheriting the httpapi plugin directly from ansible-core's ``HttpApiBase``. It also fixes a finding query time-boundary precision issue and adds an ansible-core version matrix to the integration test workflow.

Major Changes
-------------

- Remove dependency on the ``ansible.netcommon`` collection. Utility functions (``remove_empties``, ``dict_diff``, ``dict_merge``) are now bundled locally, and the httpapi plugin inherits directly from ansible-core's ``HttpApiBase``.

Minor Changes
-------------

- ci - Add ansible-core version matrix (stable-2.16 through stable-2.21) to the network integration test workflow, aligning with the ITSI pattern. Lower minimum supported ansible-core version to 2.16.0.

Bugfixes
--------

- splunk_finding, splunk_finding_info - Fix query by ref_id failing to find findings due to sub-second time precision mismatch. The ``earliest`` time extracted from the ref_id now includes a 1-second buffer to ensure the finding falls within the search window.

v5.1.0
======

Release Summary
---------------

Release summary for v5.1.0"

Minor Changes
-------------

- Added ``limit`` parameter to splunk_finding_info, splunk_investigation_info, and splunk_response_plan_info modules to control the maximum number of results returned.
- Added splunk_finding module to manage (create/update) Splunk Enterprise Security findings.
- Added splunk_finding_info module to query information about Splunk Enterprise Security findings.
- Added splunk_investigation module to manage (create/update) Splunk Enterprise Security investigations.
- Added splunk_investigation_info module to query information about Splunk Enterprise Security investigations.
- Added splunk_investigation_type module to manage (create/update) Splunk Enterprise Security investigation types (incident types).
- Added splunk_investigation_type_info module to query information about Splunk Enterprise Security investigation types.
- Added splunk_response_plan module to manage (create/update/delete) Splunk Enterprise Security response plans.
- Added splunk_response_plan_execution module to apply/remove response plans to investigations and manage task statuses.
- Added splunk_response_plan_execution_info module to query applied response plans and task statuses on investigations.
- Added splunk_response_plan_info module to query information about Splunk Enterprise Security response plans.
- Modernized Python code across the collection by removing Python 2 compatibility patterns (``from __future__ import`` and ``__metaclass__ = type``), updating to modern ``super()`` syntax, converting ``.format()`` calls to f-strings, and consolidating duplicated ``_check_argspec()`` methods into the shared ``check_argspec()`` helper.
- splunk_notes - new module to manage notes for findings, investigations, and response plan tasks.
- splunk_notes_info - new module to query notes from findings, investigations, and response plan tasks.

Bugfixes
--------

- Implement check mode support in action plugins. Previously, check mode was declared as supported but API calls were still being made. Now all state-changing operations (merged, replaced, deleted) properly skip API calls when running in check mode.

New Modules
-----------

- splunk_finding - Manage Splunk Enterprise Security findings
- splunk_finding_info - Gather information about Splunk Enterprise Security Findings
- splunk_investigation - Manage Splunk Enterprise Security investigations
- splunk_investigation_info - Gather information about Splunk Enterprise Security Investigations
- splunk_investigation_type - Manage Splunk Enterprise Security investigation types
- splunk_investigation_type_info - Gather information about Splunk Enterprise Security investigation types
- splunk_notes - Manage notes for findings, investigations, and response plan tasks
- splunk_notes_info - Gather information about notes in Splunk Enterprise Security
- splunk_response_plan - Manage Splunk Enterprise Security response plans
- splunk_response_plan_execution - Apply response plans to investigations and manage tasks
- splunk_response_plan_execution_info - Gather information about applied response plans on an investigation
- splunk_response_plan_info - Gather information about Splunk Enterprise Security response plans

v5.0.0
======

Release Summary
---------------

Starting from this release, the minimum `ansible-core` version this collection requires is `2.17.0`. The last version known to be compatible with `ansible-core` versions below `2.17` is v4.0.0.Bumped the minimum supported Python version to ``>=3.10`` (Python 3.9 is EoL).

Major Changes
-------------

- Bumped the minimum supported Ansible version to ``>=2.17.0`` (Ansible 2.15/2.16 are EoL).

Minor Changes
-------------

- Removed legacy module support code from module_utils/splunk.py as all modules now use the modern action plugin architecture.
- Removed parse_splunk_args function that was only used by deprecated legacy modules.
- Simplified SplunkRequest class initialization by removing unused parameters (module, headers, override).
- Updated SplunkRequest to require action_module and connection parameters, improving code clarity and maintainability.

Breaking Changes / Porting Guide
--------------------------------

- Removed deprecated modules that were scheduled for removal on 2024-09-01
- adaptive_response_notable_event - Use splunk.es.splunk_adaptive_response_notable_events instead
- correlation_search - Use splunk.es.splunk_correlation_searches instead
- data_input_monitor - Use splunk.es.splunk_data_inputs_monitor instead
- data_input_network - Use splunk.es.splunk_data_inputs_network instead

Removed Features (previously deprecated)
----------------------------------------

- adaptive_response_notable_event module has been removed. Use splunk.es.splunk_adaptive_response_notable_events resource module instead.
- correlation_search module has been removed. Use splunk.es.splunk_correlation_searches resource module instead.
- correlation_search_info module has been removed. Use splunk.es.splunk_correlation_search_info instead.
- data_input_monitor module has been removed. Use splunk.es.splunk_data_inputs_monitor resource module instead.
- data_input_network module has been removed. Use splunk.es.splunk_data_inputs_network resource module instead.

Bugfixes
--------

- Added sanity test ignore file for Ansible 2.20 to handle pylint errors in deprecated modules.
- Fixed ansible-lint errors by adding missing task names in integration tests.
- Fixed deprecated module alternatives to use fully qualified collection names (FQCN).
- splunk_correlation_searches - Fixed duplicate entries in gathered state caused by redundant loop in action plugin.

v4.0.0
======

Release Summary
---------------

With this release, the minimum required version of `ansible-core` for this collection is `2.15.0`. The last version known to be compatible with `ansible-core` versions below `2.15` is v3.0.0.

Major Changes
-------------

- Bumping `requires_ansible` to `>=2.15.0`, since previous ansible-core versions are EoL now.

v3.0.0
======

Release Summary
---------------

Starting from this release, the minimum `ansible-core` version this collection requires is `2.14.0`. The last known version compatible with ansible-core<2.14 is `v2.1.2`.

Major Changes
-------------

- Bumping `requires_ansible` to `>=2.14.0`, since previous ansible-core versions are EoL now.

v2.1.2
======

Bugfixes
--------

- Fixed argspec validation for plugins with empty task attributes when run with Ansible 2.9.

v2.1.1
======

Release Summary
---------------

Releasing version 2.1.1, featuring various maintenance updates.

v2.1.0
======

Minor Changes
-------------

- Added adaptive_response_notable_events resource module
- Added correlation_searches resource module
- Added data_inputs_monitors resource module
- Added data_inputs_networks resource module

New Modules
-----------

Ansible Collections
~~~~~~~~~~~~~~~~~~~

splunk.es.plugins.modules
^^^^^^^^^^^^^^^^^^^^^^^^^

- splunk_adaptive_response_notable_events - Manage Adaptive Responses notable events resource module
- splunk_correlation_searches - Splunk Enterprise Security Correlation searches resource module
- splunk_data_inputs_monitor - Splunk Data Inputs of type Monitor resource module
- splunk_data_inputs_network - Manage Splunk Data Inputs of type TCP or UDP resource module

v2.0.0
======

Major Changes
-------------

- Minimum required ansible.netcommon version is 2.5.1.
- Updated base plugin references to ansible.netcommon.

Bugfixes
--------

- Fix ansible test sanity failures and fix flake8 issues.

v1.0.2
======

Release Summary
---------------

Re-releasing 1.0.1 with updated galaxy file.

v1.0.1
======

Release Summary
---------------

Releasing 1.0.1 with updated changelog.

v1.0.0
======

New Modules
-----------

- splunk.es.adaptive_response_notable_event - Manage Splunk Enterprise Security Notable Event Adaptive Responses
- splunk.es.correlation_search - Manage Splunk Enterprise Security Correlation Searches
- splunk.es.correlation_search_info - Manage Splunk Enterprise Security Correlation Searches
- splunk.es.data_input_monitor - Manage Splunk Data Inputs of type Monitor
- splunk.es.data_input_network - Manage Splunk Data Inputs of type TCP or UDP
