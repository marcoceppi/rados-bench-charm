
from charmhelpers.core.hookenv import (
    status_set,
    relation_get,
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


@when('ceph.connected'):
def ceph_connected():
    updated_status()


@when('ceph.available')
def configure_ceph(client):
    status_set('maintenance', 'configuring ceph client')
    ceph.configure(service=SERVICE_NAME, key=client.key(), auth=client.auth(),
                   use_syslog=client.use_syslog())
    update_status()


@when_not('ceph.available')
def configure_ceph(client):
    status_set('maintenance', 'removing ceph configuration')
    os.remove('/etc/ceph/ceph.conf')
    update_status()


@hook('benchmarks.required')
def benchmark(rel):
    status_set('maintenance', 'sending benchmarks...')
    rel.benchmarks(['write', 'read-rand', 'read-seq'])
    update_status()


@hook('update-status')
def update_status():
    if not is_state('ceph.connected'):
        return status_set('blocked', 'need to be connected to a ceph cluster')

    if is_state('ceph.connected') and not is_state('ceph.available'):
        return status_set('waiting', 'credentials from ceph')


    status_set('active', 'ready to benchmark')
