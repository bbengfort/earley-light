#!/usr/bin/env python

# nlp.homework2.parse
#
# Author:    Benjamin Bengfort <benben1@umbc.edu>
# Date:      Sat Nov 27 19:21:54 2012 -0400
# Objective: Submission as Homework 2 for CS 5263
#
# ID: parse.py [4] benjamin@bengfort.com $

"""
A command line helper for executing parse commands.
"""

import os
import sys
import traceback

from earley import *
from optparse import make_option, OptionParser

class ConsoleError(Exception):
    """
    An exception in the console command.
    """
    pass

class ConsoleProgram(object):
    """
    A utility for executing console programs.
    """

    opts = (
        make_option("-g", "--grammar", action="store", default=None, metavar="PATH",
            help="Specify the grammar file to use, the default is knowledge/nounphrases.cfg"),
        make_option("-l", "--lexicon", action="store", default=None, metavar="PATH",
            help="Specify the lexicon file to use, the default is knowledge/lexicon.data"),
        make_option("--traceback", action="store_true",
            help="Print traceback on exception"),
    )

    help = "Pass a sentence to parse on the command line."
    args = "\"A quote delimmited sentence\""

    version = ("1", "0", "0")

    def get_version(self):
        if self.version:
            return '.'.join(self.version)
        return "unknown"

    @property 
    def usage(self):
        usage = "%%prog [options] %s" % self.args
        if self.help:
            return "%s\n\n%s" % (usage, self.help)
        return usage

    def create_parser(self, prog_name):
        """
        Create and return the OptionParser which will be used
        to parse the arguments to the command.
        """
        opkw = {
            'prog':        prog_name,
            'usage':       self.usage,
            'version':     self.get_version( ),
            'option_list': self.opts,
        }
        return OptionParser(**opkw)
    
    def print_help(self, prog_name):
        """
        Print the help message for this command, from self.usage( )
        """
        parser = self.create_parser(prog_name)
        parser.print_help( )

    def load(self, argv):
        """
        Setup the environment, either Python or Django,
        then run this command.
        """
        parser = self.create_parser(argv[0])
        opts, args = parser.parse_args(argv[1:])
        self.execute(*args, **opts.__dict__)

    def execute(self, *args, **opts):
        """
        Try to execute this command.
        """
        show_traceback = opts.get('traceback', False)

        try:
            self.stdout = opts.get('stdout', sys.stdout)
            self.stderr = opts.get('stderr', sys.stderr)

            output = self.handle(*args, **opts)

            if output:
                self.stdout.write(output)
        except ConsoleError, e:
            if show_traceback:
                traceback.print_exc()
            else:
                self.stderr.write('Error: %s\n' % e)
            sys.exit(1)

    def handle(self, *args, **opts):
        
        if len(args) != 1:
            raise ConsoleError("Please specify a phrase to parse in quotes.")

        phrase = args[0]

        cfgpath = opts.get("grammar", None) or CFGPATH
        lexpath = opts.get("lexicon", None) or LEXPATH

        print cfgpath
        print lexpath

        parser = get_default_parser(cfgpath, lexpath)

        try:
            chart, parses = parser.parse(phrase)

            print parser
            print

            if len(parses) > 0:
                print "Successful Parses:"
                for state in parses:
                    print_tree(state.tree)
                
            else:
                raise ConsoleError("The input is ungrammatical.")

        except ParseError as e:
            raise ConsoleError("Parse Error: %s" % str(e))
        except LexicalError as e:
            raise ConsoleError("Lexical Error: %s" % str(e))
        except GrammarError as e:
            raise ConsoleError("Grammar Error: %s" % str(e))

if __name__ == "__main__":
    ConsoleProgram().load(sys.argv)
