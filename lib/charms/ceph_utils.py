#
# Copyright 2012 Canonical Ltd.
#
# This file is sourced from lp:openstack-charm-helpers
#
# Authors:
#  James Page <james.page@ubuntu.com>
#  Adam Gandelman <adamg@ubuntu.com>
#

import subprocess
import os

from charmhelpers.core.hookenv import log

KEYRING = '/etc/ceph/ceph.client.%s.keyring'
KEYFILE = '/etc/ceph/ceph.client.%s.key'

CEPH_CONF = """[global]
 auth supported = %(auth)s
 keyring = %(keyring)s
 mon host = %(mon_hosts)s
 log to syslog = %(use_syslog)s
 err to syslog = %(use_syslog)s
 clog to syslog = %(use_syslog)s
"""


def execute(cmd):
    subprocess.check_call(cmd)


def execute_shell(cmd):
    subprocess.check_call(cmd, shell=True)


def ceph_version():
    ''' Retrieve the local version of ceph '''
    if os.path.exists('/usr/bin/ceph'):
        cmd = ['ceph', '-v']
        output = subprocess.check_output(cmd)
        output = output.split()
        if len(output) > 3:
            return output[2]
        else:
            return None
    else:
        return None


def keyfile_path(service):
    return KEYFILE % service


def keyring_path(service):
    return KEYRING % service


def create_keyring(service, key):
    keyring = keyring_path(service)
    if os.path.exists(keyring):
        log('INFO', 'ceph: Keyring exists at %s.' % keyring)
    cmd = [
        'ceph-authtool',
        keyring,
        '--create-keyring',
        '--name=client.%s' % service,
        '--add-key=%s' % key]
    execute(cmd)
    log('INFO', 'ceph: Created new ring at %s.' % keyring)


def create_key_file(service, key):
    # create a file containing the key
    keyfile = keyfile_path(service)
    if os.path.exists(keyfile):
        log('INFO', 'ceph: Keyfile exists at %s.' % keyfile)
    fd = open(keyfile, 'w')
    fd.write(key)
    fd.close()
    log('INFO', 'ceph: Created new keyfile at %s.' % keyfile)


def configure(service, key, auth, use_syslog):
    create_keyring(service, key)
    create_key_file(service, key)
    hosts = get_ceph_nodes()
    mon_hosts = ",".join(map(str, hosts))
    keyring = keyring_path(service)
    with open('/etc/ceph/ceph.conf', 'w') as ceph_conf:
        ceph_conf.write(CEPH_CONF % locals())
    modprobe_kernel_module('rbd')


# TODO: re-use
def modprobe_kernel_module(module):
    log('INFO', 'Loading kernel module')
    cmd = ['modprobe', module]
    execute(cmd)
    cmd = 'echo %s >> /etc/modules' % module
    execute_shell(cmd)
