'''Pretty-print documents as plain text'''

import textwrap
import functools
import itertools
import collections

# Todo: coerce should be called on retrieval, not insertion

__all__ = ['document', 'paragraph', 'table', 'row', 'txt']




# Building document

def document(title=None, items=None, style=None):
    '''style: itemsep'''
    return Node(DOC, format_document, {'title' : txt}, style, title=title, items=items or [])

def paragraph(text=None, style=None):
    return Node(PAR, format_paragraph, {'text' : txt}, style, text=text)

def table(title=None, rows=None, header_row=None, style=None):
    return Node(TAB, format_table, {'title': txt}, style, title=title, rows=rows or [],
                header_row=header_row)

def row(items=None, style=None):
    '''style: columnsep'''
    return Node(ROW, coerced={'items': txt}, style=style, items=items or [])

def txt(text=None, style=None):
    '''style: width'''
    return Node(TXT, format_text, style=style, text=text)

def vbox(items=None):
    return Node(VBOX, format_vbox, items=items or [])




def coerce(f, value, acceptable_type=None):
    acceptable_type = acceptable_type or Node
    if isinstance(value, acceptable_type):
        return value
    return f(value)

class CoercingList(collections.MutableSequence):
    def __init__(self, f):
        self.a = []
        self.f = f

    def __getitem__(self, key):
        return self.a[key]

    def __setitem__(self, key, value):
        self.a[key] = self.f(value)

    def __delitem__(self, key):
        del self.a[key]

    def __len__(self):
        return len(self.a)

    def insert(self, i, x):
        self.a.insert(i, self.f(x))

    # TODO: make it better
    def __str__(self):
        return str(self.a)

    def __repr__(self):
        return repr(self.a)


def coercing_list(f, *items):
    a = CoercingList(functools.partial(coerce, f))
    a.extend(items)
    return a

DOC = 'document'
PAR = 'paragraph'
TAB = 'table'
ROW = 'row'
TXT = 'text'
VBOX = 'vbox'

class Node(collections.MutableSequence):
    #DEFAULT_ITEM_CLASS = txt

    def __init__(self, id, formatter=None, coerced=None, style=None, **properties):
        self.__dict__['coerced'] = coerced or {}
        self.id = id
        self.formatter = formatter
        self.style = style or {}
        # Funny: check it out
        self.__dict__['attrnames'] = properties.keys()
        for k, v in properties.iteritems():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        # is MutableSequence an instance of list?
        if isinstance(value, list):
            ctype = self.coerced[name] if name in self.coerced else txt
            value = coercing_list(ctype, *value)
        elif name in self.coerced:
            value = coerce(self.coerced[name], value)
        super(Node, self).__setattr__(name, value)

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __delitem__(self, key):
        del self.items[key]

    def __len__(self):
        return len(self.items)

    def insert(self, i, x):
        self.items.insert(i, self.f(x))

    def format(self, style=None):
        return self.formatter(self, style or {})

    def tostring(self):
        return '\n'.join(self.format())

    def __str__(self):
        #return ''
        return str(dict(id=self.id, properties={k:str(getattr(self, k)) for k in self.attrnames}, style=self.style))


def updatefmt(f):
    @functools.wraps(f)
    def wrapper(n, style, *args, **kwds):
        return f(n, update(style, n.style), *args, **kwds)
    return wrapper

@updatefmt
def format_document(n, style):
    return vjoin([i.format(style) for i in n.items],
                 **extract(style, ('itemsep', 'sep')))

@updatefmt
def format_paragraph(n, style):
    return n.text.format(style)

@updatefmt
def format_table(n, style):
    items = [n.title]
    colnbr = len(n.rows[0].items)
    vboxes = [vbox() for i in xrange(colnbr)]
    allrows = n.rows
    if n.header_row:
        # Cannot add CoercingList directly, unfortunately
        allrows = [n.header_row, row(['---'] * colnbr)] + list(allrows)
    for r in allrows:
        for i in xrange(colnbr):
            vboxes[i].items.append(r.items[i])
    return hjoin([b.format(style) for b in vboxes],
                 **extract(style, ('columnsep', 'sep')))

@updatefmt
def format_text(n, style):
    return wrap(n.text, **extract(style, 'width'))

@updatefmt
def format_vbox(n, style):
    maxwidth = max(width(i) for i in n.items)
    return vjoin([hpadding(i.format(style), maxwidth) for i in n.items])

EMPTYLINE = ['']

# Text utils

def wrap(text, width=80):
    return textwrap.wrap(text, width=width)

def hpadding(area, n):
    return [line + (' ' * (n - len(line))) for line in area]

def vpadding(area, n):
    assure(n >= len(area),
           'n=%s smaller than number of lines in input=%s' % (n, len(area)))
    return area + EMPTYLINE*(n - len(area))

def hjoin(areas, sep=' '):
    hmax = max(len(a) for a in areas)
    padded_areas = [vpadding(a, hmax) for a in areas]
    fullrows = []
    for i in xrange(hmax):
        fullrows.append(sep.join(a[i] for a in areas))
    return fullrows

def vjoin(areas, sep=None):
    assure(sep is None or isinstance(sep, list),
           'vertical sep should be a list, not %s' % sep)
    separators = [sep]*(len(areas) - 1) if sep is not None else []
    return sum(roundrobin(areas, separators), [])

def width(thing):
    return max(len(line) for line in thing.format())


# Utils



def update(dst, src):
    dst.update(src)
    return dst

def extract(d, *args):
    args = [(a[0], a[1]) if isinstance(a, tuple) else (a, a) for a in args]
    return {newk:d[k] for (k, newk) in args if k in d}

def assure(expr, error_msg):
    if not expr:
        raise ValueError(error_msg)

# From itertools' recipes

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
