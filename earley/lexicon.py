# nlp.homework2.lexicon
#
# Author:    Benjamin Bengfort <benben1@umbc.edu>
# Date:      Tue Nov 27 15:59:42 2012 -0400
# Objective: Submission as Homework 2 for CS 5263
#
# ID: lexicon.py [4] benjamin@bengfort.com $

import re

class LexicalError(Exception):
    """
    Generic class for lexical errors.
    """
    pass

class Lexicon(object):
    """
    A datastructure for lexical entries.
    """

    @classmethod
    def parse(klass, path):
        """
        Reads a lexical file from the path and instantiates a lexicon.

        The lexical file should be of the form:
            word   PoS-Tag

        Where the word (or token) cannot have spaces on it, and is white
        space separated from its part of speech tag.
        """
        words  = {}
        define = re.compile(r'^([\w\-]+)\s+([\w\-]+)\s*#?(.*)$')
        try:
            with open(path, 'rb') as lexfile:
                for line in lexfile.readlines():
                    line = line.strip()

                    # Ignore comments and empty lines
                    if not line or line.startswith('#'): continue

                    match = define.match(line)
                    if not match:
                        raise LexicalError("Problem parsing: %s" % line)
                    else:
                        word  = match.groups()[0]
                        gloss = match.groups()[1]
                        words[word] = gloss
            return klass(**words)
        except IOError as e:
            raise LexicalError("Could not open lexicon:\n%s" % str(e))

    def __init__(self, **words):
        
        self.__words = {}

        for word, gloss in words.items():
            self[word] = gloss

    def __len__(self):
        return len(self.words())

    def __getitem__(self, word):
        if word in self:
            return self.__words[word]
        raise LexicalError("The word '%s' is not in the lexicon." % word)
    
    def __setitem__(self, word, gloss):
        self.__words[word] = gloss

    def __delitem__(self, word):
        del self.__words[word]

    def __contains__(self, word):
        return word in self.__words

    def __iter__(self):
        for item in self.__words.items():
            yield item

    def words(self):
        return self.__words.keys()

    def preterminals(self):
        return set(self.__words.values())

    def isLexical(self, term):
        return term in self.words()

if __name__ == "__main__":

    lexicon = Lexicon.parse("../knowledge/lexicon.data")
    for definition in lexicon:
        print "%s: %s" % definition
