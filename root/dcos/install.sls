{%- if grains['dcos']['role'] in ['master', 'slave', 'slave_public'] %}
include:
  - .prepare
  - .transfer

DC/OS installation:
  cmd.run:
    - name: sh dcos_install.sh {{ grains['dcos']['role'] }}
    - cwd: /tmp/dcos-installer
    - require:
      - archive: serve.tar.gz
      - pkg: DC/OS packages
      - service: ntpd
      - service: docker
      - sysctl: net.bridge.bridge-nf-call-iptables
      - sysctl: net.bridge.bridge-nf-call-ip6tables
      - group: nogroup
{%- endif %}
