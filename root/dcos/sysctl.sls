br_netfilter:
  kmod.present:
    - persist: True

net.bridge.bridge-nf-call-iptables:
  sysctl.present:
    - value: 1
    - require:
      - kmod: br_netfilter

net.bridge.bridge-nf-call-ip6tables:
  sysctl.present:
    - value: 1
    - require:
      - kmod: br_netfilter
