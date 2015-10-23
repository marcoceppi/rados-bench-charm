
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.templating import render
from charms.reactive import (
    when,
    when_not,
    hook,
    set_state,
    remove_state,
)

@hook('install')
def install():
    pass

