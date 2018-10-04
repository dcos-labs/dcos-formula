include:
  - .selinux

{%- set os_family = salt['grains.get']('os_family', '') %}
{%- set os_major_release = salt['grains.get']('osmajorrelease', 0)|int %}
{%- if os_family == 'RedHat' and os_major_release == 7 %}
docker package repository:
  pkgrepo.managed:
    - name: docker
    - humanname: Docker Repository
    - baseurl: https://download.docker.com/linux/centos/$releasever/$basearch/stable
    - gpgcheck: 1
    - gpgkey: https://download.docker.com/linux/centos/gpg
    - require_in:
      - pkg: docker package
{%- endif %}

docker:
  service.running:
    - enable: True
    - require:
      - pkg: docker package
      - group: docker group

docker group:
  group.present:
    - system: True
    - name: docker

docker package:
  pkg.installed:
    - pkgs:
      - docker
    - refresh: True
    - require:
      - cmd: setenforce 0
