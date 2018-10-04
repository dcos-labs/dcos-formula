{%- if grains['dcos']['role'] in ['master', 'slave', 'slave_public'] %}
serve.tar.gz:
  archive.extracted:
    - name: /tmp/dcos-installer
    - source: salt://dcos_cache/{{ grains['dcos']['cluster-id'] }}/serve.tar.gz
    - makedirs: True
    - overwrite: True
    - require:
      - file: /tmp/dcos-installer

/tmp/dcos-installer:
  file.absent
{%- endif %}
