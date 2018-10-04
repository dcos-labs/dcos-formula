{% from 'dcos/_clusters.sls' import clusters %}
{% for cluster, properties in clusters.items() %}
{% if properties['installer'].get('type') == 'enterprise' %}
{%   set master_list = salt['mine.get']('G@dcos:role:master and G@dcos:cluster-id:'+cluster, 'dcos.public_ip', tgt_type='compound').values() %}
{%   if master_list|length > 0 %}
{%     set url = 'https://' + master_list[0] %}
{%     if 'admin' in properties or 'admin' in salt['pillar.get']('dcos:defaults') %}
{%       set login = properties.get('admin', {}).get('login', salt['pillar.get']('dcos:defaults:admin:login')) %}
{%       set password = properties.get('admin', {}).get('password', salt['pillar.get']('dcos:defaults:admin:password')) %}
{{ cluster }} admin user:
  dcos.change_login:
    - login: {{ login }}
    - password: {{ password }}
    - description: Admin User
    - url: {{ url }}
{%     endif %}
{%   endif %}
{% endif %}
{% endfor %}
