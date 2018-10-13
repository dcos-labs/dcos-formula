{%- set cache_dir = salt['pillar.get']('dcos:cache_dir', '/srv/salt/dcos_cache') -%}
{%- set cache_uri = salt['pillar.get']('dcos:cache_uri', 'salt://dcos_cache') -%}
{%- set cluster = salt['pillar.get']('cluster', None) %}
{%- if cluster != None %}
{%-   set properties = salt['pillar.get']('dcos:clusters:'+cluster, None) %}
{%-   set clusters = {cluster: properties} if properties else None %}
{%- else %}
{%-   set clusters = salt['pillar.get']('dcos:clusters', None) %}
{%- endif %}
