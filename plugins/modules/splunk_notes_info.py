#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = """
---
module: splunk_notes_info
short_description: Gather information about notes in Splunk Enterprise Security
description:
  - This module allows for querying information about notes in Splunk Enterprise Security.
  - Notes can be queried from findings, investigations, or response plan tasks.
  - Use C(target_type) to specify where to query notes from.
  - Query by C(note_id) to fetch a specific note.
  - Use C(limit) to control the maximum number of notes returned.
  - This module is read-only and does not make any changes.
version_added: "5.1.0"
options:
  target_type:
    description:
      - The type of object to query notes from.
      - Use C(finding) to query notes from a security finding.
      - Use C(investigation) to query notes from an investigation.
      - Use C(response_plan_task) to query notes from a task within an applied response plan.
    type: str
    required: true
    choices:
      - finding
      - investigation
      - response_plan_task
  finding_ref_id:
    description:
      - The reference ID of the finding to query notes from.
      - Required when C(target_type=finding).
      - Format is typically C(uuid@@notable@@time{timestamp}).
      - The C(notable_time) query parameter is automatically extracted from this ID.
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
      - The ID of the task to query notes from.
      - Required when C(target_type=response_plan_task).
    type: str
  note_id:
    description:
      - The ID of a specific note to retrieve.
      - If specified, returns only the note with this ID.
      - For C(response_plan_task), this enables direct API lookup.
      - For C(finding) and C(investigation), notes are fetched and filtered by ID.
    type: str
  limit:
    description:
      - Maximum number of notes to return.
      - Defaults to 100 if not specified.
      - Ignored when C(note_id) is provided.
    type: int
    default: 100
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
# Query all notes from a finding
- name: Get all notes from a finding
  splunk.es.splunk_notes_info:
    target_type: finding
    finding_ref_id: "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
  register: finding_notes

- name: Display finding notes
  debug:
    var: finding_notes.notes

# Query all notes from an investigation
- name: Get all notes from an investigation
  splunk.es.splunk_notes_info:
    target_type: investigation
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
  register: investigation_notes

# Query all notes from a response plan task
- name: Get all notes from a response plan task
  splunk.es.splunk_notes_info:
    target_type: response_plan_task
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    response_plan_id: "b9ef7dce-6dcd-4900-b5d5-982fc194554a"
    phase_id: "phase-001"
    task_id: "task-001"
  register: task_notes

# Query a specific note by ID from a finding
- name: Get specific note from a finding
  splunk.es.splunk_notes_info:
    target_type: finding
    finding_ref_id: "2008e99d-af14-4fec-89da-b9b17a81820a@@notable@@time1768225865"
    note_id: "note-abc123"
  register: specific_note

# Query a specific note by ID from a response plan task
- name: Get specific note from a response plan task
  splunk.es.splunk_notes_info:
    target_type: response_plan_task
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    response_plan_id: "b9ef7dce-6dcd-4900-b5d5-982fc194554a"
    phase_id: "phase-001"
    task_id: "task-001"
    note_id: "note-xyz789"
  register: specific_task_note

# Query notes with a custom limit
- name: Get latest 10 notes from an investigation
  splunk.es.splunk_notes_info:
    target_type: investigation
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    limit: 10
  register: limited_notes

# Query notes with custom API configuration
- name: Get notes with custom API path
  splunk.es.splunk_notes_info:
    target_type: investigation
    investigation_ref_id: "590afa9c-23d5-4377-b909-cd2cfa1bc0f1"
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
  register: custom_notes
"""

RETURN = """
notes:
  description: List of notes matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    note_id:
      description: The unique identifier of the note.
      type: str
    content:
      description: The content/body of the note.
      type: str
  sample:
    - note_id: "note-abc123"
      content: "Initial investigation shows suspicious activity from external IP."
    - note_id: "note-def456"
      content: "Escalating to security team for further analysis."
changed:
  description: Whether any changes were made. Always false for info modules.
  returned: always
  type: bool
  sample: false
"""
