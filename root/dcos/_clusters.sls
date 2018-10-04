{%- set cluster = salt['pillar.get']('cluster', None) %}
{%- if cluster != None %}
{%-   set properties = salt['pillar.get']('dcos:clusters:'+cluster, None) %}
{%-   set clusters = {cluster: properties} if properties else None %}
{%- else %}
{%-   set clusters = salt['pillar.get']('dcos:clusters', None) %}
{%- endif %}
