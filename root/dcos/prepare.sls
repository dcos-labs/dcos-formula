include:
{%- if salt['grains.get']('dcos:role') == 'bootstrap' %}
  - .serve
{%- else %}
  - .pkgs
  - .selinux
  - .sysctl
  - .nogroup
{%- endif %}
