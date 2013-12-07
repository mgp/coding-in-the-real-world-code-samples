from bitfield import Bitfield

bitfield = Bitfield(8, '\xee')
print 'value={0:b} complete={1}'.format(ord(bitfield.tostring()), bitfield.complete())
bitfield[3] = True
bitfield[7] = True
print 'value={0:b} complete={1}'.format(ord(bitfield.tostring()), bitfield.complete())

