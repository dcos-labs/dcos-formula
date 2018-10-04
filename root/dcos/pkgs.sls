include:
  - .docker

ntpd:
  service.running:
    - enable: True
    - requires:
      - pkg: DC/OS packages

DC/OS packages:
  pkg:
    - latest
    - refresh: True
    - names:
      - ntp
      - unzip
      - ipset
      - xz
      - curl
      - bash
      - tar
      - iputils
