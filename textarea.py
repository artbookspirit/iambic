import textwrap
from . import utils

SPACE = ' '
EMPTYLINE = ['']

def line_hpadding(line, wdth, chr=' '):
    assert wdth >= len(line)
    return line + (chr * (wdth - len(line)))

def wrap(text, width=80):
    return textwrap.wrap(text, width=width)
    
def width(area):
    return max(len(line) for line in area)
    
def height(area):
    return len(area)

def hpadding(area, wdth=None, chr=SPACE):
    wdth = wdth or width(area)
    return [line_hpadding(line, wdth) for line in area]

def vpadding(area, hght, paddingline=EMPTYLINE):
    assert hght >= len(area),\
           'hght=%s smaller than number of input lines=%s' % (hght, len(area))
    return area + paddingline * (hght - len(area))

def hjoin(areas, sep=SPACE, paddingline=EMPTYLINE):
    maxheight = max(height(a) for a in areas)
    sameheight = [vpadding(a, maxheight, paddingline) for a in areas]
    return [sep.join(row) for row in zip(*sameheight)]

def vjoin(areas, sep=None):
    assert sep is None or isinstance(sep, list),\
           'vertical sep should be a list, not %s' % sep
    seps = [sep]*(len(areas) - 1) if sep is not None else []
    return sum(utils.roundrobin(areas, seps), [])


    