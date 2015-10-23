# RADOS Benchmark charm

## Deploy

```
juju deploy ceph -n3
juju deploy rados-bench
juju add-relation rados-bench ceph
```

## Develop

From [source](https://github.com/marcoceppi/rados-bench-charm.git) execute the following commands:

```
git clone https://github.com/marcoceppi/rados-bench-charm.git rados-bench
charm build -o /tmp/charms rados-bench
juju deploy --repository=/tmp/charms local:trusty/rados-bench
```
