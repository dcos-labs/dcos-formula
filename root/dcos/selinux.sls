/etc/selinux/config:
  file.replace:
    - pattern: SELINUX=enforcing
    - repl: SELINUX=permissive

libselinux-utils:
  pkg.installed

#permissive:
#  selinux.mode

setenforce 0:
  cmd.run:
    - onlyif: getenforce | grep Enforcing
    - require:
      - pkg: libselinux-utils
