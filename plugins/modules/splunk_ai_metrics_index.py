#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
---
module: splunk_ai_metrics_index
short_description: Configure a Splunk index for AI Factory GPU and AI metrics
description:
  - This module creates or updates a Splunk index optimized for ingesting AI Factory
    telemetry including NVIDIA DCGM GPU metrics, NIM inference server metrics, and
    model training telemetry.
  - Supports configuring retention policies, data model acceleration, and metric
    schema definitions for AI workload observability.
  - Tested against Splunk Enterprise Server with Splunk Enterprise Security installed.
version_added: "5.2.0"
options:
  name:
    description:
      - Name of the Splunk index to create or update.
      - Commonly set to C(ai_factory_metrics) or similar.
    type: str
    required: true
  datatype:
    description:
      - The datatype of the index.
      - Set to C(metric) for metrics-based indexes or C(event) for event-based.
    type: str
    choices:
      - metric
      - event
    default: metric
  frozen_time_period_in_secs:
    description:
      - Number of seconds after which indexed data is frozen (archived or deleted).
      - Default is 7776000 (90 days).
    type: int
    default: 7776000
  max_data_size:
    description:
      - Maximum size of a hot bucket in MB.
      - Specify C(auto) to let Splunk manage bucket sizing.
      - Specify C(auto_high_volume) for high-volume GPU metric ingestion.
    type: str
    default: auto_high_volume
  metric_transforms:
    description:
      - List of metric transform definitions for structuring AI Factory telemetry.
      - Each transform maps raw data fields to Splunk metric names and dimensions.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the metric transform (e.g., C(dcgm_gpu_metrics), C(nim_inference_metrics)).
        type: str
        required: true
      metric_name_field:
        description:
          - Field in the raw data that contains the metric name.
        type: str
        default: metric_name
      metric_value_field:
        description:
          - Field in the raw data that contains the metric value.
        type: str
        default: _value
      dimensions:
        description:
          - List of fields to use as metric dimensions (e.g., C(gpu_id), C(hostname), C(model_name)).
        type: list
        elements: str
  state:
    description:
      - Whether the index should exist or not.
    type: str
    choices:
      - present
      - absent
    default: present
  api_namespace:
    description:
      - The namespace portion of the Splunk API path.
    type: str
    default: servicesNS
  api_user:
    description:
      - The user portion of the Splunk API path.
    type: str
    default: nobody

author: Ansible Security Automation Team (@ansible-security)
"""

EXAMPLES = """
# Create a metrics index for DCGM GPU telemetry
- name: Create AI Factory metrics index
  splunk.es.splunk_ai_metrics_index:
    name: ai_factory_metrics
    datatype: metric
    frozen_time_period_in_secs: 7776000
    max_data_size: auto_high_volume
    state: present

# Create an index with metric transforms for GPU and inference metrics
- name: Create AI metrics index with transforms
  splunk.es.splunk_ai_metrics_index:
    name: ai_factory_metrics
    datatype: metric
    metric_transforms:
      - name: dcgm_gpu_metrics
        metric_name_field: metric_name
        metric_value_field: _value
        dimensions:
          - gpu_id
          - hostname
          - gpu_model
          - pci_bus_id
      - name: nim_inference_metrics
        metric_name_field: metric_name
        metric_value_field: _value
        dimensions:
          - model_name
          - endpoint
          - hostname
          - gpu_id
      - name: training_telemetry
        metric_name_field: metric_name
        metric_value_field: _value
        dimensions:
          - job_id
          - framework
          - hostname
          - gpu_id
    state: present

# Remove an AI Factory metrics index
- name: Remove AI Factory metrics index
  splunk.es.splunk_ai_metrics_index:
    name: ai_factory_metrics
    state: absent
"""

RETURN = """
index:
  description: The index configuration after module execution.
  returned: always
  type: dict
  contains:
    before:
      description: The index state before module execution.
      type: dict
      returned: when index existed
    after:
      description: The index state after module execution.
      type: dict
      returned: always
  sample:
    before: null
    after:
      name: "ai_factory_metrics"
      datatype: "metric"
      frozen_time_period_in_secs: 7776000
      max_data_size: "auto_high_volume"
changed:
  description: Whether any changes were made.
  returned: always
  type: bool
  sample: true
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Index created successfully"
"""
