dcos
====

Formula to install and configure DC/OS on Enterprise Linux 7.

.. note::

    See the full `Salt Formulas installation and usage instructions
    <http://docs.saltstack.com/en/latest/topics/development/conventions/formulas.html>`_.
    Refer to pillar.example for configurable values.

Available states
================

.. contents::
    :local:

``dcos.prepare``
------------
Prepares the DC/OS installer on the minion tagged as ``dcos:role:bootstrap`` or installs DC/OS prerequisits on any other minion

``dcos.install``
------------
Downloads and installs DC/OS on any node tagged with ``dcos:role`` ``master``, ``slave`` or ``slave_public`` (includes ``dcos.prepare``)

``dcos.upgrade``
------------
Downloads and upgrade DC/OS on any node tagged with ``dcos:role`` ``master``, ``slave`` or ``slave_public``

``dcos.change_login``
------------
Create the admin user and remove the default bootstrap user the first time a DC/OS cluster has been installed


Usage
=====
The general idea of this formula is that you prepare the DC/OS installer on the Salt Master, tagged with a grain ``dcos:role:bootstrap``,
from where it is downloaded by the minions of a cluster tagged with a grain ``dcos:role:[master,slave,slave_public]`` and a ``dcos:cluster-id:foobar``.

Example:

::

    $ export CLUSTER=prod1
    $ salt-call grains.setval dcos "{'role': 'bootstrap'}"
    $ salt 'master*.prod1.example.com' grains.setval dcos "{'role': 'master', 'cluster-id': '${CLUSTER}'}"
    $ salt 'agent*.prod1.example.com' grains.setval dcos "{'role': 'slave', 'cluster-id': '${CLUSTER}'}"
    $ salt 'pubagent*.prod1.example.com' grains.setval dcos "{'role': 'slave_public', 'cluster-id': '${CLUSTER}'}"


The cluster configuration is stored in a pillar only accessible to the Salt Master. By default each state iterates over all available clusters.
E.g. ``salt-call state.apply dcos.prepare`` on the Salt Master would prepare the DC/OS installer of all clusters. To target a specific cluster
provide the ``cluster`` variable as a pillar like so:

::

    $ export CLUSTER=prod1
    $ salt-call state.apply dcos.prepare pillar="{'cluster': '${CLUSTER}'}"

This would prepare the DC/OS installer for a cluster named `prod1`.

Once the installer is prepared a cluster would be installed using

::

    $ salt -C "G@dcos:cluster-id:${CLUSTER}" state.apply dcos.install

To upgrade a cluster to a new version of DC/OS first upgrade the Masters one by one and then a certain percentage of the Agents at a time.
Note that is you run stateful services they might require a more specific order in which you upgrade the Agent nodes.

::

    salt -C "G@dcos:cluster-id:${CLUSTER} and G@dcos:role:master" -b 1 state.apply dcos.upgrade
    salt -C "G@dcos:cluster-id:${CLUSTER} and G@dcos:role:slave or G@dcos:cluster-id:${CLUSTER} and G@dcos:role:slave_public" -b 20% state.apply dcos.upgrade


If a cluster is being installed for the first time it is advisable to change the default bootstrap user and create a dedicated admin.
To do so use the `dcos.change_login` state called from the bootstrap node.

::

    $ salt-call state.apply dcos.change_login pillar="{'cluster': '${CLUSTER}'}"

If the bootstrap node is not allowed to communicate with the master's adminrouter there's also an execution module available that will do the same thing:

::

    $ salt -C "G@dcos:cluster-id:${CLUSTER} and G@dcos:role:master" -b 1 dcos.change_login admin securepassword Administrator

will connect from the master locally and perform the change.


Miscellaneous states
====================

.. contents::
    :local:

``dcos.download``
------------
Download the DC/OS installer

``dcos.config``
------------
Create DC/OS configuration files like config.yaml, ip-detect, etc.

``dcos.docker``
------------
Install Docker and run the service

``dcos.genconf``
------------
Run genconf to create the DC/OS serve/ directory structure

``dcos.serve``
------------
Create the serve.tar.gz tarball which contains the DC/OS installer and is downloaded by minions

``dcos.pkgs``
------------
Install packages required for DC/OS to run

``dcos.nogroup``
------------
Create a group called nogroup - required for DC/OS to run

``dcos.sysctl``
------------
Make sysctl changes - required for DC/OS to run

``dcos.selinux``
------------
Turn off SELinux - required for DC/OS to run

``dcos.transfer``
------------
Transfer the serve.tar.gz tarball from the Salt master to a minion and extract it
