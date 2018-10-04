{% from 'dcos/_clusters.sls' import clusters %}

include:
  - .docker
  - .config
  - .download

{% for cluster, properties in clusters.items() %}
{{ cluster }} genconf:
  cmd.run:
{%- if 'upgrade_from' in properties['installer'] %}
    - name: sh dcos_generate_config.sh --generate-node-upgrade-script {{ properties['installer']['upgrade_from'] }}
{%- else %}
    - name: sh dcos_generate_config.sh --genconf
{%- endif %}
    - cwd: /srv/salt/dcos_cache/{{ cluster }}
    - require:
      - service: docker
      - file: /srv/salt/dcos_cache/{{ cluster }}/genconf/serve
      - file: {{ cluster }} installer download
      - file: {{ cluster }} config.yaml

/srv/salt/dcos_cache/{{ cluster }}/genconf/serve:
  file.absent

{% endfor %}
