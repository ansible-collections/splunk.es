#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
---
module: splunk_finding
short_description: Manage Splunk Enterprise Security findings
description:
  - This module allows for creation and update of Splunk Enterprise Security findings.
  - When C(ref_id) is not provided, a new finding is always created (no idempotency check).
  - When C(ref_id) is provided, the module will check if the finding exists and update it.
  - Update operations use a different API endpoint and only support updating C(owner), C(status), C(urgency), and C(disposition).
  - Tested against Splunk Enterprise Server with Splunk Enterprise Security installed.
version_added: "3.0.0"
options:
  ref_id:
    description:
      - Reference ID (finding ID / event_id) of an existing finding.
      - Format is typically C(uuid@@notable@@time{timestamp}) (e.g., C(2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865)).
      - If provided, the module will verify the finding exists and update it.
      - If not provided, a new finding is created.
      - When updating, only C(owner), C(status), C(urgency), and C(disposition) can be modified.
    type: str
  title:
    description:
      - Title of the finding.
      - Required when creating a new finding (without C(ref_id)).
    type: str
  description:
    description:
      - Description of the finding.
      - Required when creating a new finding.
    type: str
  security_domain:
    description:
      - Security domain for the finding.
      - Required when creating a new finding.
    type: str
    choices:
      - access
      - endpoint
      - network
      - threat
      - identity
      - audit
  entity:
    description:
      - The risk object (entity) associated with the finding.
      - Required when creating a new finding.
    type: str
  entity_type:
    description:
      - The type of the risk object (entity).
      - Required when creating a new finding.
    type: str
    choices:
      - user
      - system
  finding_score:
    description:
      - The risk score for the finding.
      - Required when creating a new finding.
    type: int
  owner:
    description:
      - Owner of the finding.
      - Can be updated on existing findings.
    type: str
  status:
    description:
      - Status of the finding.
      - Can be updated on existing findings.
    type: str
    choices:
      - unassigned
      - new
      - in_progress
      - pending
      - resolved
      - closed
  urgency:
    description:
      - Urgency level of the finding.
      - Can be updated on existing findings.
    type: str
    choices:
      - informational
      - low
      - medium
      - high
      - critical
  disposition:
    description:
      - Disposition of the finding.
      - Can be updated on existing findings.
    type: str
    choices:
      - unassigned
      - true_positive
      - benign_positive
      - false_positive
      - false_positive_inaccurate_data
      - other
      - undetermined
  fields:
    description:
      - List of custom fields to add to the finding.
      - Only used when creating new findings.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the custom field.
        type: str
        required: true
      value:
        description:
          - Value of the custom field.
        type: str
        required: true
  api_namespace:
    description:
      - The namespace portion of the Splunk API path.
      - Override this if your environment uses a different namespace.
    type: str
    default: servicesNS
  api_user:
    description:
      - The user portion of the Splunk API path.
      - Override this if your environment requires a different user context.
    type: str
    default: nobody
  api_app:
    description:
      - The app portion of the Splunk API path for the findings endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: SplunkEnterpriseSecuritySuite

author: Ansible Security Automation Team (@ansible-security) <https://github.com/ansible-security>
"""

EXAMPLES = """
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
"""

RETURN = """
finding:
  description: The finding result containing before/after states.
  returned: always
  type: dict
  contains:
    before:
      description: The finding state before module execution (if existed).
      type: dict
      returned: when finding existed
    after:
      description: The finding state after module execution.
      type: dict
      returned: always
  sample:
    before: null
    after:
      title: "Suspicious Login Activity"
      description: "Multiple failed login attempts detected"
      security_domain: "access"
      entity: "testuser"
      entity_type: "user"
      finding_score: 50
      owner: "admin"
      status: "new"
      urgency: "high"
      disposition: "undetermined"
changed:
  description: Whether any changes were made.
  returned: always
  type: bool
  sample: true
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Finding created/updated successfully"
"""
