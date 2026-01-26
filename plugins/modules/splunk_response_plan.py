#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_response_plan
short_description: Manage Splunk Enterprise Security response plans
description:
  - This module allows for creation, update, and deletion of Splunk Enterprise Security
    response plans (response templates).
  - Response plan names are unique in Splunk ES, so C(name) is used as the identifier.
  - When C(state=present), the module creates or updates the response plan.
  - When C(state=absent), the module deletes the response plan.
  - Phases and tasks are matched by name for updates - existing IDs are preserved
    for items with matching names, and new IDs are generated for new items.
  - B(IMPORTANT - Declarative Approach:) This module uses a declarative approach where the
    playbook defines the complete desired state. Whatever you define is exactly what will
    exist after the module runs. Any existing phases, tasks, or searches that are NOT
    included in your playbook will be REMOVED. This is not a merge operation - it is a
    full replacement of the response plan structure.
  - For example, if a response plan has phases A, B, C and you only define phase A in your
    playbook, phases B and C will be deleted. The same applies to tasks within phases and
    searches within tasks.
version_added: "5.1.0"
options:
  name:
    description:
      - The name of the response plan.
      - This is the unique identifier and is always required.
      - Used to look up existing response plans for update or delete operations.
    type: str
    required: true
  description:
    description:
      - The description of the response plan.
    type: str
  template_status:
    description:
      - The status of the response plan template.
      - Use C(draft) for work-in-progress plans.
      - Use C(published) for plans ready for use.
    type: str
    choices:
      - published
      - draft
    default: draft
  phases:
    description:
      - List of phases in the response plan.
      - Required when C(state=present).
      - Phases are matched by name for updates.
      - B(Note:) Only phases defined here will exist after update. Any existing phases
        not included in this list will be removed from the response plan.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The name of the phase.
          - Used as identifier for matching during updates.
        type: str
        required: true
      tasks:
        description:
          - List of tasks in the phase.
          - Tasks are matched by name within their parent phase for updates.
          - B(Note:) Only tasks defined here will exist in the phase after update.
            Any existing tasks not included in this list will be removed.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - The name of the task.
              - Used as identifier for matching during updates.
            type: str
            required: true
          description:
            description:
              - The description of the task.
            type: str
          is_note_required:
            description:
              - Whether a note is required when completing the task.
            type: bool
            default: false
          owner:
            description:
              - The owner of the task.
              - Use C(admin) for the administrator user.
              - Use C(unassigned) to leave the task unassigned.
            type: str
            default: unassigned
          searches:
            description:
              - List of saved searches to attach to the task.
              - Searches are replaced entirely on update (not merged).
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - The name of the search.
                type: str
                required: true
              description:
                description:
                  - The description of the search.
                type: str
              spl:
                description:
                  - The SPL (Search Processing Language) query.
                type: str
                required: true
  state:
    description:
      - The desired state of the response plan.
      - Use C(present) to create or update the response plan.
      - Use C(absent) to delete the response plan.
    type: str
    choices:
      - present
      - absent
    default: present
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
      - The app portion of the Splunk API path for the response templates endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
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
"""

RETURN = """
response_plan:
  description: The response plan result containing before/after states.
  returned: always
  type: dict
  contains:
    before:
      description: The response plan state before module execution (null if creating).
      type: dict
      returned: when response plan existed
    after:
      description: The response plan state after module execution (null if deleted).
      type: dict
      returned: always
  sample:
    before: null
    after:
      name: "Incident Response Plan"
      description: "Standard incident response procedure"
      template_status: "published"
      phases:
        - name: "Investigation"
          tasks:
            - name: "Initial Triage"
              description: "Perform initial assessment"
              is_note_required: true
              owner: "admin"
              searches:
                - name: "Access Over Time"
                  description: "Check access patterns"
                  spl: "| tstats count from datamodel=Authentication"
changed:
  description: Whether any changes were made.
  returned: always
  type: bool
  sample: true
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Response plan created successfully"
"""
