{%- if grains['dcos']['role'] in ['master', 'slave', 'slave_public'] %}
include:
  - .transfer

DC/OS upgrade:
  cmd.run:
    - name: sh upgrade/*/dcos_node_upgrade.sh
    - cwd: /tmp/dcos-installer
    - require:
      - archive: serve.tar.gz
{%- endif %}
