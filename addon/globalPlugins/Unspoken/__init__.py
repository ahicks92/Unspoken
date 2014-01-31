# Unspoken user interface feedback for NVDA
# By Bryan Smart (bryansmart@bryansmart.com)

import os
import sys

import globalPluginHandler
import NVDAObjects
import config
import speech

from camlorn_audio import *


# Constants

# Dimensions of the audio display
AUDIO_WIDTH = 24.0 # Width of the audio display.
AUDIO_DEPTH = 5.0 # Distance of listener from display.

UNSPOKEN_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


# Sounds

UNSPOKEN_SOUNDS_PATH = os.path.join(UNSPOKEN_ROOT_PATH, "sounds")

# Associate object roles to sounds.
sound_files={
"check box": "checkbox.wav",
"radio button": "radiobutton.wav",
"text": "editabletext.wav",
"edit": "editabletext.wav",
"button": "button.wav",
"menu bar": "menuitem.wav",
"menu item": "menuitem.wav",
"menu": "menuitem.wav",
"combo box": "combobox.wav",
"list item": "listitem.wav",
"graphic": "icon.wav",
"link": "link.wav",
"tree view item": "treeviewitem.wav",
"tab": "tab.wav",
"tab control": "tab.wav",
"slider": "slider.wav",
"drop down button": "combobox.wav",
"clock": "clock.wav",
"animation": "icon.wav",
"icon": "icon.wav",
"image map": "icon.wav",
"radio menu item": "radiobutton.wav",
"rich edit": "editabletext.wav",
"shape": "icon.wav",
"tear off menu": "menuitem.wav",
"toggle button": "checkbox.wav",
"chart": "icon.wav",
"diagram": "icon.wav",
"dial": "slider.wav",
"drop list": "combobox.wav",
"menu button": "button.wav",
"drop down button grid": "button.wav",
"hot key field": "editabletext.wav",
"indicator": "icon.wav",
"spin button": "slider.wav",
"tree view button": "button.wav",
"desktop icon": "icon.wav",
"password edit": "editabletext.wav",
"check menu item": "checkbox.wav",
"split button": "splitbutton.wav",
}

sounds = dict() # For holding instances in RAM.

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		globalPluginHandler.GlobalPlugin.__init__(self, *args, **kwargs)

		init_camlorn_audio()

		# Load sounds.
		for key in sound_files:
			sounds[key] = Sound3D(os.path.join(UNSPOKEN_SOUNDS_PATH, sound_files[key]))
			sounds[key].set_rolloff_factor(0)

		# Setup room ambience
		self._room_reverb = Reverb()
		self._room_reverb.set_reverb_density(0)
		self._room_reverb.set_Decay_time(0.4)
		self._room_reverb.set_gain(1)
		self._room_reverb.set_reflections_gain(0.4)
		self._room_reverb.set_late_reverb_gain(0)
		for sound in sounds:
			sounds[sound].set_effect_for_slot(self._room_reverb, 1)

		# Hook to keep NVDA from announcing roles.
		self._NVDA_getSpeechTextForProperties = speech.getSpeechTextForProperties
		speech.getSpeechTextForProperties = self._hook_getSpeechTextForProperties

		self._previous_mouse_object = None


	def _hook_getSpeechTextForProperties(self, reason=NVDAObjects.controlTypes.REASON_QUERY, *args, **kwargs):
		role = kwargs.get('role', None)
		if role:
			role_label = NVDAObjects.controlTypes.roleLabels[role]
			if 'role' in kwargs and role_label in sounds:
				del kwargs['role']
		return self._NVDA_getSpeechTextForProperties(reason, *args, **kwargs)

	def play_object(self, obj):
		global AUDIO_WIDTH, AUDIO_DEPTH
		role_label = NVDAObjects.controlTypes.roleLabels[obj.role]
		if sounds.has_key(role_label):
			# Get coordinate bounds of desktop.
			desktop = NVDAObjects.api.getDesktopObject()
			desktop_max_x = desktop.location[2]
			desktop_max_y = desktop.location[3]
			desktop_aspect = float(desktop_max_y) / float(desktop_max_x)
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
			position_x = (obj_x / desktop_max_x) * (AUDIO_WIDTH * 2) - AUDIO_WIDTH
			position_y = (obj_y / desktop_max_y) * (desktop_aspect * AUDIO_WIDTH * 2) - (desktop_aspect * AUDIO_WIDTH)
			position_y *= -1
			sounds[role_label].set_position(position_x, position_y, AUDIO_DEPTH * -1)
			sounds[role_label].play()

	def event_becomeNavigatorObject(self, obj, nextHandler):
		self.play_object(obj)
		nextHandler()

	def event_mouseMove(self, obj, nextHandler, x, y):
		if obj != self._previous_mouse_object:
			self._previous_mouse_object = obj
			self.play_object(obj)
		nextHandler()
