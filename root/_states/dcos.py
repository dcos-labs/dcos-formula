# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import salt.exceptions
import logging

log = logging.getLogger(__name__)


__virtualname__ = 'dcos'

def __virtual__():
    '''
    Set this modules name
    '''
    return __virtualname__


def change_login(name, login, password, description=None, url=None):
    '''
    Remove the bootstrap user and create a new admin account

    This state module is used after cluster creation. It calls out to the execution module
    ``dcos`` in order to remove the bootstrap user and create a new admin.

    name
        A name for this state
    login
        Name of the new admin login
    password
        Password of the new admin login
    description : None
        Full name of the new admin
    url : None
        URL to the DC/OS cluster
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': '',
        'pchanges': {},
        }

    # Start with basic error-checking. Do all the passed parameters make sense
    # and agree with each-other?
    if len(login) < 1 or len(password) < 6:
        raise salt.exceptions.SaltInvocationError(
            'Argument "login" or "password" too short')

    # Check the current state of the system. Does anything need to change?
    current_state = __salt__['dcos.change_login'](login, password, description, url, True)

    if len(current_state['changes']['new']) == 0:
        ret['result'] = True
        ret['comment'] = 'System already in the correct state'
        return ret

    # The state of the system does need to be changed. Check if we're running
    # in ``test=true`` mode.
    if __opts__['test'] == True:
        ret['comment'] = 'The state of "{0}" will be changed.'.format(name)
        ret['pchanges'] = current_state['changes']

        # Return ``None`` when running with ``test=true``.
        ret['result'] = None

        return ret

    # Finally, make the actual change and return the result.
    new_state = __salt__['dcos.change_login'](login, password, description, url, False)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = new_state['changes']

    ret['result'] = True

    return ret
