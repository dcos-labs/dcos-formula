{% from 'dcos/_clusters.sls' import clusters %}

{% for cluster, properties in clusters.items() %}
{{ cluster }} config.yaml:
  file.managed:
    - name: /srv/salt/dcos_cache/{{ cluster }}/genconf/config.yaml
    - source: salt://dcos/templates/config.yaml
    - template: jinja
    - makedirs: True
    - context:
      config: {{ properties['config'] }}
      cluster: {{ cluster }}

{{ cluster }} ip-detect:
  file.managed:
    - name: /srv/salt/dcos_cache/{{ cluster }}/genconf/ip-detect
    - source: salt://dcos/scripts/ip-detect
    - makedirs: True
    - require_in:
      - file: {{ cluster }} config.yaml

{% if properties['installer'].get('type') == 'enterprise' %}
{{ cluster }} license.txt:
  file.managed:
    - name: /srv/salt/dcos_cache/{{ cluster }}/genconf/license.txt
    - source: salt://dcos/templates/license.txt
    - template: jinja
    - makedirs: True
    - context:
      license: {{ properties.get('license', salt['pillar.get']('dcos:defaults:license')) }}
    - require_in:
      - file: {{ cluster }} config.yaml
{% endif %}

{% if properties['config'].get('fault_domain_enabled') == 'true' %}
{{ cluster }} fault-domain-detect:
  file.managed:
    - name: /srv/salt/dcos_cache/{{ cluster }}/genconf/fault-domain-detect
    - source: salt://dcos/scripts/fault-domain-detect
    - makedirs: True
    - require_in:
      - file: {{ cluster }} config.yaml
{% endif %}

{% if properties['config'].get('ip_detect_public_filename', salt['pillar.get']('dcos:defaults:config:ip_detect_public_filename')) %}
{{ cluster }} ip-detect-public:
  file.managed:
    - name: /srv/salt/dcos_cache/{{ cluster }}/genconf/ip-detect-public
    - source: {{ properties['config'].get('ip_detect_public_filename', salt['pillar.get']('dcos:defaults:config:ip_detect_public_filename')) }}
    - makedirs: True
    - require_in:
      - file: {{ cluster }} config.yaml
{% endif %}
{% endfor %}
