import unittest
import iambic as ia
import textwrap

LOREM_IPSUM = textwrap.dedent('''\
    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Proin nibh augue, 
    suscipit a, scelerisque sed, lacinia in, mi. Cras vel lorem. Etiam 
    pellentesque aliquet tellus. Phasellus pharetra nulla ac diam. Quisque 
    semper justo at risus. Donec venenatis, turpis vel hendrerit interdum, dui 
    ligula ultricies purus, sed posuere libero dui id orci. Nam congue, pede 
    vitae dapibus aliquet, elit magna vulputate arcu, vel tempus metus leo non 
    est. Etiam sit amet lectus quis est congue mollis. Phasellus congue lacus 
    eget neque. Phasellus ornare, ante vitae consectetuer consequat, purus 
    sapien ultricies dolor, et mollis pede metus eget nisi. Praesent sodales 
    velit quis augue. Cras suscipit, urna at aliquam rhoncus, urna quam viverra 
    nisi, in interdum massa nibh nec erat.''')

    
class TestIambic(unittest.TestCase):
    def setUp(self):
        doc = ia.document('Foo document')
        fmt = dict(width=30, columnsep='|', itemsep=['%'*30])
        doc['fmt'] = fmt
        p1 = ia.paragraph('\n'.join(LOREM_IPSUM.splitlines()[:3]))
        doc['items'].append(p1)
        t1 = ia.table('Foo table')
        t1['header_row'] = ia.row(['FIRST', 'SECOND', 'THIRD'])
        t1['rows'].append(ia.row(['foo', 'bar', 'baz']))
        t1['rows'].append(ia.row(['this', 'is', 'something']))
        doc['items'].append(t1)
        p2 = ia.paragraph('\n'.join(LOREM_IPSUM.splitlines()[3:7]))
        doc['items'].append(p2)
        self.doc = doc
        
    def test_dummy(self):
        print ia.tostring(self.doc)
    