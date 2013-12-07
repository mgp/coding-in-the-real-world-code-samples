from PiecePicker import PiecePicker

picker = PiecePicker(3, rarest_first_cutoff=0)
# Three peers have piece 0.
picker.got_have(0)
picker.got_have(0)
picker.got_have(0)
# Only one peer has piece 1.
picker.got_have(1)
# Two peers have piece 2.
picker.got_have(2)
picker.got_have(2)

# Return the piece to download from a seed.
seed_have_func = lambda index: True
print 'rarest piece from seed: %s' % picker.next(seed_have_func)
# Return the piece to download from a peer missing piece 1.
peer_have_func = lambda index: index != 1
print 'rarest piece from peer: %s' % picker.next(peer_have_func)

