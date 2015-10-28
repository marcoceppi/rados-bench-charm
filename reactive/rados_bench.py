import os

from charmhelpers.core.hookenv import (
    status_set,
    relation_get,
    service_name,
)

from charmhelpers.fetch import apt_install
from charmhelpers.core.templating import render
from charms.reactive import (
    when,
    when_not,
    hook,
    set_state,
    remove_state,
    is_state,
)

from charms import ceph_utils as ceph


@hook('install')
def install():
    if not os.path.isdir('/etc/ceph'):
        os.mkdir('/etc/ceph')
    status_set('maintenance', 'installing dependencies')
    apt_install('ceph-common')
    update_status()


def ceph_connected(_=None):
    update_status()


@when('radosgw.ready')
@when('radosgw.connected')
def heyo():
    update_status()


@hook('benchmarks.required')
def benchmark(rel):
    status_set('maintenance', 'sending benchmarks...')
    rel.benchmarks(['write', 'read-rand', 'read-seq'])
    update_status()


@hook('update-status')
def update_status():
    if not is_state('radosgw.connected'):
        return status_set('blocked', 'need to be connected to a ceph cluster')

    if is_state('radosgw.connected') and not is_state('radosgw.ready'):
        return status_set('waiting', 'credentials from ceph')


    status_set('active', 'ready to benchmark')
