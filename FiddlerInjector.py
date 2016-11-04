import sublime, sublime_plugin, os, locale, sys, re
from xml.dom import minidom

def get_setting(key, default=None):
	settings = sublime.load_settings('FiddlerInjector.sublime-settings')
	os_specific_settings = {}
	if os.name == 'nt':
		os_specific_settings = sublime.load_settings('Terminal (Windows).sublime-settings')
	elif os.name == 'darwin':
		os_specific_settings = sublime.load_settings('Terminal (OSX).sublime-settings')
	else:
		os_specific_settings = sublime.load_settings('Terminal (Linux).sublime-settings')
	return os_specific_settings.get(key, settings.get(key, default))

class NotFoundError(Exception):
    pass

class FiddlerInjectorCommand():

	def get_path(self, paths):
		if paths:
			return paths[0]
		# DEV: On ST3, there is always an active view.
		#   Be sure to check that it's a file with a path (not temporary view)
		elif self.window.active_view() and self.window.active_view().file_name():
			return self.window.active_view().file_name()
		elif self.window.folders():
			return self.window.folders()[0]
		else:
			sublime.error_message('Terminal: No place to open terminal to')
			return False
	def appendFiles(self, arr, path):
		for content in os.listdir(path):
			if(self.validateFiles(content)):
				arr.append(content)

	def validateFiles(self, file):
		settings = sublime.load_settings('FiddlerInjector.sublime-settings')

		if re.match(settings.get('ignore'), file, flags=0):
			return False
		if re.match(settings.get('append'), file, flags=0):
			return True

		return False
	def generateXMLstr(self, files):
		doc = minidom.Document()
		root = doc.createElement('root')
		doc.appendChild(root)

	def create_fiddler(self, path,  parameters):

		try:
			if not path:
				raise NotFoundError('The file open in the selected view has ' +
				'not yet been saved')
			for k, v in enumerate(parameters):
				parameters[k] = v.replace('%CWD%', path)

			args = []
			files = []
			settings = sublime.load_settings('FiddlerInjector.sublime-settings')
			if os.path.isfile(path):
				files.append(path)
			else:
				self.appendFiles(files, path)

			args.extend(parameters)
			ignore = settings.get('files')
			sublime.message_dialog('<::::::jol::::>'.join(files))
			self.generateXMLstr(files)
		except (Exception) as exception:
			sublime.error_message('FiddlerInjector: ' + str(exception))

class FileFiddlerInjectorCommand(sublime_plugin.WindowCommand, FiddlerInjectorCommand):
	def run(self, paths=[], parameters=None):
		path = self.get_path(paths)
		if not path:
			return

		if parameters is None:
			parameters = get_setting('parameters', [])
		self.create_fiddler(path, parameters)