{% from 'dcos/_clusters.sls' import clusters %}

include:
  - .genconf

{% for cluster, properties in clusters.items() %}
{{ cluster }} serve.tar.gz:
  cmd.run:
    - name: tar czf ../../serve.tar.gz .
    - cwd: /srv/salt/dcos_cache/{{ cluster }}/genconf/serve/
    - require:
      - cmd: {{ cluster }} genconf
      - file: /srv/salt/dcos_cache/{{ cluster }}/serve.tar.gz

/srv/salt/dcos_cache/{{ cluster }}/serve.tar.gz:
  file.absent

{% endfor %}
