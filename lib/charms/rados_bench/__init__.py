
import rados
import subprocess

from charms.rados_bench.maps import key_map, flatten


class Rados(rados.Rados):
    def __init__(self):
        super(Rados, self).__init__(conffile='/etc/ceph/ceph.conf')
        self.connect()

    def bench(self, pool, method, seconds, op_size=None, concurrent=None, cleanup=True):
        def parse(results):
            data = {}
            summary = results.replace('  ', '').split('Total time run:')[1].split('\n')
            data['results.duration'] = {'direction': 'asc',
                                        'units': 'sec',
                                        'value': summary.pop(0)}
            data['meta.raw'] = results
            for item in summary:
                if ':' not in summary:
                    continue
                k, v = summary.split(':')
                if k not in key_map:
                    continue
                mapping = key_map[k].copy()
                mapping['meta']['value'] = v
                data[mapping['key']] = mapping['meta'].copy()

            if 'results.bandwidth.average' in data:
                data['meta.composite'] = data['results.bandwidth.average'].copy()

            return dict(flatten(data, join=lambda a,b:a+'.'+b))

        # rados -p <pool> bench <seconds> <method> -t <concurrent> -b op_size
        if method not in ['write', 'rand', 'seq']:
            raise ValueError('method must be either write, rand, or seq')

        cmd = ['rados', '-p', pool, 'bench', str(seconds), method]
        if op_size:
            try:
                cmd.extend(['-b', str(human_to_bytes(op_size))])
            except ValueError:
                pass # Meh
        if isinstance(concurrent, int):
            cmd.extend(['-t', str(concurrent)])
        if not cleanup:
            cmd.append('--no-cleanup')

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode:
            raise IOError("{!r} failed:\n{}".format(cmd, _as_text(err)))
        return parse(_as_text(out)) if out else None


def human_to_bytes(human):
    if human.isdigit():
        return human
    factors = {'k': 1024, 'm': 1048576, 'g': 1073741824, 't': 1099511627776}
    modifier = human[-1]
    if modifier.lower() in factors:
        return int(human[:-1]) * factors[modifier.lower()]

    raise ValueError("Can only convert K, M, G, and T")


def _as_text(bytestring):
    """Naive conversion of subprocess output to Python string"""
    if not bytestring:
        return ""

    return bytestring.decode("utf-8", "replace")
