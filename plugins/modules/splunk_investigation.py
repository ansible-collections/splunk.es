#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
---
module: splunk_investigation
short_description: Manage Splunk Enterprise Security investigations
description:
  - This module allows for creation and update of Splunk Enterprise Security investigations.
  - When C(investigation_ref_id) is not provided, a new investigation is created.
  - When C(investigation_ref_id) is provided, the module will update the existing investigation.
  - Update operations can modify all fields except C(name).
version_added: "5.1.0"
options:
  investigation_ref_id:
    description:
      - Reference ID of an existing investigation.
      - If provided, the module will update the existing investigation.
      - If not provided, a new investigation is created.
      - When updating, all fields except C(name) can be modified.
    type: str
  name:
    description:
      - The name of the investigation.
      - Required when creating a new investigation (without C(investigation_ref_id)).
      - Cannot be updated after creation.
      - Note that names are not unique - multiple investigations can have the same name.
    type: str
  description:
    description:
      - The description of the investigation.
    type: str
  status:
    description:
      - The status of the investigation.
      - Can be updated on existing investigations.
    type: str
    choices:
      - unassigned
      - new
      - in_progress
      - pending
      - resolved
      - closed
  disposition:
    description:
      - The disposition of the investigation.
      - Can be updated on existing investigations.
    type: str
    choices:
      - unassigned
      - true_positive
      - benign_positive
      - false_positive
      - false_positive_inaccurate_data
      - other
      - undetermined
  owner:
    description:
      - The owner of the investigation.
      - Use C(admin) for the administrator user.
      - Use C(unassigned) to leave the investigation unassigned.
      - Can be updated on existing investigations.
    type: str
  urgency:
    description:
      - The urgency of the investigation.
      - Can be updated on existing investigations.
    type: str
    choices:
      - informational
      - low
      - medium
      - high
      - critical
      - unknown
  sensitivity:
    description:
      - The sensitivity of the investigation.
      - Can be updated on existing investigations.
    type: str
    choices:
      - white
      - green
      - amber
      - red
      - unassigned
  finding_ids:
    description:
      - List of finding IDs (event_ids) to attach to the investigation.
      - When updating, findings are added to the investigation via a separate API call.
      - Finding IDs can only be added, removal is not supported.
    type: list
    elements: str
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
      - The app portion of the Splunk API path for the investigations endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
# Create a new investigation
- name: Create an investigation
  splunk.es.splunk_investigation:
    name: "Security Incident 2026-01"
    description: "Investigation into suspicious login activity"
    status: new
    owner: admin
    urgency: high
    sensitivity: amber
    disposition: undetermined

# Create an investigation with findings attached
- name: Create investigation with findings
  splunk.es.splunk_investigation:
    name: "Malware Investigation"
    description: "Investigation into potential malware detection"
    status: new
    owner: admin
    urgency: critical
    sensitivity: red
    finding_ids:
      - "A265ED94-AE9E-428C-91D2-64BB956EB7CB@@notable@@62eaebb8c0dd2574fc0b3503a9586cd9"

# Update an existing investigation status
- name: Update investigation status
  splunk.es.splunk_investigation:
    investigation_ref_id: "inv-12345-abcde"
    status: in_progress
    owner: analyst1

# Update investigation disposition
- name: Close investigation as resolved
  splunk.es.splunk_investigation:
    investigation_ref_id: "inv-12345-abcde"
    status: resolved
    disposition: true_positive
    urgency: low

# Add findings to an existing investigation
- name: Add findings to investigation
  splunk.es.splunk_investigation:
    investigation_ref_id: "inv-12345-abcde"
    finding_ids:
      - "B376FE05-BF9F-539D-A2E3-75CC067FC8DC@@notable@@73fbccc9d1ee3685gd1c4614b0697de0"
"""

RETURN = """
investigation:
  description: The investigation result containing before/after states.
  returned: always
  type: dict
  contains:
    before:
      description: The investigation state before module execution (if existed).
      type: dict
      returned: when investigation existed
    after:
      description: The investigation state after module execution.
      type: dict
      returned: always
  sample:
    before: null
    after:
      name: "Security Incident 2026-01"
      description: "Investigation into suspicious login activity"
      status: "new"
      owner: "admin"
      urgency: "high"
      sensitivity: "amber"
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
  sample: "Investigation created/updated successfully"
"""
