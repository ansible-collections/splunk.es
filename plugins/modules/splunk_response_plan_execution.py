#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_response_plan_execution
short_description: Apply response plans to investigations and manage tasks
description:
  - This module applies or removes response plans from Splunk Enterprise Security investigations.
  - It also manages task lifecycle within applied response plans (start, end, change owner).
  - The C(response_plan) parameter accepts either a UUID or a name.
  - When C(state=present), the response plan is applied to the investigation.
  - When C(state=absent), the response plan is removed from the investigation.
  - Use the C(tasks) parameter to manage individual task statuses and owners within the applied plan.
version_added: "5.1.0"
options:
  investigation_ref_id:
    description:
      - The investigation UUID to apply or manage response plans.
      - This is the unique identifier of the investigation in Splunk ES.
    type: str
    required: true
  response_plan:
    description:
      - The response plan template to apply or remove.
      - Accepts either a UUID (e.g., "2dc5530d-8bb0-4a4f-9b53-74745bf4ea6a") or a name
        (e.g., "Incident Response Plan").
      - If UUID format is detected, it is used directly as the template ID.
      - If not a UUID, the module performs an API lookup to resolve the name to an ID.
    type: str
    required: true
  state:
    description:
      - The desired state of the response plan on the investigation.
      - Use C(present) to apply the response plan to the investigation or update the tasks.
      - Use C(absent) to remove the response plan from the investigation.
    type: str
    choices:
      - present
      - absent
    default: present
  tasks:
    description:
      - List of tasks to manage within the applied response plan.
      - Each task is identified by phase name and task name.
      - You can set the task status (started/ended) and/or change the owner.
      - Tasks are only managed when C(state=present).
    type: list
    elements: dict
    suboptions:
      phase_name:
        description:
          - The name of the phase containing the task.
          - Used to look up the phase ID within the applied response plan.
        type: str
        required: true
      task_name:
        description:
          - The name of the task to manage.
          - Used to look up the task ID within the phase.
        type: str
        required: true
      status:
        description:
          - The desired status of the task.
          - Use C(started) to mark the task as in progress.
          - Use C(ended) to mark the task as completed.
          - Use C(reopened) to reopen a completed task.
        type: str
        choices:
          - started
          - ended
          - reopened
      owner:
        description:
          - The owner/assignee of the task.
          - Use C(admin) for the administrator user.
          - Use C(unassigned) to remove the current owner or leave unassigned.
        type: str
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
      - The app portion of the Splunk API path.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
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
"""

RETURN = """
response_plan_execution:
  description: The response plan execution result containing before/after states.
  returned: always
  type: dict
  contains:
    before:
      description: The state before module execution.
      type: dict
      returned: always
      contains:
        applied:
          description: Whether the response plan was applied before execution.
          type: bool
        applied_plan_id:
          description: The ID of the applied response plan instance (if applied).
          type: str
        response_plan_id:
          description: The response plan template ID.
          type: str
    after:
      description: The state after module execution.
      type: dict
      returned: always
      contains:
        applied:
          description: Whether the response plan is applied after execution.
          type: bool
        applied_plan_id:
          description: The ID of the applied response plan instance (if applied).
          type: str
        response_plan_id:
          description: The response plan template ID.
          type: str
    tasks_updated:
      description: List of tasks that were updated (when tasks parameter is used).
      type: list
      elements: dict
      returned: when tasks parameter is provided
      contains:
        phase_name:
          description: The phase name containing the task.
          type: str
        task_name:
          description: The task name.
          type: str
        status:
          description: The task status after update.
          type: str
        owner:
          description: The task owner after update.
          type: str
        changed:
          description: Whether this specific task was changed.
          type: bool
  sample:
    before:
      applied: false
    after:
      applied: true
      applied_plan_id: "b9ef7dce-6dcd-4900-b5d5-982fc194554a"
      response_plan_id: "2dc5530d-8bb0-4a4f-9b53-74745bf4ea6a"
    tasks_updated:
      - phase_name: "Investigation Phase"
        task_name: "Initial Triage"
        status: "started"
        owner: "admin"
        changed: true
changed:
  description: Whether any changes were made.
  returned: always
  type: bool
  sample: true
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Response plan applied successfully"
"""
