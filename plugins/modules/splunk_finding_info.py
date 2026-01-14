#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: splunk_finding_info
short_description: Gather information about Splunk Enterprise Security Findings
description:
  - This module allows for querying information about Splunk Enterprise Security Findings.
  - Use this module to retrieve finding configurations without making changes.
  - Query by C(ref_id) to fetch a specific finding. Without C(earliest) and C(latest).
  - Query by C(title) to filter findings by exact title match.
  - Use C(earliest) and C(latest) to control the time range of returned findings.
  - By default, if C(earliest) and C(latest) are not specified, findings from the last 24 hours are returned.
  - This default time (24 hours) range applies when querying by C(title) or all findings (not by C(ref_id)).
  - This module uses the httpapi connection plugin and does not require local Splunk SDK.
version_added: "5.1.0"
options:
  ref_id:
    description:
      - Reference ID (finding ID) to query a specific finding.
      - If specified, returns only the finding with this ID.
      - Takes precedence over C(title) if both are provided.
      - The time is automatically extracted from the ref_id (format uuid@@notable@@time{timestamp}).
      - When querying by ref_id, the C(earliest) and C(latest) parameters are ignored.
    required: false
    type: str
  title:
    description:
      - Title name to filter findings.
      - Returns all findings with an exact title match.
      - Ignored if C(ref_id) is provided.
      - The C(earliest) and C(latest) time filters still apply when querying by title.
    required: false
    type: str
  earliest:
    description:
      - The earliest time for findings to return.
      - All findings returned have a _time greater than or equal to this value.
      - Accepts relative time (e.g. C(-30m), C(-7d), C(-1w)), epoch time, or ISO 8601 time.
      - If not provided, defaults to the last 24 hours (C(-24h)).
      - Ignored when querying by C(ref_id) (time is extracted from ref_id automatically).
      - Applies when querying by C(title) or all findings.
    required: false
    type: str
  latest:
    description:
      - The latest time for findings to return.
      - All findings returned have a _time less than or equal to this value.
      - Accepts relative time (e.g. C(-30m), C(now)), epoch time, or ISO 8601 time.
      - If not provided, defaults to the current time (C(now)).
      - Ignored when querying by C(ref_id) (time is extracted from ref_id automatically).
      - Applies when querying by C(title) or all findings.
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
      - The app portion of the Splunk API path for the findings endpoint.
      - Override this if your environment uses a different app name.
    type: str
    default: SplunkEnterpriseSecuritySuite

author: Ansible Security Automation Team (@ansible-security)
"""

EXAMPLES = """
- name: Query specific finding by ref_id (time extracted automatically from ref_id)
  splunk.es.splunk_finding_info:
    ref_id: "abc-123-def-456@@notable@@time1234567890"
  register: result

- name: Display the finding info
  debug:
    var: result.findings

- name: Query findings by title (from last 24 hours by default)
  splunk.es.splunk_finding_info:
    title: "Suspicious Login Activity"
  register: result

- name: Query findings by title from the last 7 days
  splunk.es.splunk_finding_info:
    title: "Suspicious Login Activity"
    earliest: "-7d"
  register: result

- name: Display findings with matching title
  debug:
    var: result.findings

- name: Query all findings (from last 24 hours by default)
  splunk.es.splunk_finding_info:
  register: all_findings

- name: Display all findings
  debug:
    var: all_findings.findings

- name: Query all findings from the last 7 days
  splunk.es.splunk_finding_info:
    earliest: "-7d"
    latest: "now"
  register: all_findings

- name: Query all findings from the last 30 days
  splunk.es.splunk_finding_info:
    earliest: "-30d"
  register: all_findings

- name: Query findings from a specific time range (ISO 8601)
  splunk.es.splunk_finding_info:
    earliest: "2026-01-01T00:00:00"
    latest: "2026-01-07T23:59:59"
  register: all_findings

- name: Filter findings by status using Jinja2
  splunk.es.splunk_finding_info:
    earliest: "-7d"
  register: all_findings

# Query findings with custom API path (for non-standard environments)
- name: Query findings with custom API path
  splunk.es.splunk_finding_info:
    earliest: "-7d"
    api_namespace: "{{ es_namespace | default('servicesNS') }}"
    api_user: "{{ es_user | default('nobody') }}"
    api_app: "{{ es_app | default('SplunkEnterpriseSecuritySuite') }}"
  register: custom_findings
"""

RETURN = """
findings:
  description: List of findings matching the query
  returned: always
  type: list
  elements: dict
  contains:
    ref_id:
      description: The unique reference ID of the finding
      type: str
    title:
      description: Title of the finding
      type: str
    description:
      description: Description of the finding
      type: str
    security_domain:
      description: Security domain of the finding
      type: str
    entity:
      description: The risk object (entity) associated with the finding
      type: str
    entity_type:
      description: Type of the risk object (user or system)
      type: str
    finding_score:
      description: Risk score of the finding
      type: int
    owner:
      description: Owner of the finding
      type: str
    status:
      description: Status of the finding
      type: str
    urgency:
      description: Urgency level of the finding
      type: str
    disposition:
      description: Disposition of the finding
      type: str
  sample:
    - ref_id: "abc-123-def-456"
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
"""
