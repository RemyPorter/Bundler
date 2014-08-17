from pyparsing import *
import os.path as path

ENTRY = Combine(QuotedString("Description") + restOfLine("Path"))("entry")
SECTION = Suppress("#") + restOfLine("Section")
SEGMENT = Optional(SECTION) + OneOrMore(ENTRY)
BUNDLE = OneOrMore(SEGMENT)