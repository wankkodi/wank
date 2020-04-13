from .. import html5lib
import xml.etree.ElementTree as ETree
# import re
# from copy import copy


class MyParser(html5lib.html5parser.HTMLParser):
    def parse(self, stream, *args, **kwargs):
        return MyElementTree(super(MyParser, self).parse(stream, *args, **kwargs))


class MyElementTree(ETree.ElementTree):
    # def __init__(self, *args):
    #     super(MyElementTree, self).__init__(*args)

    @property
    def attrib(self):
        return self._root.attrib

    @property
    def text(self):
        return self._root.text

    @property
    def tag(self):
        return self._root.tag

    @property
    def tail(self):
        return self._root.tail

    def xpath(self, obj):
        last_argument = None
        if obj[-1] != ']':
            # We have a suspicious to lxml xpath, while ElementTree does not support such argument...
            split_obj = obj.split('/')
            last_argument = split_obj[-1]
            if last_argument == 'text()' or last_argument[0] == '@':
                # We have lxml form
                obj = '/'.join(split_obj[:-1])
            else:
                # We have a regular form
                obj = '/'.join(split_obj)
                last_argument = None

        # res = [MyElementTree(x) for x in self.findall(obj)]
        res = [MyElementTree(x) for x in self.findall(obj)]
        # res = self.findall(obj)
        if last_argument is not None:
            if last_argument == 'text()':
                res = [x.text for x in res if x.text is not None]
            elif last_argument[0] == '@':
                # We have an argument of the style @href, @class, etc...
                res = [x.attrib[last_argument[1:]] for x in res if last_argument[1:] in x.attrib]
            else:
                raise ValueError('Wrong xpath value {o}.'.format(o=obj))
        return res


class MyElement(ETree.Element):
    def xpath(self, obj):
        res = self.findall(obj)
        return res
