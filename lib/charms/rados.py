
import rados
import subprocess


class Rados(rados.Rados):
    def __init__(self):
        super(Rados, self).__init__(conffile='/etc/ceph/ceph.conf')
        self.connect()

    def bench(pool, method, seconds, op_size=None, concurrent=None):
        # rados -p <pool> bench <seconds> <method> -t <concurrent> -b op_size
        if method not in ['write', 'rand', 'seq']:
            raise ValueError('method must be either write, rand, or seq')

        cmd = ['rados', '-p', pool, method]
        if op_size:
            try:
                cmd.extend(['-b', human_to_bytes(op_size)])
            except ValueError:
                pass # Meh
        if concurrent.is_integer():
            cmd.extend(['-t', concurrent])

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode:
            raise IOError("{!r} failed:\n{}".format(cmd, _as_text(err)))
        return _as_text(out) if out else None


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
    return bytestring.decode("utf-8", "replace")
