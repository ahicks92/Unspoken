# Unspoken user interface feedback for NVDA
# By Bryan Smart (bryansmart@bryansmart.com) and Austin Hicks (camlorn38@gmail.com)

import os
import os.path
import sys
import time
import globalPluginHandler
import NVDAObjects
import config
import speech
import controlTypes
import sayAllHandler
import addonGui

sys.path.append(os.path.join(os.path.dirname(__file__),'deps'))

#this is a hack.
#Normally, we would modify Libaudioverse to know about Unspoken and NVDA.
#But if Windows sees a DLL is already loaded, it doesn't reload it.
#To that end, we grab the DLLs out of the Libaudioverse directory here.
#order is important.
import ctypes
file_directory = os.path.split(os.path.abspath(__file__))[0]
libaudioverse_directory = os.path.join(file_directory, 'deps', 'libaudioverse')
dll_hack = [ctypes.cdll.LoadLibrary(os.path.join(libaudioverse_directory, 'libsndfile-1.dll'))]
dll_hack.append(ctypes.cdll.LoadLibrary(os.path.join(libaudioverse_directory, 'libaudioverse.dll')))

import libaudioverse
libaudioverse.initialize()
from . import mixer

UNSPOKEN_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


# Sounds

UNSPOKEN_SOUNDS_PATH = os.path.join(UNSPOKEN_ROOT_PATH, "sounds")

# Associate object roles to sounds.
sound_files={
controlTypes.ROLE_CHECKBOX : "checkbox.wav",
controlTypes.ROLE_RADIOBUTTON : "radiobutton.wav",
controlTypes.ROLE_STATICTEXT : "editabletext.wav",
controlTypes.ROLE_EDITABLETEXT : "editabletext.wav",
controlTypes.ROLE_BUTTON : "button.wav",
controlTypes.ROLE_MENUBAR : "menuitem.wav",
controlTypes.ROLE_MENUITEM : "menuitem.wav",
controlTypes.ROLE_MENU : "menuitem.wav",
controlTypes.ROLE_COMBOBOX : "combobox.wav",
controlTypes.ROLE_LISTITEM : "listitem.wav",
controlTypes.ROLE_GRAPHIC : "icon.wav",
controlTypes.ROLE_LINK : "link.wav",
controlTypes.ROLE_TREEVIEWITEM : "treeviewitem.wav",
controlTypes.ROLE_TAB : "tab.wav",
controlTypes.ROLE_TABCONTROL : "tab.wav",
controlTypes.ROLE_SLIDER : "slider.wav",
controlTypes.ROLE_DROPDOWNBUTTON : "combobox.wav",
controlTypes.ROLE_CLOCK: "clock.wav",
controlTypes.ROLE_ANIMATION : "icon.wav",
controlTypes.ROLE_ICON : "icon.wav",
controlTypes.ROLE_IMAGEMAP : "icon.wav",
controlTypes.ROLE_RADIOMENUITEM : "radiobutton.wav",
controlTypes.ROLE_RICHEDIT : "editabletext.wav",
controlTypes.ROLE_SHAPE : "icon.wav",
controlTypes.ROLE_TEAROFFMENU : "menuitem.wav",
controlTypes.ROLE_TOGGLEBUTTON : "checkbox.wav",
controlTypes.ROLE_CHART : "icon.wav",
controlTypes.ROLE_DIAGRAM : "icon.wav",
controlTypes.ROLE_DIAL : "slider.wav",
controlTypes.ROLE_DROPLIST : "combobox.wav",
controlTypes.ROLE_MENUBUTTON : "button.wav",
controlTypes.ROLE_DROPDOWNBUTTONGRID : "button.wav",
controlTypes.ROLE_HOTKEYFIELD : "editabletext.wav",
controlTypes.ROLE_INDICATOR : "icon.wav",
controlTypes.ROLE_SPINBUTTON : "slider.wav",
controlTypes.ROLE_TREEVIEWBUTTON: "button.wav",
controlTypes.ROLE_DESKTOPICON : "icon.wav",
controlTypes.ROLE_PASSWORDEDIT : "editabletext.wav",
controlTypes.ROLE_CHECKMENUITEM : "checkbox.wav",
controlTypes.ROLE_SPLITBUTTON : "splitbutton.wav",
}

sounds = dict() # For holding instances in RAM.

#taken from Stackoverflow. Don't ask.
def clamp(my_value, min_value, max_value):
	return max(min(my_value, max_value), min_value)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		addonGui.initialize()
		config.conf.spec["unspoken"]={
			"sayAll" : "boolean(default=False)"
		}
		self.simulation = libaudioverse.Simulation(block_size = 1024)
		self.make_sound_objects()
		self.hrtf_panner = libaudioverse.HrtfNode(self.simulation, "default")
		self.hrtf_panner.should_crossfade = False
		self.hrtf_panner.connect_simulation(0)
		# Hook to keep NVDA from announcing roles.
		self._NVDA_getSpeechTextForProperties = speech.getSpeechTextForProperties
		speech.getSpeechTextForProperties = self._hook_getSpeechTextForProperties
		self._previous_mouse_object = None
		self._last_played_object = None
		self._last_played_time = 0
		#these are in degrees.
		self._display_width = 180.0
		self._display_height_min = -40.0
		self._display_height_magnitude = 50.0
		#the mixer feeds us through NVDA.
		self.mixer =mixer.Mixer(self.simulation, 1)

	def make_sound_objects(self):
		"""Makes sound objects from libaudioverse."""
		for key, value in sound_files.iteritems():
			path = os.path.join(UNSPOKEN_SOUNDS_PATH, value)
			libaudioverse_object = libaudioverse.BufferNode(self.simulation)
			buffer = libaudioverse.Buffer(self.simulation)
			buffer.load_from_file(path)
			libaudioverse_object.buffer = buffer
			sounds[key] = libaudioverse_object

	def shouldNukeRoleSpeech(self):
		if config.conf["unspoken"]["sayAll"]:
			return not sayAllHandler.isRunning()
		return True

	def _hook_getSpeechTextForProperties(self, reason=NVDAObjects.controlTypes.REASON_QUERY, *args, **kwargs):
		role = kwargs.get('role', None)
		if role:
			if (role in sounds and self.shouldNukeRoleSpeech()):
				#NVDA will not announce roles if we put it in as _role.
				print "bah"
				kwargs['_role'] = kwargs['role']
				del kwargs['role']
		return self._NVDA_getSpeechTextForProperties(reason, *args, **kwargs)

	def terminate(self):
		addonGui.terminate()

	def _compute_volume(self):
		driver=speech.getSynth()
		volume = getattr(driver, 'volume', 100)/100.0 #nvda reports as percent.
		volume=clamp(volume, 0.0, 1.0)
		return volume

	def play_object(self, obj):
		curtime = time.time()
		if curtime-self._last_played_time < 0.1 and obj is self._last_played_object:
			return
		self._last_played_object = obj
		self._last_played_time = curtime
		role = obj.role
		if sounds.has_key(role):
			# Get coordinate bounds of desktop.
			desktop = NVDAObjects.api.getDesktopObject()
			desktop_max_x = desktop.location[2]
			desktop_max_y = desktop.location[3]
			# Get location of the object.
			if obj.location != None:
				# Object has a location. Get its center.
				obj_x = obj.location[0] + (obj.location[2] / 2.0)
				obj_y = obj.location[1] + (obj.location[3] / 2.0)
			else:
				# Objects without location are assumed in the center of the screen.
				obj_x = desktop_max_x / 2.0
				obj_y = desktop_max_y / 2.0
			# Scale object position to audio display.
			angle_x = ((obj_x-desktop_max_x/2.0)/desktop_max_x)*self._display_width
			#angle_y is a bit more involved.
			percent = (desktop_max_y-obj_y)/desktop_max_y
			angle_y = self._display_height_magnitude*percent+self._display_height_min
			#clamp these to Libaudioverse's internal ranges.
			angle_x = clamp(angle_x, -90.0, 90.0)
			angle_y = clamp(angle_y, -90.0, 90.0)
			#In theory, this can be made faster if we remember which is last, but that shouldn't matter here
			with self.simulation:
				for i, j in sounds.iteritems():
					j.disconnect(0)
				sounds[role].connect(0, self.hrtf_panner, 0)	
				sounds[role].position = 0.0
				self.hrtf_panner.azimuth = angle_x
				self.hrtf_panner.elevation = angle_y
				self.hrtf_panner.mul =self._compute_volume()

	def event_becomeNavigatorObject(self, obj, nextHandler):
		self.play_object(obj)
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		self.play_object(obj)
		nextHandler()

	def event_mouseMove(self, obj, nextHandler, x, y):
		if obj != self._previous_mouse_object:
			self._previous_mouse_object = obj
			self.play_object(obj)
		nextHandler()

