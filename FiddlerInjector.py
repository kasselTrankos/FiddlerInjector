import sublime, sublime_plugin, os, locale, sys, re
from xml.dom import minidom
from xml.etree import ElementTree
import ntpath
import subprocess
from subprocess import Popen, PIPE, STDOUT
from sys import version_info
import datetime

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

	def getCnt_cgt_info(self, path):
		parts = os.path.normpath(path)
		paths = parts.split(os.sep)
		isCGT = False
		name = ''
		for path_ in paths:
			if re.match('^cgt-', path_, flags=0) :
				isCGT = True
				name = path_.split('-', 1)[1]
			if re.match('^cnt-', path_, flags=0):
				name = path_.split('-', 2)[1]

		return [isCGT, name[0].lower() + name[1:]]


	def appendFiles(self, arr, path):
		for content in os.listdir(path):
			if(self.validateFiles(content)):
				arr.append(content)
		sublime.message_dialog('<::::::FILES IS::::>'.join(arr)+'----')
	def validateFiles(self, file):
		settings = sublime.load_settings('FiddlerInjector.sublime-settings')

		if re.match(settings.get('ignore'), file, flags=0):
			return False
		if re.match(settings.get('append'), file, flags=0):
			return True

		return False
	def get_file_name(self, path):
		head, tail = ntpath.split(path)
		return tail or ntpath.basename(head)

	def generateXMLstr(self, files, cntName, isCGT, cgtName, path):
		settings = sublime.load_settings('FiddlerInjector.sublime-settings')

		doc = minidom.Document()
		doc.toprettyxml(encoding="utf-8")
		root = doc.createElement('AutoResponder')
		root.setAttribute('FiddlerVersion', '4.6.3.44034')
		root.setAttribute('LastSave', 'hol')
		state = doc.createElement('State')
		state.setAttribute('Enabled', 'true')
		state.setAttribute('Fallthrough', 'true')
		state.setAttribute('UseLatency', 'true')
		root.appendChild(state)
		doc.appendChild(root)
		for file in files:
			regexMatch = []
			origPath = []
			origPath.append(path)
			origPath.append('\\')
			origPath.append(file)
			regexMatch.append('EXACT:http://')
			regexMatch.append(settings.get('DOMAIN'))
			regexMatch.append(':')
			regexMatch.append(settings.get('PORT'))
			regexMatch.append('/')
			regexMatch.append(cntName)
			regexMatch.append('/')
			if(isCGT):
				regexMatch.append('cgt')
				regexMatch.append('/')
				regexMatch.append(cgtName)
			regexMatch.append('/')
			regexMatch.append(self.get_file_name(file))
			tempChild = doc.createElement('ResponseRule')
			tempChild.setAttribute('Enabled', 'true')
			tempChild.setAttribute('Match', ''.join(regexMatch))
			tempChild.setAttribute('Action', ''.join(origPath))

			state.appendChild(tempChild)
		sublime.message_dialog('<::::::jol::::>'+doc.toxml()+'----')
		return doc
	def create_fiddler(self, path,  parameters, cntName, isCGT, cgtName):

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
			sublime.message_dialog('<::::::jol::::>'.join(files)+'----')
			xml = self.generateXMLstr(files, cntName, isCGT, cgtName, path)
			nameXML = []
			nameXML.append(settings.get('saveOn'))
			nameXML.append('\\')
			if(isCGT):
				nameXML.append('cgt-')
				nameXML.append(cgtName)
			else:
				nameXML.append('cnt-')
				nameXML.append(cntName)
			nameXML.append('.farx')
			xml.writexml(open(''.join(nameXML), 'w', encoding='utf8'),
               encoding='utf-8',
               newl='\n')
		except (Exception) as exception:
			sublime.error_message('FiddlerInjector: ' + str(exception))

class FileFiddlerInjectorCommand(sublime_plugin.WindowCommand, FiddlerInjectorCommand):
	def run(self, paths=[], parameters=None):
		sublime.message_dialog('<::::::jol::::>'+paths[0]+'----')
		isCGT, name = self.getCnt_cgt_info(paths[0])
		fname = self.window.active_view().file_name()
		if fname == None:
			fname = ""
		if isCGT:
			sublime.message_dialog('<::::::jol::::>CGT----')
		else:
			sublime.message_dialog('<::::::jol::::>CNT----')
		def done(cntName):
				self.create_fiddler(paths[0], parameters, cntName, isCGT, name)
		if parameters is None:
			parameters = get_setting('parameters', [])

		if(isCGT):
			self.window.show_input_panel(
            "Name of CNT is: ", fname, done, None, None)
		else:
			self.create_fiddler(paths[0], parameters, name, isCGT, name)






