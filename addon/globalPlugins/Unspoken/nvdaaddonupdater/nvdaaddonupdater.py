# Automatically update an NVDA add on.
# By Bryan Smart (bryansmart@bryansmart.com)

import os
import threading
import urllib
import tempfile

import gui

import wx

from callafter import *

class NVDAAddOnUpdater (object):

	def __init__ (self, add_on_name, update_url, current_version):
		self._add_on_name = add_on_name
		self._update_url = update_url
		self._current_version = current_version

		update_thread = threading.Thread(target=self.check_update)
		update_thread.daemon = True
		update_thread.start()

	def check_update(self):
		# Retrieve current version number.
		try:
			f = urllib.urlopen(self._update_url + '/version')
		except:
			# If Internet unavailable, silently fail.
			return

		# Check response code.
		if f.getcode() != 200:
			# Silently fail on 404 or other page errors.
			return

		# Finally, if we have a good connection, read the version.
		new_version = f.readline()
		f.close

		if new_version <= self._current_version: return

		# Prompt to update.
		caption = "New NVDA add on version available"
		question = self._add_on_name + "\nA new version is available. Would you like to install it now?\n"
		question += "Installed version: " + self._current_version + "\n"
		question += "New version: " + new_version + "\n"
		#answer = gui.messageBox(question, caption=caption, style=wx.YES_NO | wx.ICON_QUESTION)
		answer = call_after_and_block(gui.messageBox, question, caption=caption, style=wx.YES_NO | wx.ICON_QUESTION)
		if answer == wx.YES:
			self.force_update()

	def force_update(self):
		# Open connection to download update.
		try:
			remote_file = urllib.urlopen(self._update_url + '/install')
		except:
			gui.messageBox("Unable to connect to update server!", style=wx.ICON_ERROR)
			return
		if remote_file.getcode() != 200:
			gui.messageBox("The update could not be accessed! Check your Internet connection.", style=wx.ICON_ERROR)
			return

		# Download the update to a temporary file.
		local_file = tempfile.TemporaryFile(suffix='.nvda-addon', delete=False)
		local_file.write(remote_file.read())
		local_file.close()

		os.system(local_file.name)