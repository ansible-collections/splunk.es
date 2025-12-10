[splunk]
${SPLUNK_HOSTNAME}

[splunk:vars]
ansible_connection=httpapi
ansible_network_os=splunk.es.splunk
ansible_user=${SPLUNK_USERNAME}
ansible_httpapi_pass=${SPLUNK_PASSWORD}
ansible_httpapi_port=8089
ansible_httpapi_use_ssl=yes
ansible_httpapi_validate_certs=False
