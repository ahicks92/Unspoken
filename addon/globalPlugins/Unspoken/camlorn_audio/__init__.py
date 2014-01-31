"""
High level Python wrapper to Camlorn Audio
Author: Christopher Toth <q@q-continuum.net>, Austin hicks <camlorn38@gmail.com>
"""

import _camlorn_audio
import collections
import os

#a bunch of exceptions.
class CamlornAudioError(Exception):
	"""Base camlorn_audio exception."""
	pass

	def __init__(self, code = 0):
		self.code = code

class ObjectCreationError(CamlornAudioError):
	"""Thrown when an object couldn't be created."""
	pass

class NotInitializedError(CamlornAudioError):
	"""Thrown when something that needs to use the library is called before init_camlorn_audio."""
	pass

class UnsupportedChannelCountError(CamlornAudioError):
	"""Thrown when the library cannot deal with sound data because it has an unsupported number of channels."""
	pass

class ArgumentOutOfRangeError(CamlornAudioError):
	"""Thrown when an argument to a camlorn_audio function is out of range."""
	pass

#this mapping holds the code->class information for those errors which have a dedicated class.
_error_code_to_class = collections.defaultdict(lambda: CamlornAudioError,
{
_camlorn_audio.UNSUPPORTED_CHANNEL_COUNT_ERROR: UnsupportedChannelCountError,
_camlorn_audio.ARGUMENT_OUT_OF_RANGE_ERROR: ArgumentOutOfRangeError,
})

def camcall(function, *args):
	"""Handles calling camlorn_audio functions which may fail in a standard fashion.  Does not handle constructors, or those functions which can't fail."""
	if args[0] is None:
		print "Warning: handle may be invalid."
	code= function(*args)
	if code != 0:
		raise _error_code_to_class[code](code)

#compute the default HRTF location.
default_hrtf_location = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hrtfs', '%r.hrtf')
def init_camlorn_audio(should_have_hrtf=True, channels="stereo", frequency=44100, backend_order="dsound, winmm", should_allow_user_config_file = False, max_number_of_sources = 100000, hrtf_file_specifier = default_hrtf_location):
	"""Initialize camlorn_audio.  The defaults are good enough for most cases.
Note: some people will have better luck with different backend orders. Play with setting it to different values: options are mmdevapi, winmm, or dsound.  Set it to a comma separated list, and they will be tried in order.  If it works for you, mmdevapi is the best option."""
	_camlorn_audio.CA_initCamlornAudio(1 if should_have_hrtf else 0, channels, frequency, backend_order, 1 if should_allow_user_config_file else 0, max_number_of_sources, hrtf_file_specifier)

class CAObject(object):
	constructor = None

	def __init__(self, *args, **kwargs):
		self.handle = None
		if callable(self.constructor):
			self.handle = self.constructor()
		if self.handle is None:
			raise ObjectCreationError()	
		super(CAObject, self).__init__()

	def free(self):
		_camlorn_audio.CA_free(self.handle)
		self.handle = None

	def __del__(self):
		if self.handle is not None:
			self.free()

class SoundBase(CAObject):

	def play(self):
		"""Begin playing a sound.  Subsequent calls to play on an an already playing sound will cause it to start playing from the beginning again."""
		camcall(_camlorn_audio.CA_SoundBase_play, self.handle)

	def pause(self):
		"""Pause a sound.  Stops playback such that calling play will cause it to start playing from the current position."""
		camcall(_camlorn_audio.CA_SoundBase_pause, self.handle)

	def set_volume(self, volume) :
		"""Sets the volume.  Any value above or equal to zero is valid, but going above 1.0 has intensional side effects."""
		camcall(_camlorn_audio.CA_SoundBase_setVolume, self.handle, volume)


	def stop(self):
		"""Stops playback of a sound and rewinds it to the beginning."""
		camcall(_camlorn_audio.CA_SoundBase_stop, self.handle)

	def get_looping(self):
		"""Returns true if the sound is looping; otherwise false."""
		return bool(_camlorn_audio.CA_SoundBase_getLooping(self.handle))

	def set_looping(self, looping):
		"""Sets whether or not the sound is looping.  Pass in true to make the sound loop; pass in false to stop it again."""
		camcall(_camlorn_audio.CA_SoundBase_setLooping, self.handle, looping)

	def set_pitch_bend(self, bend):
		"""Set the pitch bend."""
		camcall(_camlorn_audio.CA_SoundBase_setPitchBend, self.handle, bend)

	def get_length(self):
		"""Return the length of the sound, in seconds."""
		return _camlorn_audio.CA_SoundBase_getLength( self.handle)

	def seek(self, where, accountForPitch = True):
		"""Seek to a position, optionally accounting for any pitch bend."""
		camcall(_camlorn_audio.CA_SoundBase_seek, self.handle, where, 1 if accountForPitch else 0)

class EfxCapable(SoundBase):
	"""Anything inheriting from EfxCapable may play through effects and filters"""

	def set_dry_filter(self, filter):
		"""Sets the filter to be applied to the dry path."""
		camcall(_camlorn_audio.CA_EfxCapable_setDryFilter, self.handle, filter.handle)

	def clear_dry_filter(self):
		"""Clears the filter on the dry path if any."""
		camcall(_camlorn_audio.CA_EfxCapable_clearDryFilter, self.handle)

	def set_filter_for_slot(self, filter, number):
		"""Sets the filter for a slot."""
		camcall(_camlorn_audio.CA_EfxCapable_setFilterForSlot, self.handle, filter.handle, number)

	def clear_filter_for_slot(self, number):
		"""Disconnects a filter from one of the 4 slots."""
		camcall(_camlorn_audio.CA_EfxCapable_clearFilterForSlot, self.handle, number)

	def set_effect_for_slot(self, effect, number):
		"""Sets an effect for one of the 4 slots, such that this sound will begin playing through it."""
		camcall(_camlorn_audio.CA_EfxCapable_setEffectForSlot, self.handle, effect.handle, number)

	def clear_effect_for_slot(self, number):
		"""Clears an effect on the specified slot."""
		camcall(_camlorn_audio.CA_EfxCapable_clearEffectForSlot, self.handle, number)

	def set_air_absorption_factor(self, factor):
		"""Sets the air absorption factor.  Valid values are from 0 to 10."""
		camcall(_camlorn_audio.CA_EfxCapable_setAirAbsorptionFactor, self.handle, factor)

class SourceHelper3D(EfxCapable):

	def set_position(self, x, y, z):
		"""Sets the position of a sound in the default Open AL coordinate system.

There is no need to move sounds when the player moves.  Instead, create a Viewpoint and move that.  Moving viewpoints moves all sounds appropriately.

The Open AL coordinate system is as follows: positive X values are to the right, positive Y values are up, and positive Z values are behind you.  If you are using a Viewpoint, this may not hold true--
if the viewpoint is turned to look along the positive Z axis, for example, then positive Z is in front, positive X is to the left, and positive y is still up.  This means that, in effect, viewpoints should represent the player's position and orientation, you should consider x as east/west, z as south/north, and y as up/down and position things in world space.
"""
		camcall(_camlorn_audio.CA_SourceHelper3D_setPosition, self.handle, x, y, z)

	def set_velocity(self, x, y, z):
		"""Sets the velocity.  This doesn't actually move sounds and is used only in doppler calculations.  This is in world space and uses the same coordinate system and rules as set_position."""
		camcall(_camlorn_audio.CA_SourceHelper3D_setVelocity, self.handle, x, y, z)

	def set_head_relative(self, onoff):
		"""Turns head relativity-whether a source's position is relative to the active viewpoint or the origin-on or off."""
		camcall(_camlorn_audio.CA_SourceHelper3D_setHeadRelative, self.handle, 1 if onoff else 0)

	def set_reference_distance(self, distance):
		"""Sets the reference distance."""
		camcall(_camlorn_audio.CA_SourceHelper3D_setReferenceDistance, self.handle, distance)

	def set_rolloff_factor(self, factor):
		"""Sets the rolloff factor, a value which represents how quickly sources lose volume as they move further away."""
		camcall(_camlorn_audio.CA_SourceHelper3D_setRolloffFactor, self.handle, factor)

	def set_max_distance(self, distance):
		"""Sets the maximum distance at which a sound is to be heard."""
		camcall(_camlorn_audio.CA_SourceHelper3D_setMaxDistance, self.handle, distance)

	def set_distance_model(self, model):
		"""Sets the per-sound distance model."""
		camcall(_camlorn_audio.CA_SourceHelper3D_setDistanceModel, self.handle, model)

class FileSetter(object):

	def __init__(self, filename=None):
		"""Initializes an object, optionally setting the file which it is to play."""
		super(FileSetter, self).__init__()
		if filename is not None:
			self.set_file(filename)

	def set_file(self, filename):
		"""Sets the file from which to play audio."""
		camcall(_camlorn_audio.CA_FileSetter_setFile, self.handle, filename)
		self.filename = filename

class Sound3D(FileSetter, SourceHelper3D):
	"""A Sound3D is a mono sound that can be positioned in 3d space.

It will load the entire file at once.  If files are large, use StreamingSound3D instead.  Set the file by calling set_file.
"""
	constructor = _camlorn_audio.CA_newSound3d

class Music(FileSetter, EfxCapable):
	"""Represents music.  Music is different from a 3d sound in two ways: it need not be a mono file and it cannot be moved."""
	constructor = _camlorn_audio.CA_newMusic

class StreamingMusic(Music):
	"""Represents music.  Unlike Music, this class streams from disk rather than loading the file all at once."""
	constructor = _camlorn_audio.CA_newStreamingMusic

class StreamingSound3D(Sound3D):
	"""A StreamingSound3D is the same as a Sound3D except that it streams the file from disk rather than loading it all at once."""
	constructor = _camlorn_audio.CA_newStreamingSound3d

class Echo(CAObject):
	constructor = _camlorn_audio.CA_newEcho

	def set_delay(self, delay):
		camcall(_camlorn_audio.CA_Echo_setDelay, self.handle, delay)

	def set_LR_delay(self, delay):
		camcall(_camlorn_audio.CA_Echo_setLRDelay, self.handle, delay)

	def set_damping(self, damping):
		camcall(_camlorn_audio.CA_Echo_setDamping, self.handle, damping)

	def set_feedback(self, feedback):
		camcall(_camlorn_audio.CA_Echo_setFeedback, self.handle, feedback)

	def set_spread(self, spread):
		camcall(_camlorn_audio.CA_Echo_setSpread, self.handle, spread)

class Filter(CAObject):
	"""Represents a filter"""
	constructor = _camlorn_audio.CA_newFilter

	def set_filter_type(self, type):
		camcall(_camlorn_audio.CA_Filter_setFilterType, self.handle, type)

	def set_gain(self, gain):
		camcall(_camlorn_audio.CA_Filter_setGain, self.handle, gain)

	def set_gain_hf(self, gain):
		camcall(_camlorn_audio.CA_Filter_setGainHF, self.handle, gain)

	def set_gain_lf(self, gain):
		camcall(_camlorn_audio.CA_Filter_setGainLF, self.handle, gain)

class Reverb(CAObject):
	constructor = _camlorn_audio.CA_newReverb

	def set_reverb_density(self, reverb_density):
		camcall(_camlorn_audio.CA_Reverb_setReverbDensity, self.handle, reverb_density)

	def set_diffusion(self, diffusion):
		camcall(_camlorn_audio.CA_Reverb_setDiffusion, self.handle, diffusion)

	def set_gain(self, gain):
		camcall(_camlorn_audio.CA_Reverb_setGain, self.handle, gain)

	def set_gain_HF(self, gain_HF):
		camcall(_camlorn_audio.CA_Reverb_setGainHF, self.handle, gain_HF)

	def set_Decay_time(self, decay_time):
		camcall(_camlorn_audio.CA_Reverb_setDecayTime, self.handle, decay_time)

	def set_decay_HF_ratio(self, decay_HF_ratio):
		camcall(_camlorn_audio.CA_Reverb_setDecayHFRatio, self.handle, decay_HF_ratio)

	def set_reflections_gain(self, reflections_gain):
		camcall(_camlorn_audio.CA_Reverb_setReflectionsGain, self.handle, reflections_gain)

	def set_reflections_delay(self, reflections_delay):
		camcall(_camlorn_audio.CA_Reverb_setReflectionsDelay, self.handle, reflections_delay)

	def set_late_reverb_gain(self, late_reverb_gain):
		camcall(_camlorn_audio.CA_Reverb_setLateReverbGain, self.handle, late_reverb_gain)

	def set_late_reverb_delay(self, late_reverb_delay):
		camcall(_camlorn_audio.CA_Reverb_setLateReverbDelay, self.handle, late_reverb_delay)

	def set_air_absorption_gain_HF(self, air_absorption_gain_HF):
		camcall(_camlorn_audio.CA_Reverb_setAirAbsorptionGainHF, self.handle, air_absorption_gain_HF)

	def set_room_rolloff_factor(self, room_rolloff_factor):
		camcall(_camlorn_audio.CA_Reverb_setRoomRolloffFactor, self.handle, room_rolloff_factor)

	def set_decay_HF_limit(self, decay_HF_limit):
		camcall(_camlorn_audio.CA_Reverb_setDecayHFLimit, self.handle, decay_HF_limit)

class EAXReverb(CAObject):
	constructor = _camlorn_audio.CA_newEaxReverb

	def set_reverb_density(self, reverb_density):
		camcall(_camlorn_audio.CA_EaxReverb_setReverbDensity, self.handle, reverb_density)

	def set_diffusion(self, diffusion):
		camcall(_camlorn_audio.CA_EaxReverb_setDiffusion, self.handle, diffusion)

	def set_gain(self, gain):
		camcall(_camlorn_audio.CA_EaxReverb_setGain, self.handle, gain)

	def set_gain_HF(self, gain_HF):
		camcall(_camlorn_audio.CA_EaxReverb_setGainHF, self.handle, gain_HF)

	def set_gain_LF(self, gain_LF):
		camcall(_camlorn_audio.CA_EaxReverb_setGainLF, self.handle, gain_LF)

	def set_decay_time(self, decay_time):
		camcall(_camlorn_audio.CA_EaxReverb_setDecayTime, self.handle, decay_time)

	def set_decay_HF_ratio(self, decay_HF_ratio):
		camcall(_camlorn_audio.CA_EaxReverb_setDecayHFRatio, self.handle, decay_HF_ratio)

	def set_decay_LF_ratio(self, decay_LF_ratio):
		camcall(_camlorn_audio.CA_EaxReverb_setDecayHFRatio, self.handle, decay_LF_ratio)

	def set_reflections_gain(self, reflections_gain):
		camcall(_camlorn_audio.CA_EaxReverb_setReflectionsGain, self.handle, reflections_gain)

	def set_reflections_delay(self, reflections_delay):
		camcall(_camlorn_audio.CA_EaxReverb_setReflectionsDelay, self.handle, reflections_delay)

	def set_late_reverb_gain(self, late_reverb_gain):
		camcall(_camlorn_audio.CA_EaxReverb_setLateReverbGain, self.handle, late_reverb_gain)

	def set_late_reverb_delay(self, late_reverb_delay):
		camcall(_camlorn_audio.CA_EaxReverb_setLateReverbDelay, self.handle, late_reverb_delay)

	def set_echo_time(self, echo_time):
		camcall(_camlorn_audio.CA_EaxReverb_setEchoTime, self.handle, echo_time)

	def set_echo_depth(self, echo_depth):
		camcall(_camlorn_audio.CA_EaxReverb_setEchoDepth, self.handle, echo_depth)

	def set_modulation_time(self, modulation_time):
		camcall(_camlorn_audio.CA_EaxReverb_setModulationTime, self.handle, modulation_time)

	def set_modulation_depth(self, modulation_depth):
		camcall(_camlorn_audio.CA_EaxReverb_setModulationDepth, self.handle, modulation_depth)

	def set_air_absorption_gain_HF(self, air_absorption_gain_HF):
		camcall(_camlorn_audio.CA_EaxReverb_setAirAbsorptionGainHF, self.handle, air_absorption_gain_HF)

	def set_HF_reference(self, HF_reference):
		camcall(_camlorn_audio.CA_EaxReverb_setHFReference, self.handle, HF_reference)

	def set_lF_reference(self, lF_reference):
		camcall(_camlorn_audio.CA_EaxReverb_setLFReference, self.handle, lf_reference)

	def set_room_rolloff_factor(self, room_rolloff_factor):
		camcall(_camlorn_audio.CA_EaxReverb_setRoomRolloffFactor, self.handle, room_rolloff_factor)

	def set_decay_HF_limit(self, decay_HF_limit):
		camcall(_camlorn_audio.CA_EaxReverb_setDecayHFLimit, self.handle, decay_HF_limit)

	def set_reflections_pan(self, x, y, z):
		camcall(_camlorn_audio.CA_EaxReverb_setReflectionsPan, self.handle, x, y, z)

	def set_late_reverb_pan(self, x, y, z):
		camcall(_camlorn_audio.CA_EaxReverb_setLateReverbPan, self.handle, x, y, z)


class Viewpoint(CAObject):
	"""Represents a viewpoint.  This is the position from which someone or something is listening."""
	constructor = _camlorn_audio.CA_newViewpoint

	def set_at_vector(self, x, y, z):
		"""Sets the at vector, the vector representing the direction in which the viewpoint is looking.  This should always be orthogonal to the up vector."""
		camcall(_camlorn_audio.CA_Viewpoint_setAtVector, self.handle, x, y, z)

	def set_up_vector(self, x, y, z):
		"""This sets the up vector: the direction of the top of the Viewpoint.  This should be orthogonal to the at vector."""
		camcall(_camlorn_audio.CA_Viewpoint_setUpVector, self.handle, x, y, z)

	def set_orientation(self, at_x, at_y, at_z, up_x, up_y, up_z):
		"""Sets the at and up vectors at the same time.  Use this when setting them separately will lead to them not being orthogonal for any period of time."""
		camcall(_camlorn_audio.CA_Viewpoint_setOrientation, self.handle, at_x, at_y, at_z, up_x, up_y, up_z)

	def set_velocity(self, x, y, z):
		"""This sets the velocity of the viewpoint.  This is used in doppler calculations."""
		camcall(_camlorn_audio.CA_Viewpoint_setVelocity, self.handle, x, y, z)

	def set_position(self, x, y, z):
		"""Sets the position of the viewpoint in world coordinates: positive x is to the right, positive z is out of the screen, and positive y is up."""
		camcall(_camlorn_audio.CA_Viewpoint_setPosition, self.handle, x, y, z)

	def make_active(self):
		"""Makes this viewpoint active, deactivating any other active viewpoint in the process.  This means that the player is listening from this viewpoint."""
		camcall(_camlorn_audio.CA_Viewpoint_makeActive, self.handle)

	def is_active(self):
		"""Returns true if this viewpoint is the active viewpoint; otherwise false."""
		return True if _camlorn_audio.CA_Viewpoint_isActive(self.handle) == 1 else False
