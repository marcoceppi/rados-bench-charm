from collections import Mapping
from itertools import chain
from operator import add

_FLAG_FIRST = object()

key_map = {
    'Total writes made': {
        'key': 'results.writes',
        'meta': {'direction': 'desc', 'units': ''},
    },
    'Write size': {
        'key': 'results.size',
        'meta': {'direction': 'desc', 'units': 'bytes'},
    },
    'Bandwidth (MB/sec)': {
        'key': 'results.bandwidth-average',
        'meta': {'direction': 'desc', 'units': 'MB/s'},
    },
    'Stddev Bandwidth': {
        'key': 'results.bandwidth-stddev',
        'meta': {'direction': 'asc', 'units': ''},
    },
    'Max bandwidth (MB/sec)': {
        'key': 'results.bandwidth-max',
        'meta': {'direction': 'desc', 'units': 'MB/s'},
    },
    'Min bandwidth (MB/sec)': {
        'key': 'results.bandwidth-min',
        'meta': {'direction': 'desc', 'units': 'MB/s'},
    },
    'Average Latency': {
        'key': 'results.latency-average',
        'meta': {'direction': 'asc', 'units': ''},
    },
    'Stddev Latency': {
        'key': 'results.latency-stddev',
        'meta': {'direction': 'asc', 'units': ''},
    },
    'Max latency': {
        'key': 'results.latency-max',
        'meta': {'direction': 'asc', 'units': ''},
    },
    'Min latency': {
        'key': 'results.latency-min',
        'meta': {'direction': 'asc', 'units': ''},
    },
}


def flatten(d, join=add, lift=lambda x:x):
    results = []
    def visit(subdict, results, partialKey):
        for k,v in subdict.items():
            newKey = lift(k) if partialKey==_FLAG_FIRST else join(partialKey,lift(k))
            if isinstance(v,Mapping):
                visit(v, results, newKey)
            else:
                results.append((newKey,v))
    visit(d, results, _FLAG_FIRST)
    return results
