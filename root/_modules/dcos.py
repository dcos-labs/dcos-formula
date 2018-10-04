# -*- coding: utf-8 -*-
'''
A module for DC/OS specific functions
'''
from __future__ import absolute_import, print_function, unicode_literals
import os
import logging
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv

log = logging.getLogger(__name__)

__virtualname__ = 'dcos'


class DCOSAuth:
    """Used to acquire a DCOS authentication token to make requests to other DCOS components.
    Can also create and delete users and assign them to groups.
    """
    def __init__(self, admin_url, login=None, password=None, description=None, log=None):
        """Constructor
        :rtype: DCOSAuth
        :param admin_url: The DCOS UI url
        :param login:
        :param password:
        :param description:
        """
        self.admin_url = admin_url
        self.login = login
        self.password = password
        self.description = description
        self.default_headers = {'Accept': 'application/json', 'Accept-Charset': 'utf-8'}
        self.default_login = {'login': 'bootstrapuser', 'password': 'deleteme'}
        self.auth_header = None
        self.log = logging.getLogger(self.__class__.__name__)

    @property
    def default_login_works(self):
        """Tests if the default login works.
        :rtype: bool
        :return: True or False
        """
        return True if self.default_login_auth_header else False

    @property
    def default_login_auth_header(self):
        """Requests a DCOS authentication token header using default credentials
        :rtype: Union[dict, None]
        :return: authentication header dict or None
        """
        return self.get_auth_header(self.default_login['login'], self.default_login['password'])

    def create_user(self, login, password, description):
        """Create a user
        :rtype: bool
        :param login: The user's login
        :param password: The user's password
        :param description: The user's full name
        :return: True on success
        """
        return self.request('put',
                            '/users/{}'.format(login),
                            json={'password': password,
                                  'description': description
                                  },
                            msg='creating user {}'.format(login)
                            )

    def delete_user(self, login):
        """Delete a user
        :rtype: bool
        :param login: The user's login
        :return: True on success
        """
        return self.request('delete',
                            '/users/{}'.format(login),
                            msg='deleting user {}'.format(login)
                            )

    def add_user_to_group(self, login, group):
        """Add a user to a group
        :rtype: bool
        :param login: The user's login
        :param group: The group to add the user to
        :return: True on success
        """
        return self.request('put',
                            '/groups/{}/users/{}'.format(group, login),
                            msg='adding user {} to group {}'.format(login, group)
                            )

    def request(self, method, path, msg=None, json=None, retfmt='bool', errorfatal=True, autoauth=True, verify_ssl=False):
        """Send a http request to the DCOS authentication service
        :rtype: Union[bool, object, dict, None]
        :param method: HTTP method to use (get, post, put, delete)
        :param path: The API path to send the request to
        :param msg: An optional log message
        :param json: Optional JSON data to be transmitted with the request
        :param verify_ssl: Bool verify SSL certificate when using https admin_url
        :param retfmt: Return format (default=bool, json, request)
                       json will return the r.json() data
                       request will return the entire r object
        :param errorfatal: If True throw exception on error
        :param autoauth: Try to automatically acquire an auth token
        :return: depends on retfmt
        """
        url = self.admin_url + '/acs/api/v1' + path

        if msg:
            self.log.info(msg)

        headers = self.default_headers.copy()

        if not self.auth_header and autoauth:
            self.set_auth_header()

        if self.auth_header:
            headers.update(self.auth_header)

        self.log.debug('Request: {}, {}'.format(headers, json))

        if method == 'get':
            r = requests.get(url, headers=headers, json=json, verify=verify_ssl)
        elif method == 'post':
            r = requests.post(url, headers=headers, json=json, verify=verify_ssl)
        elif method == 'put':
            r = requests.put(url, headers=headers, json=json, verify=verify_ssl)
        elif method == 'delete':
            r = requests.delete(url, headers=headers, json=json, verify=verify_ssl)

        if 200 <= r.status_code < 300:
            self.log.debug("success")
            if retfmt == 'json':
                self.log.debug('returning json')
                return r.json()
            elif retfmt == 'request':
                self.log.debug('returning request object')
                return r
            else:
                return True
        else:
            if 'Content-Type' in r.headers and r.headers['Content-Type'] == 'application/json':
                resp = r.json()['code']
            else:
                resp = r.reason
            msg = "failed: {}".format(resp)
            self.log.debug(msg)
            if errorfatal:
                raise Exception(msg)
            else:
                if retfmt == 'request':
                    self.log.debug('returning request object')
                    return r
                else:
                    return None

    def get_auth_header(self, login, password):
        """Try to acquire a DCOS authentication token
        :rtype: Union[dict, None]
        :param login: Login to use
        :param password: Password to use
        :return: A header dict with the token or None
        """
        json = self.request('post',
                            '/auth/login',
                            json={'uid': login, 'password': password},
                            msg='authenticating at {} with user {}'.format(self.admin_url, login),
                            errorfatal=False,
                            retfmt='json',
                            autoauth=False
                            )
        if json:
            return {'Authorization': 'token=%s' % json['token']}
        else:
            return None

    def set_auth_header(self):
        """Set the objects authentication header by requesting an auth token
        :rtype: bool
        :return: True or False
        """
        self.auth_header = self.get_auth_header(self.login, self.password)
        return True if self.auth_header else False

    def change_login(self, dry_run=False):
        """Test if the configured admin account can authenticate if not create it.
        Also test if the default bootstrap user exists and remove it.
        """
        ret = {
            'changes': {'old': [], 'new': []},
            'result': False,
        }

        admin_exists = self.set_auth_header()

        if self.default_login_works:
            self.log.info("default login worked, removing it")
            ret['changes']['old'].append('default login worked, removing it')
            if admin_exists:
                self.log.info("admin user exists, only deleting default user")
                ret['changes']['old'].append('admin user already exists, only deleting default user')
            else:
                # Since the admin user doesn't exist but we were able to authenticate
                # using the default login request an authentication token and
                # explicitly set the object's auth_header to it.
                self.auth_header = self.default_login_auth_header

                self.log.info("admin user doesn't exist, creating it before deleting default user")
                if not dry_run:
                    self.create_user(self.login, self.password, self.description)
                    self.add_user_to_group(self.login, 'superusers')
                ret['changes']['new'].append('creating new admin user {}'.format(self.login))
            if not dry_run:
                self.delete_user(self.default_login['login'])
            ret['changes']['new'].append('removing default admin user {}'.format(self.default_login['login']))
        else:
            if not admin_exists:
                self.log.error("default user doesn't exist but admin user doesn't work either - manual intervention required")
                ret['changes']['old'].append("default user doesn't exist but admin user doesn't work either - manual intervention required")
                return ret
            else:
                self.log.info("default user doesn't exist and admin user works - everything looking good")
                ret['changes']['old'].append("default user doesn't exist and admin user works")
        ret['result'] = True
        return ret


def __virtual__():
    '''
    Confine this module to the Salt Master
    '''
    return __virtualname__


def ip():
    '''
    Returns the IP used for DC/OS communication

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.ip
    '''
    local_script = '/opt/mesosphere/bin/detect_ip'
    remote_script = 'salt://dcos/scripts/ip-detect'
    script = local_script if os.path.exists(local_script) else remote_script
    return __salt__['cmd.script'](script)['stdout']


def public_ip():
    '''
    Returns the public IP used for DC/OS communication

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.public_ip
    '''
    local_script = '/opt/mesosphere/bin/detect_ip_public'
    remote_script = 'salt://dcos/scripts/ip-detect-public'
    script = local_script if os.path.exists(local_script) else remote_script
    return __salt__['cmd.script'](script)['stdout']


def change_login(login, password, description=None, url=None, dry_run=False):
    '''
    Remove the bootstrap user and create a new admin account

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.change_login newadmin newpassword [description] [url] [dry_run]
    '''
    url = 'https://'+ip() if url is None else url
    description = login if description is None else description
    dcos_auth = DCOSAuth(url, login, password, description)
    return dcos_auth.change_login(dry_run)


def mesos_ready():
    '''
    Returns True if mesos-master/mesos-slave on the DC/OS node is ready

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.mesos_ready
    '''
    dcos_shell = '/opt/mesosphere/bin/dcos-shell'
    args = 'dcos-diagnostics check node-poststart '
    master_args = 'mesos_master_replog_synchronized'
    agent_args = 'mesos_agent_registered_with_masters'
    args += master_args if os.path.exists('/etc/mesosphere/roles/master') else agent_args
    result_json = __salt__['cmd.script'](dcos_shell, args=args)['stdout']
    result = json.loads(result_json)
    return result['status'] == 0


def zookeeper_ready():
    '''
    Returns True if Zookeeper on the DC/OS master node is ready

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.zookeeper_ready
    '''
    dcos_shell = '/opt/mesosphere/bin/dcos-shell'
    args = 'dcos-diagnostics check node-poststart zookeeper_serving'
    if not os.path.exists('/etc/mesosphere/roles/master'):
        return None
    result_json = __salt__['cmd.script'](dcos_shell, args=args)['stdout']
    result = json.loads(result_json)
    return result['status'] == 0


def ready():
    '''
    Returns True if the DC/OS node is ready

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.ready
    '''
    dcos_shell = '/opt/mesosphere/bin/dcos-shell'
    args = 'dcos-diagnostics check node-poststart'
    result_json = __salt__['cmd.script'](dcos_shell, args=args)['stdout']
    result = json.loads(result_json)
    return result['status'] == 0


def crdb_underreplicated():
    '''
    Returns the number of underreplicated CockroachDB ranges'

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.crdb_underreplicated
    '''
    dcos_shell = '/opt/mesosphere/bin/dcos-shell'
    args = 'cockroach node status --ranges --certs-dir=/run/dcos/pki/cockroach --format csv --host=' + ip()
    if not os.path.exists('/etc/mesosphere/roles/master'):
        return None
    result_csv = __salt__['cmd.script'](dcos_shell, args=args)['stdout']
    f = StringIO(result_csv)
    reader = csv.DictReader(f)
    iam_status = sum([int(x['ranges_underreplicated']) for x in reader if x['address']])
    return iam_status


def crdb_ready():
    '''
    Returns True if CockroachDB is replicated'

    CLI Example:

    .. code-block:: bash

        salt -C 'G@dcos:role:master' dcos.crdb_ready
    '''
    return crdb_underreplicated() == 0
