from bencode import bencode, bdecode

data = [42, {"username": "mgp"}]
# Convert to bencoded form.
bencoded_data = bencode(data)
print 'bencoded_data=%s' % bencoded_data
# Convert from bencoded form.
bdecoded_data = bdecode(bencoded_data)
print 'bdecoded_data=%s' % bdecoded_data

