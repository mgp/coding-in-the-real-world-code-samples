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
# Comments added by Michael Parker

from random import randrange, shuffle, choice

class PiecePicker:
    def __init__(self, numpieces, rarest_first_cutoff = 1):
        self.rarest_first_cutoff = rarest_first_cutoff
        # The number of pieces.
        self.numpieces = numpieces
        # The availability of each piece.
        # Element interests[i] is an array of all pieces with availability i.
        self.interests = [range(numpieces)]
        # If a piece has availability i, specifies its index in interests[i].
        self.pos_in_interests = range(numpieces)
        # The availability of each piece.
        self.numinterests = [0] * numpieces
        # Any pieces that we have requested from anyone.
        self.started = []
        # Any pieces that we have requested from a seed.
        self.seedstarted = []
        # The number of completed pieces.
        self.numgot = 0
        # All pieces randomly ordered.
        self.scrambled = range(numpieces)
        shuffle(self.scrambled)

    def got_have(self, piece):
        if self.numinterests[piece] is None:
            # This piece is complete.
            return
        # Decrement the availability of this piece.
        numint = self.numinterests[piece]
        if numint == len(self.interests) - 1:
            self.interests.append([])
        self.numinterests[piece] += 1
        # Update interests and pos_in_interests for this piece.
        self._shift_over(piece, self.interests[numint], self.interests[numint + 1])

    def lost_have(self, piece):
        if self.numinterests[piece] is None:
            # This piece is complete.
            return
        # Increment the availability of this piece.
        numint = self.numinterests[piece]
        self.numinterests[piece] -= 1
        # Update interests and pos_in_interests for this piece.
        self._shift_over(piece, self.interests[numint], self.interests[numint - 1])

    def _shift_over(self, piece, l1, l2):
        # Move the piece from l1 to l2, which are arrays in interests.
        # This finishes either incrementing or decrementing its availability.
        p = self.pos_in_interests[piece]
        l1[p] = l1[-1]
        self.pos_in_interests[l1[-1]] = p
        del l1[-1]
        newp = randrange(len(l2) + 1)
        if newp == len(l2):
            # Moving the piece to the end of l2.
            self.pos_in_interests[piece] = len(l2)
            l2.append(piece)
        else:
            # Moving the piece before the end of l2, replacing an existing piece.
            # Move that piece to the end first.
            old = l2[newp]
            self.pos_in_interests[old] = len(l2)
            l2.append(old)
            # The piece now takes its position.
            l2[newp] = piece
            self.pos_in_interests[piece] = newp

    def requested(self, piece, seed = False):
        if piece not in self.started:
            # We have requested this piece from another client.
            self.started.append(piece)
        if seed and piece not in self.seedstarted:
            # We have requestd this piece from a seed.
            self.seedstarted.append(piece)

    def complete(self, piece):
        assert self.numinterests[piece] is not None
        # Have one more piece.
        self.numgot += 1
        # Remove this piece from whatever array in numinterests.
        l = self.interests[self.numinterests[piece]]
        p = self.pos_in_interests[piece]
        l[p] = l[-1]
        self.pos_in_interests[l[-1]] = p
        del l[-1]
        # Set numinterests element to None to signify that it's done.
        self.numinterests[piece] = None
        try:
            # Not requesting this piece from anyone anymore.
            self.started.remove(piece)
            self.seedstarted.remove(piece)
        except ValueError:
            pass

    def next(self, havefunc, seed = False):
        # The rarest pieces this peer has.
        bests = None
        # The availability of the rarest pieces this peer has.
        bestnum = 2 ** 30
        if seed:
            # Peer is a seed, so choose a pieces that we've already requested from other seeds.
            s = self.seedstarted
        else:
            # Choose from among pieces we've already requested from other peers.
            s = self.started
        for i in s:
            # Find some piece this peer has that we've already requested.
            if havefunc(i):
                if self.numinterests[i] < bestnum:
                    # This piece is rarer than the rarest pieces found so far.
                    bests = [i]
                    bestnum = self.numinterests[i]
                elif self.numinterests[i] == bestnum:
                    # This piece has the same availability as the rarest pieces found so far.
                    bests.append(i)
        if bests:
            # This peer has some piece that we've already requested.
            return choice(bests)
        if self.numgot < self.rarest_first_cutoff:
            # Randomize requests for the first few pieces.
            for i in self.scrambled:
                if havefunc(i):
                    return i
            return None
        for i in xrange(1, min(bestnum, len(self.interests))):
            # Request one of the rarest pieces that this client has not yet requested.
            for j in self.interests[i]:
                if havefunc(j):
                    return j
        return None

    def am_I_complete(self):
        # Return true if we've called completed with each piece.
        return self.numgot == self.numpieces

    def bump(self, piece):
        # Move this piece to the end of its interests array.
        # This demotes its priority, given the append operation, and how next iterates in order.
        l = self.interests[self.numinterests[piece]]
        pos = self.pos_in_interests[piece]
        del l[pos]
        l.append(piece)
        for i in range(pos,len(l)):
            self.pos_in_interests[l[i]] = i


def test_requested():
    p = PiecePicker(9)
    p.complete(8)
    p.got_have(0)
    p.got_have(2)
    p.got_have(4)
    p.got_have(6)
    p.requested(1)
    p.requested(1)
    p.requested(3)
    p.requested(0)
    p.requested(6)
    v = _pull(p)
    assert v[:2] == [1, 3] or v[:2] == [3, 1]
    assert v[2:4] == [0, 6] or v[2:4] == [6, 0]
    assert v[4:] == [2, 4] or v[4:] == [4, 2]

def test_change_interest():
    p = PiecePicker(9)
    p.complete(8)
    p.got_have(0)
    p.got_have(2)
    p.got_have(4)
    p.got_have(6)
    p.lost_have(2)
    p.lost_have(6)
    v = _pull(p)
    assert v == [0, 4] or v == [4, 0]

def test_change_interest2():
    p = PiecePicker(9)
    p.complete(8)
    p.got_have(0)
    p.got_have(2)
    p.got_have(4)
    p.got_have(6)
    p.lost_have(2)
    p.lost_have(6)
    v = _pull(p)
    assert v == [0, 4] or v == [4, 0]

def test_complete():
    p = PiecePicker(1)
    p.got_have(0)
    p.complete(0)
    assert _pull(p) == []
    p.got_have(0)
    p.lost_have(0)

def test_rarer_in_started_takes_priority():
    p = PiecePicker(3)
    p.complete(2)
    p.requested(0)
    p.requested(1)
    p.got_have(1)
    p.got_have(0)
    p.got_have(0)
    assert _pull(p) == [1, 0]

def test_zero():
    assert _pull(PiecePicker(0)) == []

def _pull(pp):
    r = []
    def want(p, r = r):
        return p not in r
    while True:
        n = pp.next(want)
        if n is None:
            break
        r.append(n)
    return r
