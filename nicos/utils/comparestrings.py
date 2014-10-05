#
# (C) 2005, Rob W. W. Hooft (rob@hooft.net)
#
# Comparison algorithm as implemented by Reinhard Schneider and Chris Sander
# for comparison of protein sequences, but implemented to compare two
# ASCII strings. This can be very useful for command interpreters to account
# for mistyped commands (use the routine "compare(s1, s2)" in here to get
# a score for each possible command, and see if one stands out). The comparison
# makes use of a similarity matrix for letters: in the protein case this is
# normally a chemical functionality similarity, for our case this is a matrix
# based on keys next to each other on a US Qwerty keyboard and on "capital
# letters are similar to their lowercase equivalent"
#
# The algorithm does not cut corners: it is sure to find the absolute best
# match between the two strings.
#
# No attempt has been made to make this efficient in time or memory. Time taken
# and memory used is proportional to the product of the length of the input
# strings. Use for strings longer than 25 characters is entirely for your own
# risk.
#
# Use freely, but please attribute when using.
# from http://starship.python.net/crew/hooft/

from __future__ import print_function


# How much does it cost to make a hole in one of the strings?
GAPOPENPENALTY = -0.3
# How much does it cost to elongate a hole in one of the strings?
GAPELONGATIONPENALTY = -0.2
# How much alike (0.0-1.0) are small and capital letters?
CAPITALIZESCORE = 0.8
# How much alike (0.0-1.0) are characters next to each other on a (US) keyboard?
NEXTKEYSCORE = 0.6

comparematrix = {}


def _makekeyboardmap():
    # different characters score 0.0, equal characters score 1.0
    for i in range(33, 126 + 1):
        for j in range(33, 126 + 1):
            comparematrix[i, j] = 0.0
        comparematrix[i, i] = 1.0
    # Capital and small letters are CAPITALIZESCORE alike
    capdist = ord('A') - ord('a')
    for i in range(ord('a'), ord('z') + 1):
        comparematrix[i, i + capdist] = CAPITALIZESCORE
        comparematrix[i + capdist, i] = CAPITALIZESCORE

    # Keyboard layout, add some score for letters that are close together
    line1 = '`1234567890-= '
    line2 = ' qwertyuiop[] '
    line3 = ' asdfghjkl;   '
    line4 = ' zxcvbnm,./   '
    for i in range(len(line1) - 1):
        _keyboardneighbour(line1[i], line1[i + 1])
        _keyboardneighbour(line2[i], line2[i + 1])
        _keyboardneighbour(line3[i], line3[i + 1])
        _keyboardneighbour(line4[i], line4[i + 1])
        _keyboardneighbour(line1[i], line2[i])
        _keyboardneighbour(line2[i], line3[i])
        _keyboardneighbour(line3[i], line4[i])
        _keyboardneighbour(line1[i], line2[i + 1])
        _keyboardneighbour(line2[i], line3[i + 1])
        _keyboardneighbour(line3[i], line4[i + 1])


def _keyboardneighbour(c1, c2):
    i1 = ord(c1)
    i2 = ord(c2)
    if 33 <= i1 <= 126 and 33 <= i2 <= 126:
        comparematrix[i1, i2] = NEXTKEYSCORE
        comparematrix[i2, i1] = NEXTKEYSCORE

_makekeyboardmap()


def compare(s1, s2):
    lh = {}
    gapped = {}

    l1 = len(s1)
    l2 = len(s2)

    if s1 == s2:
        return l1 + 1

    # Top left of the matrix is "before the first character" in both directions
    lh[1, 1] = 0.0
    gapped[1, 1] = False

    # Start with a gap in s1
    lh[2, 1] = GAPOPENPENALTY
    gapped[2, 1] = True

    for ii in range(3, l1 + 2):
        lh[ii, 1] = lh[ii - 1, 1] + GAPELONGATIONPENALTY
        gapped[ii, 1] = True

    # Start with a gap in s2
    lh[1, 2] = GAPOPENPENALTY
    gapped[1, 2] = True

    for jj in range(3, l2 + 2):
        lh[1, jj] = lh[1, jj - 1] + GAPELONGATIONPENALTY
        gapped[1, jj] = True

    # The main algorithm: for each point in the matrix decide what the best
    # route so far is, by comparing the diagonal route forward with the
    # possibility to open or elongate a gap either way.
    for jj in range(1, l2 + 1):
        for ii in range(1, l1 + 1):
            oc1 = ord(s1[ii - 1])
            oc2 = ord(s2[jj - 1])
            if 33 <= oc1 <= 126 and 33 <= oc2 <= 126:
                ld = comparematrix[oc1, oc2]
            elif oc1 == oc2:
                ld = 1.0
            else:
                ld = 0.0

            if gapped[ii + 1, jj]:
                gph = GAPELONGATIONPENALTY
            else:
                gph = GAPOPENPENALTY

            if gapped[ii, jj + 1]:
                gpv = GAPELONGATIONPENALTY
            else:
                gpv = GAPOPENPENALTY

            s = lh[ii, jj] + ld
            sh = lh[ii + 1, jj] + gph
            sv = lh[ii, jj + 1] + gpv
            sd = max(sh, sv)
            if s >= sd:
                lh[ii + 1, jj + 1] = s
                gapped[ii + 1, jj + 1] = False
            else:
                lh[ii + 1, jj + 1] = sd
                gapped[ii + 1, jj + 1] = True
    # The highest alignment score is in the bottom right corner of the matrix,
    # behind the last character in both strings
    return lh[l1 + 1, l2 + 1]


def test():
    assert compare("test", "test") == len("test") + 1.0
    assert compare("Test", "test") == len("test") - 1.0 + CAPITALIZESCORE
    assert compare("rest", "test") == len("test") - 1.0 + NEXTKEYSCORE
    assert compare("rest", "crest") == len("rest") + GAPOPENPENALTY
