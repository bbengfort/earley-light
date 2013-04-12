# -*- coding: utf-8 -*-

# nlp.homework2.earley
#
# Author:    Benjamin Bengfort <benben1@umbc.edu>
# Date:      Wed Nov 28 11:22:38 2012 -0400
# Objective: Submission as Homework 2 for CS 5263
#
# ID: earley.py [4] benjamin@bengfort.com $

"""
Implementation of the Earely algorithm. 
"""

from utils import unpunct
from lexicon import Lexicon, LexicalError
from grammar import Grammar, GrammarError, Production

CFGPATH = "knowledge/nounphrases.cfg"
LEXPATH = "knowledge/lexicon.data"

def get_default_parser(cfgpath=CFGPATH, lexpath=LEXPATH):
    return EarleyParser(Grammar.parse(cfgpath), Lexicon.parse(lexpath))

def print_tree(tree, level=0):
    
    for node in tree:
        if isinstance(node, list):
            print_tree(node, level+1)
        else:
            print "%s%s" % ("    "*level, node)

class ParseError(Exception):
    """
    An object for exceptions in parsing.
    """
    pass

class DottedRule(object):
    """
    A data structure representing a state in Earley parsing.
    """
    
    def __init__(self, subtree, progress, position):
        self.subtree  = subtree
        self.progress = progress
        self.position = position

        self.previous = [ ] # Points to the previous rule that informed this rule.

    def finalized(self, length):
        """
        Returns true if the rule is in the form:
            NP ⟶  rhs ● [0, length]
        To indidcate a successful parse of this rule.
        """
        if self.subtree.lhs == "NP":
            if not self.incomplete():
                if self.position[0] == 0:
                    if self.position[1] == length:
                        return True
        return False

    def incomplete(self):
        """
        Returns False if the progress is > the length of the RHS
        """
        if self.progress >= len(self.subtree.rhs):
            return False
        return True

    def nextcat(self):
        """
        Returns the next part of the subtree, after the progress.
        """
        if self.incomplete():
            return self.subtree.rhs[self.progress]
        return None

    @property
    def tree(self):
        """
        Returns a tree of the previous nodes connected to this rule.
        """
        def expandtree(tree):
            for idx, node in enumerate(tree):
                if isinstance(node, list):
                    expandtree(node)
                    continue

                if node.previous:
                    tree.insert(idx+1, node.previous)

        tree = [self,]
        expandtree(tree)
        return tree

    def __eq__(self, other):
        return (self.subtree.lhs == other.subtree.lhs and 
                self.subtree.rhs == other.subtree.rhs and
                self.progress == other.progress and
                self.position == other.position)

    def __str__(self):
        rhs = list(self.subtree.rhs)
        rhs[self.progress:self.progress] = ["●"]
        return "%s ⟶  %s, [%i, %i]" % (self.subtree.lhs, " ".join(rhs), self.position[0], self.position[1])

class EarleyParser(object):
    
    def __init__(self, grammar, lexicon):
        self.grammar = grammar
        self.lexicon = lexicon

        self.chart   = None
        self.words   = ""

        self.validate()

    @property
    def dummy_state(self):
        """
        Returns a dummy state to start the algorithm.
        """
        gam = Production("⟐", ("NP"))         # This represents GAMMA -> NP
        dot = 0                               # This represents the dot before NP
        pos = [0,0]                           # This represents the position [0,0]

        return DottedRule(gam, dot, pos)

    @property
    def parses(self):
        """
        Looks through the chart to find any successful parses.
        """
        if self.chart and self.words:
            for entry in self.chart:
                for state in entry:
                    if state.finalized(len(self.words)):
                        yield state

    def validate(self):
        """
        Checks to make sure all the symbols in the Lexicon are contained 
        in the Grammar, otherwise words in the lexicon could not be parsed
        """
        preterms = self.lexicon.preterminals()
        nonterms = self.grammar.nonterms()
        if not preterms <= nonterms:
            missing = preterms - nonterms
            raise ParseError(("The non-terminals or preterminals following do "
                             "not exist in the grammar:\n\t'%s'" % "'\n\t'".join(missing)))

    def tokenize(self, string):
        """
        Takes a string, ensures it's all lowercase, removes punctuation,
        then splits on space. returns a list of all the words, along with 
        the part of speech tag from the lexicon. 
        """
        string = string.lower()
        string = unpunct(string)
        tokens = string.split(" ")
        tokens = [(token, self.lexicon[token]) for token in tokens]
        return tokens

    def enqueue(self):
        """
        Resets the chart to the start state.
        """
        return [[self.dummy_state,],]

    def parse(self, string):
        """
        Initiates the parsing of a string and returns the result.
        """
        self.words = self.tokenize(string)
        self.chart = self.enqueue()

        print "Parsing the sequence:\n%s" % self.words
        
        for idx in xrange(0, len(self.words)+1):
            if len(self.chart) == idx: break
            for state in self.chart[idx]:
                #print state
                if state.incomplete():
                    #print "INCOMPLETE"
                    if state.nextcat() in self.grammar:
                        #print "PREDICTING"
                        self.predictor(state)
                    else:
                        #print "SCANNING"
                        self.scanner(state)
                else:
                    #print "COMPLETING"
                    self.completer(state)

        return self.chart, set(list(self.parses))

    def predictor(self, state):
        """
        Implements the Earley Predictor
        """
        idx = state.position[1]
        for rule in self.grammar[state.nextcat()]:
            newtree  = Production(state.nextcat(), rule.rhs)
            newstate = DottedRule(newtree, 0, [idx, idx])

            if newstate not in self.chart[idx]:
                self.chart[idx].append(newstate)

    def scanner(self, state):
        """
        Implements the Earley Scanner
        """
        idx = state.position[1]

        if len(self.words) == idx: return # Make sure we're not trying to scan past the last word

        if state.nextcat() == self.words[idx][1]:
            newtree  = Production(state.nextcat(), (self.words[idx][0],))
            newpos   = [idx, idx + 1]
            newstate = DottedRule(newtree, state.progress+1, newpos)

            if len(self.chart) < idx + 2:
                self.chart.append([])
            if newstate not in self.chart[idx+1]:
                self.chart[idx+1].append(newstate)

    def completer(self, state):
        """
        Implements the Earley Completer
        """
        jdx = state.position[0]
        kdx = state.position[1]

        for cstate in self.chart[jdx]:
            if cstate.nextcat() == state.subtree.lhs:
                idx = cstate.position[0]
                cstate.position = [idx, kdx]
                cstate.progress += 1
                cstate.previous.append(state)
                if cstate not in self.chart[kdx]:
                    self.chart[kdx].append(cstate)

    def __str__(self):
        outstr = []
        if self.chart:
            for idx, states in enumerate(self.chart):
                outstr.append("Chart Entry %i:  %s" % (idx, str(states[0])))
                for state in states[1:]:
                    outstr.append("                %s" % state)
        return "\n".join(outstr)

if __name__ == "__main__":

    try:
        parser = get_default_parser()

        #test = "The beautiful bunnies."
        test = "An airport."

        chart, parses = parser.parse(test)

        print parser
        print

        print len(parses)

        if len(parses) > 0:
            print "Successful Parses:"
            for state in parses:
                print_tree(state.tree)
        else:
            print "The input is ungrammatical."

    except ParseError as e:
        print "Parse Error: %s" % str(e)
    except LexicalError as e:
        print "Lexical Error: %s" % str(e)
    except GrammarError as e:
        print "Grammar Error: %s" % str(e)
