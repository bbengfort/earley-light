# nlp.homework2.grammar
#
# Author:    Benjamin Bengfort <benben1@umbc.edu>
# Date:      Tue Nov 27 11:23:12 2012 -0400
# Objective: Submission as Homework 2 for CS 5263
#
# ID: grammar.py [4] benjamin@bengfort.com $

"""
Creates a context free grammar object that is parsed from a CFG file. The
grammar acts as a dictionary wrapper for the RHS and a list of Production
objects as the LHS.
"""

import os
import re

class GrammarError(Exception):
    """
    A generic class for raising grammar exceptions.
    """
    pass

class Production(object):
    """
    A datastructure for a unit production with a RHS and a LHS
    """

    def __init__(self, lhs, rhs):
        
        
        self.lhs = lhs

        if isinstance(rhs, tuple):
            self.rhs = rhs
        elif isinstance(rhs, list):
            self.rhs = tuple(rhs)
        else:
            if '|' in rhs:
                raise GrammerError("Productions must be unit productions only (no \"|\").")
            self.rhs = tuple([term.strip() for term in rhs.split(' ')])

    def __repr__(self):
        return "%s -> %s" % (self.lhs, ' '.join(self.rhs))

    def __str__(self):
        return ' '.join(self.rhs)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.lhs == other
        else:
            return self.lhs == other.lhs

    def __hash__(self):
        return hash(self.lhs)

class Grammar(object):
    """
    A dictionary for loading a context free grammar from a file and
    parsing the constructions contained within it. Grammars are expected
    to take the form RHS -> LHS, where the RHS contains a single non-
    terminal symobl, and the LHS contains a series of pipe delimitted 
    constructions that make up the RHS. 
    """

    @classmethod
    def parse(klass, path):
        """
        When passed a path, opens a descriptor to the cfg file and parses
        the data, loading it into the grammar. The grammer should be
        formatted as follows:

        RHS -> LHS

        Where LHS can be of either form

        NT or NT NT ... or NT NT | NT | NT ... etc.

        Comments begin with # -- anything on the line after # is ignored.
        """
        rule  = re.compile(r'^([\w\-]+)\s+->\s+([\w\-\s\|]+)#?(.*)$')
        pcfg  = klass()
        try:
            with open(path, 'rb') as cfg:
                for line in cfg.readlines():
                    line = line.strip()
                    # Ignore commented or empty lines
                    if not line or line.startswith('#'): continue

                    match = rule.match(line)
                    if not match:
                        raise GrammarError("Problem parsing: %s" % line)
                    else:
                        lhs = match.groups()[0]
                        rhs = match.groups()[1]

                        for term in rhs.split('|'):
                            prod = Production(lhs, term.strip())
                            pcfg[prod] = prod

            return pcfg
        except IOError as e:
            raise GrammarError("Could not open grammar:\n%s" % str(e))

    def __init__(self, **productions):
        """
        A dictionary of productions can be passed into the constructor in
        order to preload the grammar. This will pass all items through the
        setitem mechanism to ensure that proper data is being loaded.
        """
        self.__productions = {}

        for k,v in productions.items():
            self[k] = v

    def __len__(self):
        """
        Returns the number of productions in the grammar.
        """
        return sum([len(production[1]) for production in self])

    def __getitem__(self, lhs):
        """
        Fetches the list of productions if the LHS
        raises GrammarError instead of KeyError
        """
        if lhs in self:
            return self.__productions[lhs]
        else:
            raise GrammarError("No production with the LHS \"%s\"" % lhs)

    def __setitem__(self, rhs, lhs):
        """
        Extends the LHS if the LHS is a list, otherwise it appends it.
        """
        if rhs in self:
            if isinstance(lhs, list):
                self.__productions[rhs].extend(lhs)
            else:
                self[rhs].append(lhs)
        else:
            if isinstance(lhs, list):
                self.__productions[rhs] = lhs
            else:
                self.__productions[rhs] = [lhs,]

    def __delitem__(self, rhs):
        """
        Deletes all productions for a RHS!
        """
        del self.__productions[rhs]

    def __contains__(self, rhs):
        """
        Membership test.
        """
        return rhs in self.__productions

    def __iter__(self):
        """
        Iteration
        """
        for item in self.__productions.items():
            yield item

    def __str__(self):
        """
        String value of Grammar
        """
        return "\n".join(["%s -> %s" % (item[0].lhs, ' | '.join([str(prod) for prod in item[1]])) for item in self])

    def keys(self):
        """
        Return all the Left-Hand Sides contained in the grammar.
        """
        return self.__productions.keys()
   
    def values(self):
        """
        Return lists of productions belonging to the same Right-Hand Side
        """
        return self.__productions.values()

    def productions(self):
        """
        Return all the Productions contained in the grammar.
        """
        for value in self.values():
            for production in value:
                yield production

    def nonterms(self):
        """
        Returns a list of the non-terminal and preterminals in the grammar.
        """
        nonterms = []
        for production in self.productions():
            nonterms.append(production.lhs)
            for symbol in production.rhs:
                nonterms.append(symbol)
        return set(nonterms)

    def isGrammatical(self, term):
        return term in self.nonterms()

if __name__ == "__main__":

    cfg = Grammar.parse("../knowledge/nounphrases.cfg")
    print cfg
