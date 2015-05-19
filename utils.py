import functools
import itertools
import collections

def coerce(cls, value, base):
    if isinstance(value, base):
        return value
    return cls(value)

class CoercingList(collections.MutableSequence):
    def __init__(self, cls, base, iterable=None):
        iterable = iterable or []
        self.a = list(iterable)
        self.cls = cls
        self.base = base

    def __getitem__(self, key):
        return self.a[key]

    def __setitem__(self, key, value):
        self.a[key] = coerce(self.cls, value, self.base)

    def __delitem__(self, key):
        del self.a[key]
        
    def __len__(self):
        return len(self.a)
        
    def insert(self, i, x):
        self.a.insert(i, coerce(self.cls, x, self.base))


def update(dst, src):
    dst.update(src)
    return dst

def extract(d, *args):
    args = [(a[0], a[1]) if isinstance(a, tuple) else (a, a) for a in args]
    return {newk:d[k] for (k, newk) in args if k in d}



# From itertools' recipes, see https://docs.python.org/2/library/itertools.html

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))
            