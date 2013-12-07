# Copyright (C) 2001-2002 Bram Cohen
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# The Software is provided "AS IS", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability,  fitness for a particular purpose and
# noninfringement. In no event shall the  authors or copyright holders
# be liable for any claim, damages or other liability, whether in an
# action of contract, tort or otherwise, arising from, out of or in
# connection with the Software or the use or other dealings in the
# Software.

# Written by Bram Cohen

from string import join

class FakeHandle:
    """A fake file handle. Used for testing."""

    def __init__(self, name, fakeopen):
        self.name = name
        self.fakeopen = fakeopen
        self.pos = 0
    
    def flush(self):
        pass
    
    def close(self):
        pass
    
    def seek(self, pos):
        self.pos = pos
    
    def read(self, amount = None):
        old = self.pos
        f = self.fakeopen.files[self.name]
        if self.pos >= len(f):
            return ''
        if amount is None:
            self.pos = len(f)
            return join(f[old:], '')
        else:
            self.pos = min(len(f), old + amount)
            return join(f[old:self.pos], '')
    
    def write(self, s):
        f = self.fakeopen.files[self.name]
        while len(f) < self.pos:
            f.append(chr(0))
        self.fakeopen.files[self.name][self.pos : self.pos + len(s)] = list(s)
        self.pos += len(s)

class FakeOpen:
    """A fake file system. Used for testing."""

    def __init__(self, initial = {}):
        self.files = {}
        for key, value in initial.items():
            self.files[key] = list(value)
    
    def open(self, filename, mode):
        """currently treats everything as rw - doesn't support append"""
        self.files.setdefault(filename, [])
        return FakeHandle(filename, self)

    def exists(self, file):
        return self.files.has_key(file)

    def getsize(self, file):
        return len(self.files[file])

def test_normal():
    f = FakeOpen({'f1': 'abcde'})
    assert f.exists('f1')
    assert not f.exists('f2')
    assert f.getsize('f1') == 5
    h = f.open('f1', 'rw')
    assert h.read(3) == 'abc'
    assert h.read(1) == 'd'
    assert h.read() == 'e'
    assert h.read(2) == ''
    h.write('fpq')
    h.seek(4)
    assert h.read(2) == 'ef'
    h.write('ghij')
    h.seek(0)
    assert h.read() == 'abcdefghij'
    h.seek(2)
    h.write('p')
    h.write('q')
    assert h.read(1) == 'e'
    h.seek(1)
    assert h.read(5) == 'bpqef'

    h2 = f.open('f2', 'rw')
    assert h2.read() == ''
    h2.write('mnop')
    h2.seek(1)
    assert h2.read() == 'nop'
    
    assert f.exists('f1')
    assert f.exists('f2')
    assert f.getsize('f1') == 10
    assert f.getsize('f2') == 4
