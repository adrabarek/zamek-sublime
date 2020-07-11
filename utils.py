import os

class cd:
		# A convenience class for changing working directory for a single
		# scope.

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def split_line(line):
	return list(filter(lambda x: x != "", [x.strip() for x in line.split(',')]))

def split_list(prefix, text_lines):
	# Checks text_lines for line in form "prefix: a, b, c"
	# If found, returns ["a", "b", "c"].

	for line in text_lines:
		split = line.split(':')
		if split[0] == prefix:
			l = split_line(split[1])
			return l

	return []

class FilePath:
	# Helper class storing various formats of a file path.

	def __init__(self, path):
		self.path = path
		self.base_name = os.path.basename(path)
		# todo: os.path.splitext
		split = self.base_name.split('.')
		self.no_extension = split[0]
		self.extension = ""
		if len(split) > 1:
			self.extension = split[1]