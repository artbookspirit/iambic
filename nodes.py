import collections
from .utils import CoercingList, coerce

class Node(collections.MutableSequence):

    def __init__(self, default_cls, id, coerced=None, 
                 style=None, **properties):
        self.__dict__['coerced'] = coerced or {}
        self.default_cls = default_cls
        self.id = id
        self.style = style or {}
        # Funny: check it out
        self.__dict__['attrnames'] = properties.keys()
        for k, v in properties.iteritems():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        if isinstance(value, list):
            try:
                ctype = self.coerced[name]  
            except KeyError:
                ctype = self.default_cls
            value = CoercingList(ctype, Node, value)
        elif name in self.coerced:
            value = coerce(self.coerced[name], value, Node)
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
        self.items.insert(i, coerce(self.coerced[name], x, Node))


DOC = 'document'
PAR = 'paragraph'
TAB = 'table'
ROW = 'row'
PLA = 'plain'
VBOX = 'vbox'        


def document(title=None, items=None, style=None):
    '''style: itemsep'''
    return node(DOC, coerced={'title' : plain}, style=style, title=title, 
                items=items or [])

def paragraph(text=None, style=None):
    return node(PAR, coerced={'text' : plain}, style=style, text=text)

def table(title=None, rows=None, header_row=None, style=None):
    return node(TAB, coerced={'title': plain}, style=style, title=title, 
                rows=rows or [], header_row=header_row)

def row(items=None, style=None):
    '''style: columnsep'''
    return node(ROW, coerced={'items': plain}, style=style, items=items or [])

def plain(text=None, style=None):
    '''style: width'''
    return node(PLA, style=style, text=text)

def vbox(items=None):
    return node(VBOX, items=items or [])
    
    
def node(id, coerced=None, style=None, **properties):
    return Node(plain, id, coerced, style, **properties)
