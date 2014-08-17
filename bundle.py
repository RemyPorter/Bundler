from pyparsing import *
import os.path as path
from collections import namedtuple
import collections

Entry = namedtuple("Entry", "description path")

ENTRY = Combine(quotedString("Description") + Suppress(",") + restOfLine("Path"))("entry").setParseAction(lambda x: Entry(x.entry.Description.replace('"',""), x.entry.Path))
BUNDLE = ZeroOrMore(ENTRY)

def loadguard(function):
	def wrapper(*args, **kwargs):
		if not args[0].loaded:
			args[0].load()
		return function(*args, **kwargs)
	return wrapper

class Bundle(collections.Iterable):
	def __init__(self, bundleFile):
		self.bundleFile = bundleFile
		self.__loaded = False
		self.__lines = []

	def load(self):
		self.__lines = BUNDLE.parseFile(self.bundleFile)

	@property
	def loaded(self):
		return self.__loaded

	@loadguard
	def __getitem__(self, item):
		return self.__lines[item]

	@loadguard
	def __setitem__(self, item, value):
		self.__lines[item] = value

	@loadguard
	def __iter__(self):
		for i in self.__lines:
			yield i

	@loadguard
	def append(self, item):
		self.__lines += [item]

	@loadguard
	def prepend(self, item):
		self.__lines = [item] + self.__lines

	def __entrystring(self, entry):
		return '"{0.description}",{0.path}'.format(entry)

	def write(self):
		with open(self.bundleFile, "w") as output:
			for l in self.__lines:
				output.write(self.__entrystring(l))

class BundleProcessor:
	def __init__(self, bundle):
		self.__bundle = bundle

	def __get(self, path):
		try:
			with open(path) as file:
				for l in file:
					yield l
		except Error as err:
			print("Failed to open file: {0}".format(err))

	def merge_to(self, output_path):
		with open(output_path, "w") as output:
			for input in self.__bundle:
				output.write("# {0}\n".format(input.description))
				for line in self.__get(input.path):
					output.write(line + "\n")