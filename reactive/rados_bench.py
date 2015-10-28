
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
)

from charms import ceph_utils as ceph


@hook('install')
def install():
    if not os.path.isdir('/etc/ceph'):
        os.mkdir('/etc/ceph')

    apt_install('ceph-common')


@when('ceph.available')
def configure_ceph(client):
    ceph.configure(service=SERVICE_NAME, key=client.key(), auth=client.auth(),
                   use_syslog=client.use_syslog())
    status_set('active', '')


@hook('benchmarks.required')
def benchmark(rel):
    rel.benchmarks(['write', 'read-rand', 'read-seq'])
    status_set('active', 'streaming metric data')
