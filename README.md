# Splunk Enterprise Security Ansible Collection

[![Collection Tests](https://github.com/ansible-collections/splunk.es/actions/workflows/tests.yml/badge.svg?event=schedule)](https://github.com/ansible-collections/splunk.es/actions/workflows/tests.yml)
[![Integration Tests](https://github.com/ansible-collections/splunk.es/actions/workflows/network_integration.yml/badge.svg?branch=main&event=schedule)](https://github.com/ansible-collections/splunk.es/actions/workflows/network_integration.yml)
[![SonarCloud Coverage](https://sonarcloud.io/api/project_badges/measure?project=ansible-collections_splunk.es&metric=coverage)](https://sonarcloud.io/project/overview?id=ansible-collections_splunk.es)

This is the [Ansible
Collection](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)
provided by the [Ansible Security Automation
Team](https://github.com/ansible-security) for automating actions in
[Splunk Enterprise Security SIEM](https://www.splunk.com/en_us/software/enterprise-security.html)

This Collection is meant for distribution through
[Ansible Galaxy](https://galaxy.ansible.com/) as is available for all
[Ansible](https://github.com/ansible/ansible) users to utilize, contribute to,
and provide feedback about.

## Description

This collection provides Ansible modules and plugins to automate security operations in [Splunk Enterprise Security](https://www.splunk.com/en_us/software/enterprise-security.html), including management of correlation searches, findings, investigations, response plans, and data inputs.

## Communication

* Join the Ansible forum:
  * [Get Help](https://forum.ansible.com/c/help/6): get help or help others.
  * [Posts tagged with 'security'](https://forum.ansible.com/tag/security): subscribe to participate in collection-related conversations.
  * [Social Spaces](https://forum.ansible.com/c/chat/4): gather and interact with fellow enthusiasts.
  * [News & Announcements](https://forum.ansible.com/c/news/5): track project-wide announcements including social events.

* The Ansible [Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn): used to announce releases and important changes.

For more information about communication, see the [Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

## Support

As a Red Hat Ansible [Certified Content](https://catalog.redhat.com/software/search?target_platforms=Red%20Hat%20Ansible%20Automation%20Platform), this collection is entitled to [support](https://access.redhat.com/support/) through [Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible) (AAP).

If a support case cannot be opened with Red Hat and the collection has been obtained either from [Galaxy](https://galaxy.ansible.com/ui/) or [GitHub](https://github.com/ansible-collections/splunk.es), there is community support available at no charge.

## Requirements

- **Ansible:** `ansible-core >= 2.16.0`
- **Python:** Python 3.10 or later on the controller node
- **Collection dependencies:** [`ansible.utils >= 2.0.0`](https://galaxy.ansible.com/ui/repo/published/ansible/utils/) (installed automatically by `ansible-galaxy`)
- **Connection:** The collection communicates with Splunk ES via its REST API using the [`httpapi` connection plugin](https://docs.ansible.com/ansible/latest/plugins/connection/httpapi.html). The managed node must have the Splunk REST API reachable on port 8089 (or the configured `ansible_httpapi_port`).
- **Splunk Enterprise Security:** A running Splunk Enterprise Security instance is required for integration tests and production use.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against the following Ansible versions: **>=2.16.0**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Collection Content

<!--start collection content-->
### Httpapi plugins
Name | Description
--- | ---
[splunk.es.splunk](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_httpapi.rst)|HttpApi Plugin for Splunk

### Modules
Name | Description
--- | ---
[splunk.es.splunk_adaptive_response_notable_events](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_adaptive_response_notable_events_module.rst)|Manage Adaptive Responses notable events resource module
[splunk.es.splunk_correlation_search_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_correlation_search_info_module.rst)|Gather information about Splunk Enterprise Security Correlation Searches
[splunk.es.splunk_correlation_searches](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_correlation_searches_module.rst)|Splunk Enterprise Security Correlation searches resource module
[splunk.es.splunk_data_inputs_monitor](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_data_inputs_monitor_module.rst)|Splunk Data Inputs of type Monitor resource module
[splunk.es.splunk_data_inputs_network](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_data_inputs_network_module.rst)|Manage Splunk Data Inputs of type TCP or UDP resource module
[splunk.es.splunk_finding](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_finding_module.rst)|Manage Splunk Enterprise Security findings
[splunk.es.splunk_finding_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_finding_info_module.rst)|Gather information about Splunk Enterprise Security Findings
[splunk.es.splunk_investigation](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_investigation_module.rst)|Manage Splunk Enterprise Security investigations
[splunk.es.splunk_investigation_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_investigation_info_module.rst)|Gather information about Splunk Enterprise Security Investigations
[splunk.es.splunk_investigation_type](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_investigation_type_module.rst)|Manage Splunk Enterprise Security investigation types
[splunk.es.splunk_investigation_type_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_investigation_type_info_module.rst)|Gather information about Splunk Enterprise Security investigation types
[splunk.es.splunk_notes](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_notes_module.rst)|Manage notes for findings, investigations, and response plan tasks
[splunk.es.splunk_notes_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_notes_info_module.rst)|Gather information about notes in Splunk Enterprise Security
[splunk.es.splunk_response_plan](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_response_plan_module.rst)|Manage Splunk Enterprise Security response plans
[splunk.es.splunk_response_plan_execution](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_response_plan_execution_module.rst)|Apply response plans to investigations and manage tasks
[splunk.es.splunk_response_plan_execution_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_response_plan_execution_info_module.rst)|Gather information about applied response plans on an investigation
[splunk.es.splunk_response_plan_info](https://github.com/ansible-collections/splunk.es/blob/main/docs/splunk.es.splunk_response_plan_info_module.rst)|Gather information about Splunk Enterprise Security response plans

<!--end collection content-->

### Supported connections

Use splunk modules with the [`httpapi` connection
plugin](https://docs.ansible.com/ansible/latest/plugins/connection/httpapi.html).
Set certain attributes in the inventory as follows:

Example `inventory.ini`:

**NOTE:** The passwords should be stored in a secure location or an [Ansible
Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

**NOTE:** the default port for Splunk's REST API is 8089

    [splunk]
    splunk.example.com

    [splunk:vars]
    ansible_network_os=splunk.es.splunk
    ansible_user=admin
    ansible_httpapi_pass=my_super_secret_admin_password
    ansible_httpapi_port=8089
    ansible_httpapi_use_ssl=yes
    ansible_httpapi_validate_certs=True
    ansible_connection=httpapi

## Installation

You can install the splunk collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install splunk.es

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: splunk.es
```

## Use Cases

### 1. Automate correlation search lifecycle management

Deploy, update, and retire Splunk ES correlation searches as part of a detection-as-code workflow. Store search definitions in version control and let Ansible enforce the desired state across environments:

```yaml
- name: Ensure threat-hunting correlation search is present
  splunk.es.splunk_correlation_searches:
    config:
      - name: Detect Lateral Movement via SMB
        search: 'index=wineventlog EventCode=4624 LogonType=3 | stats count by src_ip, dest_ip'
        description: Detects lateral movement attempts over SMB
        scheduling:
          schedule: "0 * * * *"
          cron_schedule: "0 * * * *"
    state: merged
```

### 2. Manage investigation workflows programmatically

Open, update, and close security investigations from an Ansible playbook, enabling integration with external ticketing or SOAR systems:

```yaml
- name: Open investigation for confirmed incident
  splunk.es.splunk_investigation:
    config:
      - name: "Ransomware outbreak — host {{ inventory_hostname }}"
        status: In Progress
        assignee: soc-analyst
        sensitivity: red
    state: merged
  register: investigation

- name: Attach response plan to investigation
  splunk.es.splunk_response_plan_execution:
    config:
      - investigation_id: "{{ investigation.investigation_id }}"
        response_plan_name: Ransomware Containment
    state: merged
```

### 3. Enforce data input configuration at scale

Ensure all Splunk forwarders and heavy forwarders have the correct monitored log paths and network inputs configured, replacing manual UI changes with an idempotent playbook:

```yaml
- name: Ensure syslog UDP input is configured
  splunk.es.splunk_data_inputs_network:
    config:
      - name: "514"
        protocol: udp
        sourcetype: syslog
        index: main
    state: merged
```

## Using this collection

**NOTE**: For Ansible 2.9, you may not see deprecation warnings when you run your playbooks with this collection. Use this documentation to track when a module is deprecated.

An example of using this collection to manage a log source with [Splunk Enterprise Security SIEM](https://www.splunk.com/en_us/software/enterprise-security.html) is as follows.

`inventory.ini` (Note the password should be managed by a [Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for a production environment.

```
[splunk]
splunk.example.com

[splunk:vars]
ansible_network_os=splunk.es.splunk
ansible_user=admin
ansible_httpapi_pass=my_super_secret_admin_password
ansible_httpapi_port=8089
ansible_httpapi_use_ssl=yes
ansible_httpapi_validate_certs=True
ansible_connection=httpapi
```

### Using the modules with Fully Qualified Collection Name (FQCN)

With [Ansible
Collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
there are various ways to utilize them either by calling specific Content from
the Collection, such as a module, by its Fully Qualified Collection Name (FQCN)
as we'll show in this example or by defining a Collection Search Path as the
examples below will display.

We recommend the FQCN method but the
shorthand options listed below exist for convenience.

`splunk_with_collections_fqcn_example.yml`

```
---
- name: demo splunk
  hosts: splunk
  gather_facts: false
  tasks:
    - name: test splunk_data_input_monitor
      splunk.es.data_input_monitor:
        name: "/var/log/demo.log"
        state: "present"
        recursive: true
    - name: test splunk_data_input_network
      splunk.es.data_input_network:
        name: "9001"
        protocol: "tcp"
        state: "absent"
    - name: test splunk_coorelation_search
      splunk.es.correlation_search:
        name: "Test Demo Coorelation Search From Playbook"
        description: "Test Demo Coorelation Search From Playbook, description."
        search: 'source="/var/log/snort.log"'
        state: "present"
    - name: test splunk_adaptive_response_notable_event
      splunk.es.adaptive_response_notable_event:
        name: "Demo notable event from playbook"
        correlation_search_name: "Test Demo Coorelation Search From Playbook"
        description: "Test Demo notable event from playbook, description."
        state: "present"
        next_steps:
          - ping
          - nslookup
        recommended_actions:
          - script
```

### Define your collection search path at the Play level

Below we specify our collection at the Play level which allows us to use the
splunk modules without specifying the need for the FQCN.

`splunk_with_collections_example.yml`

```
---
- name: demo splunk
  hosts: splunk
  gather_facts: false
  collections:
    - splunk.es
  tasks:
    - name: test splunk_data_input_monitor
      data_input_monitor:
        name: "/var/log/demo.log"
        state: "present"
        recursive: true
    - name: test splunk_data_input_network
      data_input_network:
        name: "9001"
        protocol: "tcp"
        state: "absent"
    - name: test splunk_coorelation_search
      correlation_search:
        name: "Test Demo Coorelation Search From Playbook"
        description: "Test Demo Coorelation Search From Playbook, description."
        search: 'source="/var/log/snort.log"'
        state: "present"
    - name: test splunk_adaptive_response_notable_event
      adaptive_response_notable_event:
        name: "Demo notable event from playbook"
        correlation_search_name: "Test Demo Coorelation Search From Playbook"
        description: "Test Demo notable event from playbook, description."
        state: "present"
        next_steps:
          - ping
          - nslookup
        recommended_actions:
          - script
```

### Define your collection search path at the Block level

Below we use the [`block`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_blocks.html)
level keyword, we are able to use the splunk modules without the need for the
FQCN.

`splunk_with_collections_block_example.yml`

```
---
- name: demo splunk
  hosts: splunk
  gather_facts: false
  tasks:
    - name: collection namespace block
      - name: test splunk_data_input_monitor
        data_input_monitor:
          name: "/var/log/demo.log"
          state: "present"
          recursive: true
      - name: test splunk_data_input_network
        data_input_network:
          name: "9001"
          protocol: "tcp"
          state: "absent"
      - name: test splunk_coorelation_search
        correlation_search:
          name: "Test Demo Coorelation Search From Playbook"
          description: "Test Demo Coorelation Search From Playbook, description."
          search: 'source="/var/log/snort.log"'
          state: "present"
      - name: test splunk_adaptive_response_notable_event
        adaptive_response_notable_event:
          name: "Demo notable event from playbook"
          correlation_search_name: "Test Demo Coorelation Search From Playbook"
          description: "Test Demo notable event from playbook, description."
          state: "present"
          next_steps:
            - ping
            - nslookup
          recommended_actions:
            - script
      collections:
        - splunk.es
```

## Testing

### Test types

| Type | Tool | What is covered |
|---|---|---|
| Sanity | `ansible-test sanity` | Code style, documentation, import correctness |
| Unit | `pytest` via `ansible-test units` | Module utilities, argument validation, API mapping logic |
| Integration | `ansible-test network-integration` | End-to-end module behaviour against a live Splunk ES instance |

### Ansible core versions

Sanity and unit tests run automatically on every pull request and on a nightly schedule against:

- `stable-2.16`
- `stable-2.18`
- `stable-2.20`
- `stable-2.21`

### Splunk Enterprise Security versions

Integration tests run against real Splunk ES instances:

- **Splunk Server 9.4** with Enterprise Security
- **Splunk Server 10.4.1** with Enterprise Security

### Known exceptions and workarounds

- **`ansible.utils` import in sanity tests:** The `import` sanity test runs in an isolated environment without collection dependencies. The `ansible.utils` import in `plugins/module_utils/splunk.py` is wrapped in a `try/except ImportError` block so the sanity test passes cleanly. At runtime `ansible.utils` is always present as a declared `galaxy.yml` dependency.
- **`httpapi` connection required:** All modules communicate exclusively through the Splunk REST API using the `httpapi` connection plugin. SSH-based connections are not supported. Ensure `ansible_connection: httpapi` and `ansible_network_os: splunk.es.splunk` are set in the inventory.
- **Certificate validation:** Splunk installations with self-signed certificates require `ansible_httpapi_validate_certs: false` in the inventory. Use a trusted certificate in production.

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Splunk collection repository](https://github.com/ansible-collections/splunk.es). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

You can also join us on:

- IRC - the `#ansible-security` [irc.libera.chat](https://libera.chat/) channel

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

### Code of Conduct

This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Release notes

Release notes are available on the [GitHub Releases page](https://github.com/ansible-collections/splunk.es/releases).

## Related Information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## License Information

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

## Author Information

[Ansible Security Automation Team](https://github.com/ansible-security)
