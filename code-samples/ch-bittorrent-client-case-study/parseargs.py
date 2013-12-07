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

# Written by Bill Bumgarner and Bram Cohen
# Comments added by Michael Parker

from types import *
from cStringIO import StringIO

def formatDefinitions(options, COLS):
    s = StringIO()
    indent = " " * 10
    width = COLS - 11

    if width < 15:
        width = COLS - 2
        indent = " "

    for (longname, default, doc) in options:
        s.write('--' + longname + ' <arg>\n')
        if default is not None:
            doc += ' (defaults to ' + repr(default) + ')'
        i = 0
        for word in doc.split():
            if i == 0:
                s.write(indent + word)
                i = len(word)
            elif i + len(word) >= width:
                s.write('\n' + indent + word)
                i = len(word)
            else:
                s.write(' ' + word)
                i += len(word) + 1
        s.write('\n\n')
    return s.getvalue()

def usage(str):
    raise ValueError(str)

def parseargs(argv, options, minargs = None, maxargs = None):
    # The command-line options parsed from argv.
    config = {}
    longkeyed = {}
    for option in options:
        longname, default, doc = option
        longkeyed[longname] = option
        # Populate the returned options with the default values passed in.
        config[longname] = default
    options = []
    # The command-line arguments parsed from argv.
    args = []
    pos = 0
    while pos < len(argv):
        if argv[pos][:2] != '--':
            # This is an argument, not an option.
            args.append(argv[pos])
            pos += 1
        else:
            # This is an option, not an argument.
            if pos == len(argv) - 1:
                usage('parameter passed in at end with no value')
            key, value = argv[pos][2:], argv[pos+1]
            pos += 2
            if not longkeyed.has_key(key):
                # This is an unrecognized option.
                usage('unknown key --' + key)
            longname, default, doc = longkeyed[key]
            try:
                # Convert the option to the type of its default value.
                t = type(config[longname])
                if t is NoneType or t is StringType:
                    config[longname] = value
                elif t in (IntType, LongType):
                    config[longname] = long(value)
                elif t is FloatType:
                    config[longname] = float(value)
                else:
                    assert 0
            except ValueError, e:
                usage('wrong format of --%s - %s' % (key, str(e)))
    # Ensure that all required arguments, which have no default values, are provided.
    for key, value in config.items():
        if value is None:
            usage("Option --%s is required." % key)
    # Ensure that neither too few nor too many arguments were provided.
    if minargs is not None and len(args) < minargs:
        usage("Must supply at least %d args." % minargs)
    if maxargs is not None and len(args) > maxargs:
        usage("Too many args - %d max." % maxargs)
    # Return the parsed options and arguments.
    return (config, args)

def test_parseargs():
    assert parseargs(('d', '--a', 'pq', 'e', '--b', '3', '--c', '4.5', 'f'), (('a', 'x', ''), ('b', 1, ''), ('c', 2.3, ''))) == ({'a': 'pq', 'b': 3, 'c': 4.5}, ['d', 'e', 'f'])
    assert parseargs([], [('a', 'x', '')]) == ({'a': 'x'}, [])
    assert parseargs(['--a', 'x', '--a', 'y'], [('a', '', '')]) == ({'a': 'y'}, [])
    try:
        parseargs([], [('a', 'x', '')])
    except ValueError:
        pass
    try:
        parseargs(['--a', 'x'], [])
    except ValueError:
        pass
    try:
        parseargs(['--a'], [('a', 'x', '')])
    except ValueError:
        pass
    try:
        parseargs([], [], 1, 2)
    except ValueError:
        pass
    assert parseargs(['x'], [], 1, 2) == ({}, ['x'])
    assert parseargs(['x', 'y'], [], 1, 2) == ({}, ['x', 'y'])
    try:
        parseargs(['x', 'y', 'z'], [], 1, 2)
    except ValueError:
        pass
    try:
        parseargs(['--a', '2.0'], [('a', 3, '')])
    except ValueError:
        pass
    try:
        parseargs(['--a', 'z'], [('a', 2.1, '')])
    except ValueError:
        pass

