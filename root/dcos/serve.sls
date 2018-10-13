{% from 'dcos/_clusters.sls' import clusters, cache_dir %}

include:
  - .genconf

{% for cluster, properties in clusters.items() %}
{{ cluster }} serve.tar.gz:
  cmd.run:
    - name: tar czf ../../serve.tar.gz .
    - cwd: {{ cache_dir }}/{{ cluster }}/genconf/serve/
    - require:
      - cmd: {{ cluster }} genconf
      - file: {{ cache_dir }}/{{ cluster }}/serve.tar.gz

{{ cache_dir }}/{{ cluster }}/serve.tar.gz:
  file.absent

{% endfor %}
