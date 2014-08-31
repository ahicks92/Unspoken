import _lav
import _libaudioverse
import weakref
import collections
import ctypes
import enum



#initialize libaudioverse.  This is per-app and implies no context settings, etc.
_lav.initialize_library()

#this makes sure that callback objects do not die.
_global_callbacks = collections.defaultdict(set)

#build and register all the error classes.
class GenericError(Exception):
	"""Base for all libaudioverse errors."""
	pass

class InternalError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_INTERNAL, InternalError)

class InvalidSlotError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_INVALID_SLOT, InvalidSlotError)

class NoOutputsError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_NO_OUTPUTS, NoOutputsError)

class CannotInitAudioError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_CANNOT_INIT_AUDIO, CannotInitAudioError)

class MemoryError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_MEMORY, MemoryError)

class RangeError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_RANGE, RangeError)

class FileNotFoundError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_FILE_NOT_FOUND, FileNotFoundError)

class ShapeError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_SHAPE, ShapeError)

class NullPointerError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_NULL_POINTER, NullPointerError)

class HrtfInvalidError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_HRTF_INVALID, HrtfInvalidError)

class CannotCrossDevicesError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_CANNOT_CROSS_DEVICES, CannotCrossDevicesError)

class CausesCycleError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_CAUSES_CYCLE, CausesCycleError)

class LimitExceededError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_LIMIT_EXCEEDED, LimitExceededError)

class FileError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_FILE, FileError)

class UnknownError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_UNKNOWN, UnknownError)

class TypeMismatchError(GenericError):
	pass
_lav.bindings_register_exception(_libaudioverse.Lav_ERROR_TYPE_MISMATCH, TypeMismatchError)


#A list-like thing that knows how to manipulate inputs.
class InputProxy(collections.Sequence):
	"""Manipulate inputs for some specific object.
This works exactly like a python list, save that concatenation is not allowed.  The elements are tuples: (parent, output) or, should no parent be set for a slot, None.

To link a parent to an output using this object, use  obj.parents[num] = (myparent, output).
To clear a parent, assign None.

Note that these objects are always up to date with their associated libaudioverse object but that iterators to them will become outdated if anything changes the graph.

Note also that we are not inheriting from MutableSequence because we cannot support __del__ and insert, but that the above advertised functionality still works anyway."""

	def __init__(self, for_object):
		self.for_object = for_object	

	def __len__(self):
		return _lav.object_get_input_count(self.for_object.handle)

	def __getitem__(self, key):
		par, out = self.for_object._get_input(key)
		if par is None:
			return None
		return par, out

	def __setitem__(self, key, val):
		if len(val) != 2 and val is not None:
			raise TypeError("Expected list of length 2 or None.")
		if not isinstance(val[0], GenericObject):
			raise TypeError("val[0]: is not a Libaudioverse object.")
		self.for_object._set_input(key, val[0] if val is not None else None, val[1] if val is not None else 0)

class _EventCallbackWrapper(object):
	"""Wraps callbacks into something sane.  Do not use externally."""

	def __init__(self, for_object, slot, callback, additional_args):
		self.obj_weakref = weakref.ref(for_object)
		self.additional_arguments = additional_args
		self.slot = slot
		self.callback = callback
		self.fptr = _libaudioverse.LavEventCallback(self)
		_lav.object_set_callback(for_object.handle, slot, self.fptr, None)

	def __call__(self, obj, userdata):
		actual_object = self.obj_weakref()
		if actual_object is None:
			return
		self.callback(actual_object, *self.additional_arguments)

class DeviceInfo(object):
	"""Represents info on a audio device."""

	def __init__(self, latency, channels, name, index):
		self.latency = latency
		self.channels = channels
		self.name = name
		self.index = index

def enumerate_devices():
	"""Returns a list of DeviceInfo representing the devices on the system.

The position in the list is the needed device index for Simulation.__iniit__."""
	max_index = _lav.device_get_count()
	infos = []
	for i in xrange(max_index):
		info = DeviceInfo(index = i,
		latency = _lav.device_get_latency(i),
		channels = _lav.device_get_channels(i),
		name = _lav.device_get_name(i))
		infos.append(info)
	return infos

class Simulation(object):
	"""Represents a running simulation.  All libaudioverse objects must be passed a simulation at creation time and cannot migrate between them.  Furthermore, it is an error to try to connect objects from different simulations."""

	def __init__(self, sample_rate = 44100, block_size = 1024, mix_ahead = 1, channels = 2, device_index = None):
		"""Create a simulation.

See enumerate_devices for the possible values of device_index and other output information.

There are two ways to initialize a device.

If device_index is None, sample_rate, buffer_size, and channels are used to give a simulation that doesn't actually output.  In this case, use the get_block method yourself to retrieve blocks of 32-bit floating point audio data.

Alternatively, if device_index is an integer, a device is created which feeds the specified output.  In this case, sample_rate, block_size, and mix_ahead are respected; channels is determined by the device in question.

One special value is not included in get_device_infos; this is -1.  -1 is the default system audio device plus the functionality required to follow the default if the user changes it, i.e. by unplugging headphones.  In this case, the returned device is always 2 channels."""
		if device_index is not None:
			handle = _lav.create_simulation_for_device(device_index, sample_rate, block_size, mix_ahead)
		else:
			handle = _lav.create_read_simulation(sample_rate, channels, block_size)
		self.handle = handle
		self._output_object = None

	def get_block(self):
		"""Returns a block of data.
Calling this on an audio output device will cause the audio thread to skip ahead a block, so don't do that."""
		length = _lav.simulation_get_block_size(self.handle)*_lav.simulation_get_channels(self.handle)
		buff = (ctypes.c_float*length)()
		_lav.simulation_get_block(self.handle, buff)
		return list(buff)

	@property
	def output_object(self):
		"""The object assigned to this property is the object which will play through the device."""
		return self._output_object

	@output_object.setter
	def output_object(self, val):
		if not (isinstance(val, GenericObject) or val is None):
			raise TypeError("Expected subclass of Libaudioverse.GenericObject")
		_lav.simulation_set_output_object(self.handle, val.handle if val is not None else val)
		self._output_object = val

#These are the enums which are needed publicly, i.e. distance model, etc.
class DistanceModels(enum.IntEnum):
	exponential = 1
	linear = 0
	inverseSquare = 2

#This is the class hierarchy.
#GenericObject is at the bottom, and we should never see one; and GenericObject should hold most implementation.
class GenericObject(object):
	"""A Libaudioverse object."""

	def __init__(self, handle, simulation):
		self.handle = handle
		self.simulation = simulation
		self._inputs = [(None, 0)]*_lav.object_get_input_count(handle)
		self._callbacks = dict()

	@property
	def suspended(self):
		return bool(_lav.object_get_int_property(self.handle, _libaudioverse.Lav_OBJECT_SUSPENDED))

	@suspended.setter
	def suspended(self, val):
		_lav.object_set_int_property(self.handle, _libaudioverse.Lav_OBJECT_SUSPENDED, int(bool(val)))


	def __del__(self):
		if _lav is None:
			#undocumented python thing: if __del__ is called at process exit, globals of this module are None.
			return
		if getattr(self, 'handle', None) is not None:
			_lav.free(self.handle)
		self.handle = None

	@property
	def inputs(self):
		"""Returns an InputProxy, an object that acts like a list of tuples.  The first item of each tuple is the parent object and the second item is the output to which we are connected."""
		self._check_input_resize()
		return InputProxy(self)

	def _check_input_resize(self):
		new_input_count = _lav.object_get_input_count(self.handle)
		new_input_list = self._inputs
		if new_input_count < len(self._inputs):
			new_input_list = self._inputs[0:new_parents_count]
		elif new_input_count > len(self._inputs):
			additional_inputs = [(None, 0)]*(new_input_count-len(self._inputs))
			new_input_list = new_input_list + additional_inputs
		self._inputs = new_input_list

	def _get_input(self, key):
		return self._inputs[key]

	def _set_input(self, key, obj, inp):
		if obj is None:
			_lav.object_set_input(self.handle, key, None, 0)
			self._inputs[key] = (None, 0)
		else:
			_lav.object_set_input(self.handle, key, obj.handle, inp)
			self._inputs[key] = (obj, inp)

	@property
	def output_count(self):
		"""Get the number of outputs that this object has."""
		return _lav.object_get_output_count(self.handle)

class SineObject(GenericObject):
	def __init__(self, sim):
		super(SineObject, self).__init__(_lav.create_sine_object(sim), sim)

	@property
	def frequency(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_SINE_FREQUENCY)

	@frequency.setter
	def frequency(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_SINE_FREQUENCY, float(val))


class MixerObject(GenericObject):
	def __init__(self, sim, max_parents, inputs_per_parent):
		super(MixerObject, self).__init__(_lav.create_mixer_object(sim, max_parents, inputs_per_parent), sim)

	@property
	def max_parents(self):
		return _lav.object_get_int_property(self.handle, _libaudioverse.Lav_MIXER_MAX_PARENTS)

	@max_parents.setter
	def max_parents(self, val):
		_lav.object_set_int_property(self.handle, _libaudioverse.Lav_MIXER_MAX_PARENTS, int(val))


	@property
	def inputs_per_parent(self):
		return _lav.object_get_int_property(self.handle, _libaudioverse.Lav_MIXER_INPUTS_PER_PARENT)

	@inputs_per_parent.setter
	def inputs_per_parent(self, val):
		_lav.object_set_int_property(self.handle, _libaudioverse.Lav_MIXER_INPUTS_PER_PARENT, int(val))


class WorldObject(GenericObject):
	def __init__(self, sim, hrtf_path):
		super(WorldObject, self).__init__(_lav.create_world_object(sim, hrtf_path), sim)

	@property
	def orientation(self):
		return _lav.object_get_float6_property(self.handle, _libaudioverse.Lav_3D_ORIENTATION)

	@orientation.setter
	def orientation(self, val):
		arg_tuple = tuple(val)
		if len(arg_tuple) != 6:
			raise ValueError('Expected a list or list-like object of 6 floats')
		_lav.object_set_float6_property(self.handle, _libaudioverse.Lav_3D_ORIENTATION, *(float(i) for i in arg_tuple))


	@property
	def position(self):
		return _lav.object_get_float3_property(self.handle, _libaudioverse.Lav_3D_POSITION)

	@position.setter
	def position(self, val):
		arg_tuple = tuple(val)
		if len(arg_tuple) != 3:
			raise  ValueError('Expected a list or list-like object of 3 floats')
		_lav.object_set_float3_property(self.handle, _libaudioverse.Lav_3D_POSITION, *(float(i) for i in arg_tuple))


class HrtfObject(GenericObject):
	def __init__(self, simulation, hrtf_path):
		super(HrtfObject, self).__init__(_lav.create_hrtf_object(simulation, hrtf_path), simulation)

	@property
	def azimuth(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_PANNER_AZIMUTH)

	@azimuth.setter
	def azimuth(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_PANNER_AZIMUTH, float(val))


	@property
	def elevation(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_PANNER_ELEVATION)

	@elevation.setter
	def elevation(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_PANNER_ELEVATION, float(val))


class FileObject(GenericObject):
	def __init__(self, sim, path):
		super(FileObject, self).__init__(_lav.create_file_object(sim, path), sim)

	@property
	def looping(self):
		return bool(_lav.object_get_int_property(self.handle, _libaudioverse.Lav_FILE_LOOPING))

	@looping.setter
	def looping(self, val):
		_lav.object_set_int_property(self.handle, _libaudioverse.Lav_FILE_LOOPING, int(bool(val)))


	@property
	def position(self):
		return _lav.object_get_double_property(self.handle, _libaudioverse.Lav_FILE_POSITION)

	@position.setter
	def position(self, val):
		_lav.object_set_double_property(self.handle, _libaudioverse.Lav_FILE_POSITION, float(val))


	@property
	def pitch_bend(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_FILE_PITCH_BEND)

	@pitch_bend.setter
	def pitch_bend(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_FILE_PITCH_BEND, float(val))


	@property
	def end_callback(self):
		cb = self._callbacks.get(_libaudioverse.Lav_FILE_END_CALLBACK, None)
		if cb is None:
			return
		return (cb.callback, cb.extra_arguments)

	@end_callback.setter
	def end_callback(self, val):
		global _global_callbacks
		val_tuple = tuple(val) if isinstance(val, collections.Iterable) else (val, )
		if len(val_tuple) == 1:
			val_tuple = (val, ())
		cb, extra_args = val_tuple
		callback_obj = _EventCallbackWrapper(self, _libaudioverse.Lav_FILE_END_CALLBACK, cb, extra_args)
		self._callbacks[_libaudioverse.Lav_FILE_END_CALLBACK] = callback_obj
		_global_callbacks[self.handle].add(callback_obj)


class HardLimiterObject(GenericObject):
	def __init__(self, sim, num_inputs):
		super(HardLimiterObject, self).__init__(_lav.create_hard_limiter_object(sim, num_inputs), sim)

class AmplitudePannerObject(GenericObject):
	def __init__(self, sim):
		super(AmplitudePannerObject, self).__init__(_lav.create_amplitude_panner_object(sim), sim)

	@property
	def azimuth(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_PANNER_AZIMUTH)

	@azimuth.setter
	def azimuth(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_PANNER_AZIMUTH, float(val))


	@property
	def elevation(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_PANNER_ELEVATION)

	@elevation.setter
	def elevation(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_PANNER_ELEVATION, float(val))


	@property
	def channel_map(self):
		retval = []
		for i in xrange(_lav.object_get_float_array_property_length(self.handle, _libaudioverse.Lav_PANNER_CHANNEL_MAP)):
			retval.append(_lav.object_read_float_array_property(self.handle, _libaudioverse.Lav_PANNER_CHANNEL_MAP, i))
		return tuple(retval)

	@channel_map.setter
	def channel_map(self, val):
		if not isinstance(val, collections.Sized):
			raise ValueError('expected an iterable with known size')
		_lav.object_replace_float_array_property(self.handle, _libaudioverse.Lav_PANNER_CHANNEL_MAP, len(val), val)


class AttenuatorObject(GenericObject):
	def __init__(self, sim, num_channels):
		super(AttenuatorObject, self).__init__(_lav.create_attenuator_object(sim, num_channels), sim)

	@property
	def multiplier(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_ATTENUATOR_MULTIPLIER)

	@multiplier.setter
	def multiplier(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_ATTENUATOR_MULTIPLIER, float(val))


class SourceObject(GenericObject):
	def __init__(self, sim, environment):
		super(SourceObject, self).__init__(_lav.create_source_object(sim, environment), sim)

	@property
	def orientation(self):
		return _lav.object_get_float6_property(self.handle, _libaudioverse.Lav_3D_ORIENTATION)

	@orientation.setter
	def orientation(self, val):
		arg_tuple = tuple(val)
		if len(arg_tuple) != 6:
			raise ValueError('Expected a list or list-like object of 6 floats')
		_lav.object_set_float6_property(self.handle, _libaudioverse.Lav_3D_ORIENTATION, *(float(i) for i in arg_tuple))


	@property
	def position(self):
		return _lav.object_get_float3_property(self.handle, _libaudioverse.Lav_3D_POSITION)

	@position.setter
	def position(self, val):
		arg_tuple = tuple(val)
		if len(arg_tuple) != 3:
			raise  ValueError('Expected a list or list-like object of 3 floats')
		_lav.object_set_float3_property(self.handle, _libaudioverse.Lav_3D_POSITION, *(float(i) for i in arg_tuple))


	@property
	def distance_model(self):
		val = _lav.object_get_int_property(self.handle, _libaudioverse.Lav_SOURCE_DISTANCE_MODEL)
		return DistanceModels(val)

	@distance_model.setter
	def distance_model(self, val):
		if not isinstance(val, DistanceModels) and isinstance(val, enum.IntEnum):
			raise valueError('Attemptn to use wrong enum to set property. Expected instance of DistanceModels')
		if isinstance(val, enum.IntEnum):
			val = val.value
		_lav.object_set_int_property(self.handle, _libaudioverse.Lav_SOURCE_DISTANCE_MODEL, int(val))


	@property
	def max_distance(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_SOURCE_MAX_DISTANCE)

	@max_distance.setter
	def max_distance(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_SOURCE_MAX_DISTANCE, float(val))


class DelayObject(GenericObject):
	def __init__(self, sim, lines):
		super(DelayObject, self).__init__(_lav.create_delay_object(sim, lines), sim)

	@property
	def feedback(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_DELAY_FEEDBACK)

	@feedback.setter
	def feedback(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_DELAY_FEEDBACK, float(val))


	@property
	def delay_max(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_DELAY_DELAY_MAX)

	@delay_max.setter
	def delay_max(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_DELAY_DELAY_MAX, float(val))


	@property
	def delay(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_DELAY_DELAY)

	@delay.setter
	def delay(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_DELAY_DELAY, float(val))


	@property
	def interpolation_time(self):
		return _lav.object_get_float_property(self.handle, _libaudioverse.Lav_DELAY_INTERPOLATION_TIME)

	@interpolation_time.setter
	def interpolation_time(self, val):
		_lav.object_set_float_property(self.handle, _libaudioverse.Lav_DELAY_INTERPOLATION_TIME, float(val))


