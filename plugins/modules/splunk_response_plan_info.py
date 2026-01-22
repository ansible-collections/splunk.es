#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_response_plan_info
short_description: Gather information about Splunk Enterprise Security response plans
description:
  - This module allows for querying information about Splunk Enterprise Security response plans.
  - Use this module to retrieve response plan configurations without making changes.
  - Query by C(name) to filter response plans by exact name match.
  - If C(name) is not specified, returns all response plans.
  - Returns complete response plan structure including all IDs (response plan ID, phase IDs, task IDs).
version_added: "5.1.0"
options:
  name:
    description:
      - Name to filter response plans.
      - Returns the response plan with an exact name match.
      - If not specified, returns all response plans.
    required: false
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
      - The app portion of the Splunk API path for the response templates endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
- name: Query all response plans
  splunk.es.splunk_response_plan_info:
  register: all_plans

- name: Query specific response plan by name
  splunk.es.splunk_response_plan_info:
    name: "Incident Response Plan"
  register: result

- name: Query response plans with custom API path
  splunk.es.splunk_response_plan_info:
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
  register: custom_plans
"""

RETURN = """
response_plans:
  description: List of response plans matching the query
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique ID of the response plan
      type: str
    name:
      description: Name of the response plan
      type: str
    description:
      description: Description of the response plan
      type: str
    template_status:
      description: Status of the response plan template (published or draft)
      type: str
    phases:
      description: List of phases in the response plan
      type: list
      elements: dict
      contains:
        id:
          description: The unique ID of the phase
          type: str
        name:
          description: Name of the phase
          type: str
        tasks:
          description: List of tasks in the phase
          type: list
          elements: dict
          contains:
            id:
              description: The unique ID of the task
              type: str
            name:
              description: Name of the task
              type: str
            description:
              description: Description of the task
              type: str
            is_note_required:
              description: Whether a note is required when completing the task
              type: bool
            owner:
              description: Owner of the task
              type: str
            searches:
              description: List of saved searches attached to the task
              type: list
              elements: dict
              contains:
                name:
                  description: Name of the search
                  type: str
                description:
                  description: Description of the search
                  type: str
                spl:
                  description: The SPL query
                  type: str
  sample:
    - id: "abc123-def456-ghi789"
      name: "Incident Response Plan"
      description: "Standard incident response procedure"
      template_status: "published"
      phases:
        - id: "phase-uuid-001"
          name: "Investigation"
          tasks:
            - id: "task-uuid-001"
              name: "Initial Triage"
              description: "Perform initial assessment"
              is_note_required: true
              owner: "admin"
              searches:
                - name: "Access Over Time"
                  description: "Check access patterns"
                  spl: "| tstats count from datamodel=Authentication"
"""
