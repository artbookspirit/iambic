'''Pretty-print documents as plain text'''

import textwrap
import functools
import itertools

# Todo: coerce should be called on retrieval, not insertion

__all__ = ['document', 'paragraph', 'table', 'row', 'txt', 'format', 'tostring']


# Building document

def document(title=None, items=None, fmt=None):
    '''fmt: itemsep'''
    return node(DOC, title=coerce(txt, title), items=items or [], fmt=fmt)

def paragraph(text=None, fmt=None):
    return node(PAR, text=coerce(txt, text), fmt=fmt)

def table(title=None, rows=None, header_row=None, fmt=None):
    return node(TAB, title=coerce(txt, title), rows=rows or [], 
                header_row=header_row, fmt=fmt)
                
def row(values=None, fmt=None):
    '''fmt: columnsep'''
    values = [coerce(txt, v) for v in (values or [])]
    return node(ROW, values=values)

def txt(text=None, fmt=None):
    '''fmt: width'''
    return node(TXT, text=text, fmt=fmt)    
    
def vbox(items=None):
    return node(VBOX, items=items or [])
    
    
# Formatting
    
def format(thing, fmt=None, dispatch_table=None):
    dispatch_table = dispatch_table or DISPATCH
    f = dispatch_table[thing['id']]
    return f(thing, fmt or {})

def tostring(thing):
    return '\n'.join(format(thing))

    


def node(id, fmt=None, **kwds):
    return dict(id=id, fmt=fmt or {}, **kwds)

def updatefmt(f):
    @functools.wraps(f)
    def wrapper(n, fmt, *args, **kwds):
        return f(n, update(fmt, n['fmt']), *args, **kwds)
    return wrapper

@updatefmt
def format_document(n, fmt):
    return vjoin([format(i, fmt) for i in n['items']], 
                 **extract(fmt, ('itemsep', 'sep')))

@updatefmt    
def format_paragraph(n, fmt):
    return format(n['text'], fmt)

@updatefmt        
def format_table(n, fmt):
    items = [n['title']]
    colnbr = len(n['rows'][0])
    vboxes = [vbox() for i in xrange(colnbr)]
    allrows = n['rows']
    if n['header_row']:
        allrows = [n['header_row'], row(['---'] * colnbr)] + allrows
    for r in allrows:
        for i in xrange(colnbr):
            vboxes[i]['items'].append(r['values'][i])
    return hjoin([format(b, fmt) for b in vboxes],
                 **extract(fmt, ('columnsep', 'sep')))
    
@updatefmt        
def format_text(n, fmt):
    return wrap(n['text'], **extract(fmt, 'width'))
    
@updatefmt            
def format_vbox(n, fmt):
    maxwidth = max(width(i) for i in n['items'])
    return vjoin([hpadding(format(i, fmt), maxwidth) for i in n['items']])
    
    
DOC = 'document'
PAR = 'paragraph'
TAB = 'table'
ROW = 'row'
TXT = 'text'  
VBOX = 'vbox'  

DISPATCH = {
    DOC: format_document,
    PAR: format_paragraph,
    TAB: format_table,
    TXT: format_text,
    VBOX: format_vbox
}    

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
    return max(len(line) for line in format(thing))

    
# Utils

def coerce(f, v):
    if isinstance(v, dict):
        return v
    return f(v)

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
            