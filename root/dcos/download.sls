{% from 'dcos/_clusters.sls' import clusters, cache_dir %}

{% for cluster, properties in clusters.items() %}
{{ cluster }} installer download:
  file.managed:
    - name: {{ cache_dir }}/{{ cluster }}/dcos_generate_config.sh
    - source: {{ properties['installer']['url'] }}
    - source_hash: {{ properties['installer']['hash'] }}
    - makedirs: True
    - mode: 755
{% endfor %}
