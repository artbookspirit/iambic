import functools
import pprint
import collections

from . import nodes, textarea, utils
from .nodes import DOC, PAR, TAB, ROW, PLA, VBOX

def update_style(f):
    @functools.wraps(f)
    def wrapper(node, style, *args, **kwds):
        return f(node, utils.update(style, node.style), *args, **kwds)
    return wrapper
    

@update_style
def document(node, style):
    return textarea.vjoin([compose(i, style) for i in node.items],
                          **utils.extract(style, ('itemsep', 'sep')))

@update_style
def paragraph(node, style):
    return compose(node.text, style)

@update_style
def table(node, style):
    items = [node.title]
    colnbr = len(node.rows[0].items)
    vboxes = [nodes.vbox() for i in xrange(colnbr)]
    allrows = node.rows
    if node.header_row:
        # Cannot add CoercingList directly, unfortunately
        allrows = [node.header_row, nodes.row(['---'] * colnbr)] + list(allrows)
    for r in allrows:
        for i in xrange(colnbr):
            vboxes[i].items.append(r.items[i])
    return textarea.hjoin([compose(b, style) for b in vboxes],
                          **utils.extract(style, ('columnsep', 'sep')))

@update_style
def plain(node, style):
    return textarea.wrap(node.text, **utils.extract(style, 'width'))

@update_style
def vbox(node, style):
    maxwidth = max(textarea.width(compose(i, style)) for i in node.items)
    return textarea.vjoin(
        [textarea.hpadding(compose(i, style), maxwidth) for i in node.items])

    

def str_plain(node, details, maxlen=10, suffix='..'):
    if len(node.text) <= maxlen:
        t = node.text
    else:
        t = node.text[:maxlen] + suffix
    return '%s(%s)' % (node.id, t)
    
def str_generic(node, details):
    s = []
    for k in node.attrnames:
        v = getattr(node, k)
        if isinstance(v, utils.CoercingList):
            print list(v)
            v = '[' + ', '.join([x.tostring(details=False) for x in v]) + ']'
        s.append('$%s=%s' % (k, v))
    if details:
        s.append('style=%s' % strstyle(node.style))
    return '%s(%s)' % (node.id, ', '.join(s))
    
def strstyle(style):
    return pprint.pformat(style)
    

    
HANDLERS = {DOC: {'compose': document, 'summary': str_generic},
            PAR: {'compose': paragraph, 'summary': str_generic},
            TAB: {'compose': table, 'summary': str_generic},
            PLA: {'compose': plain, 'summary': str_plain},
            VBOX: {'compose': vbox, 'summary': str_generic}}

def dispatch(thing, action, *args, **kwds):
    return HANDLERS[thing.id][action](thing, *args, **kwds)
    
def compose(thing, style=None):
    return dispatch(thing, 'compose', style or {})
    
def tostring(thing, style=None):
    return '\n'.join(compose(thing, style))
    
def summary(thing, details=True):
    return dispatch(thing, 'summary', details)
    