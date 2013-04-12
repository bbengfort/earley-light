#!/usr/bin/env python

from earley import *

dev_phrases = (
    "airport runway",
    "The ball",
    "Those bunnies",
    "Some houses",
    "big bunnies",
    "Her big house",
    "The ball which hit the runway",
)

test_phrases = (
    "Four new airports",
    "Very new airport runways",
    "His second house",
    "Some beautiful dishes which a restaurant offered",
    "The runway that the airport built",
)

if __name__ == "__main__":

    try:
        parser = get_default_parser()

        for phrase in dev_phrases:
            chart, parses = parser.parse(phrase)

            if len(parses) > 0:
                print "%s:" % phrase
                for state in parses:
                    print_tree(state.tree)
            else:
                print "    Error: The input is ungrammatical."

            print

    except ParseError as e:
        print "Parse Error: %s" % str(e)
    except LexicalError as e:
        print "Lexical Error: %s" % str(e)
    except GrammarError as e:
        print "Grammar Error: %s" % str(e)
