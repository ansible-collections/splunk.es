#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = """
---
module: splunk_notes
short_description: Manage notes for findings, investigations, and response plan tasks
description:
  - This module allows for creation, update, and deletion of notes in Splunk Enterprise Security.
  - Notes can be created for findings, investigations, or response plan tasks.
  - Use C(target_type) to specify where the note should be attached.
  - When C(state=present) without C(note_id), a new note is created.
  - When C(state=present) with C(note_id), the existing note is updated.
  - When C(state=absent) with C(note_id), the note is deleted.
  - Note creation (without C(note_id)) is B(NOT idempotent). Each call creates a new note,
    even if the content is identical. This is by design, as notes are meant to be additive
    and multiple notes with the same content may be intentional.
  - Note updates (with C(note_id)) B(ARE idempotent). The module compares the existing note's
    content with the desired state and only updates if there are differences.
version_added: "5.1.0"
options:
  target_type:
    description:
      - The type of object to attach the note to.
      - Use C(finding) to attach a note to a security finding.
      - Use C(investigation) to attach a note to an investigation.
      - Use C(response_plan_task) to attach a note to a task within an applied response plan.
    type: str
    required: true
    choices:
      - finding
      - investigation
      - response_plan_task
  state:
    description:
      - The desired state of the note.
      - Use C(present) to create or update a note.
      - Use C(absent) to delete a note (requires C(note_id)).
    type: str
    choices:
      - present
      - absent
    default: present
  note_id:
    description:
      - The ID of an existing note.
      - Required when updating or deleting a note.
      - When C(state=present) and C(note_id) is provided, the note is updated.
      - When C(state=absent), C(note_id) is required to identify the note to delete.
    type: str
  content:
    description:
      - The content/body of the note.
      - Required when C(state=present) (creating or updating a note).
    type: str
  finding_ref_id:
    description:
      - The reference ID of the finding to attach the note to.
      - Required when C(target_type=finding).
      - Format is typically C(uuid@@notable@@time{timestamp}).
    type: str
  investigation_ref_id:
    description:
      - The investigation UUID.
      - Required when C(target_type=investigation) or C(target_type=response_plan_task).
    type: str
  response_plan_id:
    description:
      - The ID of the applied response plan.
      - Required when C(target_type=response_plan_task).
    type: str
  phase_id:
    description:
      - The ID of the phase containing the task.
      - Required when C(target_type=response_plan_task).
    type: str
  task_id:
    description:
      - The ID of the task to attach the note to.
      - Required when C(target_type=response_plan_task).
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
# Create a note on a finding
- name: Add note to a finding
  splunk.es.splunk_notes:
    target_type: finding
    finding_ref_id: "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
    content: "Initial investigation shows suspicious activity from external IP."

# Create a note on an investigation
- name: Add note to an investigation
  splunk.es.splunk_notes:
    target_type: investigation
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    content: "Escalating to security team for further analysis."

# Create a note on a response plan task
- name: Add note to a response plan task
  splunk.es.splunk_notes:
    target_type: response_plan_task
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    response_plan_id: "b9ef7dce-6dcd-4900-b5d5-982fc194554a"
    phase_id: "phase-001"
    task_id: "task-001"
    content: "Completed isolation of affected systems."

# Update an existing note
- name: Update a note on a finding
  splunk.es.splunk_notes:
    target_type: finding
    finding_ref_id: "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
    note_id: "note-abc123"
    content: "Updated analysis: confirmed malicious activity."

# Delete a note from an investigation
- name: Delete a note from an investigation
  splunk.es.splunk_notes:
    target_type: investigation
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    note_id: "note-abc123"
    state: absent

# Create note with custom API configuration
- name: Add note with custom API path
  splunk.es.splunk_notes:
    target_type: investigation
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    content: "Note content here"
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
"""

RETURN = """
note:
  description: The note result containing before/after states.
  returned: always
  type: dict
  contains:
    before:
      description: The note state before module execution (if existed).
      type: dict
      returned: when note existed (update/delete operations)
    after:
      description: The note state after module execution.
      type: dict
      returned: when state is present
      contains:
        note_id:
          description: The unique identifier of the note.
          type: str
        content:
          description: The content of the note.
          type: str
  sample:
    before: null
    after:
      note_id: "note-abc123"
      content: "Investigation shows suspicious activity."
changed:
  description: Whether any changes were made.
  returned: always
  type: bool
  sample: true
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Note created successfully"
"""
