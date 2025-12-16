===================================================
Splunk Enterprise Security Collection Release Notes
===================================================

.. contents:: Topics

v5.0.0
======

Release Summary
---------------

Starting from this release, the minimum required version of `ansible-core` this collection requires is `2.17.0`. Previously deprecated legacy modules have been removed; use the corresponding resource modules instead.

Major Changes
-------------

- Bumped the minimum supported Ansible version to ``>=2.17.0`` (Ansible 2.15/2.16 are EoL).
- Bumped the minimum supported Python version to ``>=3.10`` (Python 3.9 is EoL).

Breaking Changes / Porting Guide
--------------------------------

- Removed deprecated modules that were scheduled for removal on 2024-09-01
- correlation_search - Use splunk_correlation_searches instead
- data_input_monitor - Use splunk_data_inputs_monitor instead
- data_input_network - Use splunk_data_inputs_network instead
- adaptive_response_notable_event - Use splunk_adaptive_response_notable_events instead

Removed Features (previously deprecated)
----------------------------------------

- correlation_search module has been removed. Use splunk_correlation_searches resource module instead.
- data_input_monitor module has been removed. Use splunk_data_inputs_monitor resource module instead.
- data_input_network module has been removed. Use splunk_data_inputs_network resource module instead.
- adaptive_response_notable_event module has been removed. Use splunk_adaptive_response_notable_events resource module instead.
- correlation_search_info module has been removed. Use splunk_correlation_search_info resource module instead.

Minor Changes
-------------

- Removed legacy module support code from module_utils/splunk.py as all modules now use the modern action plugin architecture.
- Simplified SplunkRequest class initialization by removing unused parameters (module, headers, override).
- Removed parse_splunk_args function that was only used by deprecated legacy modules.
- Updated SplunkRequest to require action_module and connection parameters, improving code clarity and maintainability.

Bugfixes
--------

- splunk_correlation_searches - Fixed duplicate entries in gathered state caused by redundant loop in action plugin.
- Fixed ansible-lint errors by adding missing task names in integration tests.
- Fixed deprecated module alternatives to use fully qualified collection names (FQCN).

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
