import string

PUNCT = ",.!?&@#*()[]{}|"

def unpunct(s):
    return s.translate(string.maketrans("",""), PUNCT)
