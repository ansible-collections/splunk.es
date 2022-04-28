#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://github.com/ansible/ansible/issues/65816
# https://github.com/PyCQA/pylint/issues/214

# Copyright 2022 Red Hat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: data_inputs_networks
short_description: Manage Splunk Data Inputs of type TCP or UDP
description:
  - This module allows for addition or deletion of TCP and UDP Data Inputs in Splunk.
version_added: "2.0.0"
options:
  config:
    description:
      - Manage and preview protocol input data. 
    type: list
    subelement: dict
    suboptions:
      name:
        description:
          - The input port which receives raw data.
        required: True
        type: str
      protocol:
        description:
          - Choose between tcp or udp
        required: True
        choices:
          - 'tcp'
          - 'udp'
        type: str
      connection_host:
        description:
          - Set the host for the remote server that is sending data.
          - C(ip) sets the host to the IP address of the remote server sending data.
          - C(dns) sets the host to the reverse DNS entry for the IP address of the remote server sending data.
          - C(none) leaves the host as specified in inputs.conf, which is typically the Splunk system hostname.
        default: "ip"
        required: False
        type: str
        choices:
          - "ip"
          - "dns"
          - "none"
      datatype:
        description: >
          Forwarders can transmit three types of data: raw, unparsed, or parsed.
          C(cooked) data refers to parsed and unparsed formats.
        choices:
          - "cooked"
          - "raw"
          - "splunktcptoken"
          - "ssl"
        default: "raw"
        required: False
        type: str
      disabled:
        description:
          - Indicates whether the input is disabled.
        type: bool
      host:
        description:
          - Host from which the indexer gets data.
        required: False
        type: str
      index:
        description:
          - default Index to store generated events.
        type: str
      no_appending_timestamp:
        description:
          - If set to true, prevents Splunk software from prepending a timestamp and hostname to incoming events. 
          - Only for UDP data input configuration.
        type: bool
      no_priority_stripping:
        description:
          - If set to true, Splunk software does not remove the priority field from incoming syslog events. 
          - Only for UDP data input configuration.
        type: bool
      queue:
        description:
          - Specifies where the input processor should deposit the events it reads. Defaults to parsingQueue.
          - Set queue to parsingQueue to apply props.conf and other parsing rules to your data. For more
            information about props.conf and rules for timestamping and linebreaking, refer to props.conf and
            the online documentation at "Monitor files and directories with inputs.conf"
          - Set queue to indexQueue to send your data directly into the index.
        choices:
          - "parsingQueue"
          - "indexQueue"
        type: str
        required: False
        default: "parsingQueue"
      raw_tcp_done_timeout:
        description:
          - Specifies in seconds the timeout value for adding a Done-key.
          - If a connection over the port specified by name remains idle after receiving data for specified
            number of seconds, it adds a Done-key. This implies the last event is completely received.
          - Only for TCP raw input configuration.
        default: 10
        type: int
        required: False
      restrict_to_host:
        description:
          - Allows for restricting this input to only accept data from the host specified here.
        required: False
        type: str
      ssl:
        description:
          - Enable or disble ssl for the data stream
        required: False
        type: bool
      source:
        description:
          - Sets the source key/field for events from this input. Defaults to the input file path.
          - >
            Sets the source key initial value. The key is used during parsing/indexing, in particular to set
            the source field during indexing. It is also the source field used at search time. As a convenience,
            the chosen string is prepended with 'source::'.
          - >
            Note: Overriding the source key is generally not recommended. Typically, the input layer provides a
            more accurate string to aid in problem analysis and investigation, accurately recording the file from
            which the data was retrieved. Consider use of source types, tagging, and search wildcards before
            overriding this value.
        type: str
      sourcetype:
        description:
          - Set the source type for events from this input.
          - '"sourcetype=" is automatically prepended to <string>.'
          - Defaults to audittrail (if signedaudit=True) or fschange (if signedaudit=False).
        type: str
      token:
        description:
          - Token value to use for SplunkTcpToken. If unspecified, a token is generated automatically. 
        type: str
      password:
        description:
          - Server certificate password, if any.
          - Only for TCP SSL configuration.
        type: str
      require_client_cert:
        description:
          - Determines whether a client must authenticate. 
          - Only for TCP SSL configuration.
        type: str
      root_ca:
        description:
          - Certificate authority list (root file).
          - Only for TCP SSL configuration.
        type: str
      server_cert:
        description:
          - Full path to the server certificate.
          - Only for TCP SSL configuration. 
        type: str
      cipher_suite:
        description:
          - Specifies list of acceptable ciphers to use in ssl.
          - Only obtained for TCP SSL configuration present on device.
        type: str

  running_config:
    description:
    - The module, by default, will connect to the remote device and retrieve the current
      running-config to use as a base for comparing against the contents of source.
      There are times when it is not desirable to have the task get the current running-config
      for every task in a playbook.  The I(running_config) argument allows the implementer
      to pass in the configuration to use as the base config for comparison. This
      value of this option should be the output received from device by executing
      command.
    type: str
  state:
    description:
    - The state the configuration should be left in
    type: str
    choices:
    - merged
    - replaced
    - deleted
    - gathered
    default: merged

author: Pranav Bhatt (@pranav-bhatt)
"""

EXAMPLES = """
# _________________________________________________________________
# Using gathered

- name: Gathering information about TCP Cooked inputs using splunk.es.data_inputs_networks
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: cooked
    state: gathered
# 
# Output:
#
# "changed": false,
# "gathered": [
#     {
#         "connection_host": "ip",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "8101"
#     },
#     {
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "9997"
#     },
#     {
#         "connection_host": "ip",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8101",
#         "restrict_to_host": "default"
#     }
# ]
#
# ------------------------------
- name: Gathering information about TCP Cooked inputs using splunk.es.data_inputs_networks
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: cooked
        name: 9997
    state: gathered
#
# Output:
#
# "changed": false,
# "gathered": [
#     {
#         "datatype": "cooked",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "name": "9997",
#         "protocol": "tcp"
#     }
# ]
#
# ------------------------------
- name: Gathering information about TCP raw inputs using splunk.es.data_inputs_networks
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: raw
    state: gathered
#
# "changed": false,
# "gathered": [
#     {
#         "connection_host": "ip",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "8099",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 10
#     },
#     {
#         "connection_host": "ip",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8100",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 10,
#         "restrict_to_host": "default",
#         "source": "test_source",
#         "sourcetype": "test_source_type"
#     }
# ]
#
# ------------------------------
- name: Gathering information about TCP raw inputs using splunk.es.data_inputs_networks
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: raw
        name: 8099
    state: gathered
#
# Output:
#
# "changed": false,
# "gathered": [
#     {
#         "connection_host": "ip",
#         "datatype": "raw",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "8099",
#         "protocol": "tcp",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 10
#     }
# ]
#
# ------------------------------
- name: Gathering information about TCP SSL configuration using splunk.es.data_inputs_networks
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: ssl
    state: gathered
# 
# Output:
#
# "changed": false,
# "gathered": [
#     {
#         "cipher_suite": <cipher-suites>,
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "test_host"
#     }
# ]
# 
# ------------------------------
- name: Gathering information about TCP SplunkTcpTokens using splunk.es.data_inputs_networks
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: splunktcptoken
    state: gathered
#
# Output:
#
# "changed": false,
# "gathered": [
#     {
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "splunktcptoken://test_token1",
#         "token": <token1>
#     },
#     {
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "splunktcptoken://test_token2",
#         "token": <token2>
#     }
# ]
# _________________________________________________________________
# Using merged
#
- name: tcp raw
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: raw
        name: 8100
        connection_host: ip
        disabled: True
        raw_tcp_done_timeout: 9
        restrict_to_host: default
        queue: parsingQueue
        source: test_source
        sourcetype: test_source_type
    state: merged
#
# Output:
#
# "after": [
#     {
#         "connection_host": "ip",
#         "datatype": "raw",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8100",
#         "protocol": "tcp",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 9,
#         "restrict_to_host": "default",
#         "source": "test_source",
#         "sourcetype": "test_source_type"
#     }
# ],
# "before": [
#     {
#         "connection_host": "ip",
#         "datatype": "raw",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8100",
#         "protocol": "tcp",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 10,
#         "restrict_to_host": "default",
#         "source": "test_source",
#         "sourcetype": "test_source_type"
#     }
# ]
#
- name: tcp cooked
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: cooked
        name: 8101
        connection_host: ip
        disabled: False
        restrict_to_host: default
    state: merged
#
# Output:
#
# "after": [
#     {
#         "connection_host": "ip",
#         "datatype": "cooked",
#         "disabled": false,
#         "host": "$decideOnStartup",
#         "name": "default:8101",
#         "protocol": "tcp",
#         "restrict_to_host": "default"
#     }
# ],
# "before": [
#     {
#         "connection_host": "ip",
#         "datatype": "cooked",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "name": "default:8101",
#         "protocol": "tcp",
#         "restrict_to_host": "default"
#     }
# ],
# "changed": true
#
- name: splunktcptoken
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: splunktcptoken
        name: test_token
    state: merged
#
# Output:
#
# "after": [
#     {
#         "datatype": "splunktcptoken",
#         "name": "splunktcptoken://test_token",
#         "protocol": "tcp",
#         "token": <token>
#     }
# ],
# "before": [],
# "changed": true
#
- name: ssl
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: ssl
        name: test_host
        root_ca: {root CA directory}
        server_cert: {server cretificate directory}
    state: merged
#
# Output:
#
# "after": [
#     {
#         "cipher_suite": <cipher suite>,
#         "datatype": "ssl",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "test_host",
#         "protocol": "tcp"
#     }
# ],
# "before": [],
# "changed": false
#
# _________________________________________________________________
# Using deleted
#
- name: tcp raw
  splunk.es.data_inputs_networks:
    config:
      - protocol: tcp
        datatype: raw
        name: default:8100
    state: deleted
#
# Output:
#
# "after": [],
# "before": [
#     {
#         "connection_host": "ip",
#         "datatype": "raw",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8100",
#         "protocol": "tcp",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 9,
#         "restrict_to_host": "default",
#         "source": "test_source",
#         "sourcetype": "test_source_type"
#     }
# ],
# "changed": true
#
# _________________________________________________________________
# Using replaced
#
# Output:
#
# "after": [
#     {
#         "connection_host": "ip",
#         "datatype": "raw",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8100",
#         "protocol": "tcp",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 9,
#         "restrict_to_host": "default",
#         "source": "test_source",
#         "sourcetype": "test_source_type"
#     }
# ],
# "before": [
#     {
#         "connection_host": "ip",
#         "datatype": "raw",
#         "disabled": true,
#         "host": "$decideOnStartup",
#         "index": "default",
#         "name": "default:8100",
#         "protocol": "tcp",
#         "queue": "parsingQueue",
#         "raw_tcp_done_timeout": 10,
#         "restrict_to_host": "default",
#         "source": "test_source",
#         "sourcetype": "test_source_type"
#     }
# ],
# "changed": true
#
"""
RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when state is I(merged), I(replaced), I(deleted)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when state is I(gathered)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
"""
