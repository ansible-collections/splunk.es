#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_investigation_info
short_description: Gather information about Splunk Enterprise Security Investigations
description:
  - This module allows for querying information about Splunk Enterprise Security Investigations.
  - Use this module to retrieve investigation configurations without making changes.
  - Query by C(investigation_ref_id) to fetch a specific investigation.
  - Query by C(name) to filter investigations by exact name match.
  - Use C(create_time_min) and C(create_time_max) to control the time range of returned investigations.
version_added: "5.1.0"
options:
  investigation_ref_id:
    description:
      - Reference ID (investigation ID) to query a specific investigation.
      - If specified, returns only the investigation with this ID.
      - Takes precedence over C(name) if both are provided.
    required: false
    type: str
  name:
    description:
      - Name to filter investigations.
      - Returns all investigations with an exact name match.
      - Ignored if C(investigation_ref_id) is provided.
      - The C(create_time_min) and C(create_time_max) time filters still apply when querying by name.
    required: false
    type: str
  create_time_min:
    description:
      - The minimum time during which investigations were created.
      - All investigations returned have a creation time greater than or equal to this value.
      - Accepts relative time (e.g. C(-30m), C(-7d), C(-1w)), epoch time, or ISO 8601 time.
      - If not provided, no minimum time filter is applied.
    required: false
    type: str
  create_time_max:
    description:
      - The maximum time during which investigations were created.
      - All investigations returned have a creation time less than or equal to this value.
      - Accepts relative time (e.g. C(-30m), C(now)), epoch time, or ISO 8601 time.
      - If not provided, no maximum time filter is applied.
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
      - The app portion of the Splunk API path for the investigations endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: missioncontrol

author: Ron Gershburg (@rgershbu)
"""

EXAMPLES = """
- name: Query specific investigation by ref_id
  splunk.es.splunk_investigation_info:
    investigation_ref_id: "abc-123-def-456"
  register: result

- name: Display the investigation info
  debug:
    var: result.investigations

- name: Query investigations by name
  splunk.es.splunk_investigation_info:
    name: "Security Incident 2026-01"
  register: result

- name: Query investigations by name within a time range
  splunk.es.splunk_investigation_info:
    name: "Security Incident 2026-01"
    create_time_min: "-7d"
    create_time_max: "now"
  register: result

- name: Display investigations with matching name
  debug:
    var: result.investigations

- name: Query all investigations
  splunk.es.splunk_investigation_info:
  register: all_investigations

- name: Display all investigations
  debug:
    var: all_investigations.investigations

- name: Query investigations created in the last 7 days
  splunk.es.splunk_investigation_info:
    create_time_min: "-7d"
  register: recent_investigations

- name: Query investigations created in the last 30 days
  splunk.es.splunk_investigation_info:
    create_time_min: "-30d"
  register: all_investigations

- name: Query investigations from a specific time range (ISO 8601)
  splunk.es.splunk_investigation_info:
    create_time_min: "2026-01-01T00:00:00"
    create_time_max: "2026-01-07T23:59:59"
  register: all_investigations

- name: Query investigations from a specific time range (epoch)
  splunk.es.splunk_investigation_info:
    create_time_min: "1676497520"
    create_time_max: "1676583920"
  register: all_investigations

# Query investigations with custom API path (for non-standard environments)
- name: Query investigations with custom API path
  splunk.es.splunk_investigation_info:
    create_time_min: "-7d"
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('missioncontrol') }}"
  register: custom_investigations
"""

RETURN = """
investigations:
  description: List of investigations matching the query
  returned: always
  type: list
  elements: dict
  contains:
    investigation_ref_id:
      description: The unique reference ID of the investigation
      type: str
    name:
      description: Name of the investigation
      type: str
    description:
      description: Description of the investigation
      type: str
    status:
      description: Status of the investigation
      type: str
    disposition:
      description: Disposition of the investigation
      type: str
    owner:
      description: Owner of the investigation
      type: str
    urgency:
      description: Urgency level of the investigation
      type: str
    sensitivity:
      description: Sensitivity level of the investigation
      type: str
    finding_ids:
      description: List of finding IDs attached to the investigation
      type: list
      elements: str
  sample:
    - investigation_ref_id: "abc-123-def-456"
      name: "Security Incident 2026-01"
      description: "Investigation into suspicious login activity"
      status: "new"
      disposition: "undetermined"
      owner: "admin"
      urgency: "high"
      sensitivity: "amber"
      finding_ids:
        - "A265ED94-AE9E-428C-91D2-64BB956EB7CB@@notable@@62eaebb8c0dd2574fc0b3503a9586cd9"
"""
