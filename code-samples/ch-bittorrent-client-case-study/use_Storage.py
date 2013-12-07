from fakeopen import FakeOpen
from Storage import Storage

files = (('file_a', 80), ('file_b', 32), ('file_c', 32), ('file_d', 32))
fs = FakeOpen()
storage = Storage(files, fs.open, fs.exists, fs.getsize)
length = 64
print '[0, 64)=%s' % storage._intervals(0 * length, length)
print '[64, 128)=%s' % storage._intervals(1 * length, length)
print '[128, 192)=%s' % storage._intervals(2 * length, length)


import string

# Create 64 bytes of data.
data_length = 64
written_data = string.printable[:data_length]
# Write this data starting at a global offset of 64.
offset = 64
storage.write(offset, written_data)
# Read this data back starting at a global offset of 64.
read_data = storage.read(offset, data_length)
print 'written_data == read_data? %s' % (written_data == read_data)
