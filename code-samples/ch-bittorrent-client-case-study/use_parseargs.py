from parseargs import parseargs

opts, args = parseargs(('arg1 --opt1 val1 arg2'.split()),
    (('opt1', 'default1', ''), ('opt2', 'default2', '')))
print 'opts=%s' % opts
print 'args=%s' % args

