# -*- coding: utf-8 -*-

import sys

def iteritems(d, **kw):
    return iter(d.items(**kw))
from urllib.parse import urlparse
from imp import reload as reload_six
from queue import Empty, Queue


def withMetaclass(meta, *bases):
    """Create a base class with a metaclass."""

    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class MetaClass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(MetaClass, 'temporary_class', (), {})
