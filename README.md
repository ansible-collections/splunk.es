# Splunk Enterprise Security Ansible Collection

## Tech Preview

Using splunk modules are meant to be used with the [`httpapi` connection
plugin](https://docs.ansible.com/ansible/latest/plugins/connection/httpapi.html)
and as such we will set certain attributes in the inventory

Example `inventory.ini`:

NOTE: The passwords should be stored in a secure location or an [Ansible
Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

NOTE: the default port for Splunk's REST API is 8089


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


Example playbook:

License
-------

GPLv3

Author Information
------------------

[Ansible Security Automation Team](https://github.com/ansible-security)
This is the [Ansible
Collection](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)
provided by the [Ansible Security Automation
Team](https://github.com/ansible-security) for automating actions in
[Splunk Enterprise Security SIEM](https://www.splunk.com/en_us/software/enterprise-security.html)

This Collection is meant for distribution via
[Ansible Galaxy](https://galaxy.ansible.com/) as is available for all
[Ansible](https://github.com/ansible/ansible) users to utilize, contribute to,
and provide feedback about.

### Using Splunk Enterprise Security Ansible Collection

An example for using this collection to manage a log source with [Splunk Enterprise Security SIEM](https://www.splunk.com/en_us/software/enterprise-security.html) is as follows.

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

#### Using the modules with Fully Qualified Collection Name (FQCN)

With [Ansible
Collections](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
there are various ways to utilize them either by calling specific Content from
the Collection, such as a module, by it's Fully Qualified Collection Name (FQCN)
as we'll show in this example or by defining a Collection Search Path as the
examples below will display.

I should be noted that the FQCN method is the recommended method but the
shorthand options listed below exist for convenience.

`splunk_with_collections_fqcn_example.yml`
```
---
- name: demo splunk
  hosts: splunk
  gather_facts: False
  tasks:
    - name: test splunk_data_input_monitor
      splunk.es.data_input_monitor:
        name: "/var/log/demo.log"
        state: "present"
        recursive: True
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

#### Define your collection search path at the Play level

Below we specify our collection at the Play level which allows us to use the
splunk modules without specifying the need for the
Ansible Collection Namespace.

`splunk_with_collections_example.yml`
```
---
- name: demo splunk
  hosts: splunk
  gather_facts: False
  collections:
    - splunk.es
  tasks:
    - name: test splunk_data_input_monitor
      data_input_monitor:
        name: "/var/log/demo.log"
        state: "present"
        recursive: True
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

#### Define your collection search path at the Block level

Below we use the [`block`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_blocks.html)
level keyword, we are able to use the splunk modules without the need for the
Ansible Collection Namespace.

`splunk_with_collections_block_example.yml`
```
---
- name: demo splunk
  hosts: splunk
  gather_facts: False
  tasks:
    - name: collection namespace block
      - name: test splunk_data_input_monitor
        data_input_monitor:
          name: "/var/log/demo.log"
          state: "present"
          recursive: True
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

### Collection Content
<!--start collection content-->
## Httpapi plugins
Name | Description
--- | ---
[splunk.es.splunk](https://github.com/ansible-collections/splunk.es/blob/master/docs/splunk.es.splunk.rst)|HttpApi Plugin for Splunk
## Modules
Name | Description
--- | ---
[splunk.es.adaptive_response_notable_event](https://github.com/ansible-collections/splunk.es/blob/master/docs/splunk.es.adaptive_response_notable_event.rst)|Manage Splunk Enterprise Security Notable Event Adaptive Responses
[splunk.es.correlation_search](https://github.com/ansible-collections/splunk.es/blob/master/docs/splunk.es.correlation_search.rst)|Manage Splunk Enterprise Security Correlation Searches
[splunk.es.correlation_search_info](https://github.com/ansible-collections/splunk.es/blob/master/docs/splunk.es.correlation_search_info.rst)|Manage Splunk Enterprise Security Correlation Searches
[splunk.es.data_input_monitor](https://github.com/ansible-collections/splunk.es/blob/master/docs/splunk.es.data_input_monitor.rst)|Manage Splunk Data Inputs of type Monitor
[splunk.es.data_input_network](https://github.com/ansible-collections/splunk.es/blob/master/docs/splunk.es.data_input_network.rst)|Manage Splunk Data Inputs of type TCP or UDP
<!--end collection content-->