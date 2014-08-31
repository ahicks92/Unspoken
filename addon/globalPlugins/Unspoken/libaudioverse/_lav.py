#implements lifting the raw ctypes-basedd api into something markedly pallatable.
#among other things, the implementation heree enables calling functions with keyword arguments and raises exceptions on error, rather than dealing with ctypes directly.
import ctypes
import collections
import _libaudioverse

#These are not from libaudioverse.
#Implement a method by which the public libaudioverse module may register its exception classes for error code translation.
class PythonBindingsCouldNotTranslateErrorCodeError(Exception):
	"""An exception representing failure to translate a libaudioverse error code into a python exception.  If you see this, report it as a bug with Libaudioverse because something has gone very badly wrong."""
	pass

errors_to_exceptions = dict()

def bindings_register_exception(code, cls):
	errors_to_exceptions[code] = cls

def make_error_from_code(err):
	"""Internal use.  Translates libaudioverse error codes into exceptions."""
	return errors_to_exceptions.get(err, PythonBindingsCouldNotTranslateErrorCodeError)()


def initialize_library():

	err = _libaudioverse.Lav_initializeLibrary()
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def free(obj):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (None*len(obj))(*obj)

	err = _libaudioverse.Lav_free(obj)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def device_get_count():

	destination = ctypes.c_uint()
	err = _libaudioverse.Lav_deviceGetCount(		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def device_get_latency(index):

	destination = ctypes.c_float()
	err = _libaudioverse.Lav_deviceGetLatency(index, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def device_get_name(index):

	destination = ctypes.c_char_p()
	err = _libaudioverse.Lav_deviceGetName(index, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def device_get_channels(index):

	destination = ctypes.c_uint()
	err = _libaudioverse.Lav_deviceGetChannels(index, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_simulation_for_device(index, sr, blockSize, mixAhead):

	destination = ctypes.POINTER(_libaudioverse.LavSimulation)()
	err = _libaudioverse.Lav_createSimulationForDevice(index, sr, blockSize, mixAhead, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_read_simulation(sr, channels, blockSize):

	destination = ctypes.POINTER(_libaudioverse.LavSimulation)()
	err = _libaudioverse.Lav_createReadSimulation(sr, channels, blockSize, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def simulation_set_output_object(simulation, object):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)
	object = getattr(object, 'handle', object)
	if isinstance(object, collections.Sized):
		object = (LavObject*len(object))(*object)

	err = _libaudioverse.Lav_simulationSetOutputObject(simulation, object)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def simulation_get_output_object(simulation):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_simulationGetOutputObject(simulation, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def simulation_get_block_size(simulation):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_simulationGetBlockSize(simulation, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def simulation_get_block(simulation, buffer):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)
	buffer = getattr(buffer, 'handle', buffer)
	if isinstance(buffer, collections.Sized):
		buffer = (ctypes.c_float*len(buffer))(*buffer)

	err = _libaudioverse.Lav_simulationGetBlock(simulation, buffer)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def simulation_get_sr(simulation):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_simulationGetSr(simulation, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def simulation_get_channels(simulation):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_simulationGetChannels(simulation, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_type(obj):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_objectGetType(obj, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_input_count(obj):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_uint()
	err = _libaudioverse.Lav_objectGetInputCount(obj, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_output_count(obj):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_uint()
	err = _libaudioverse.Lav_objectGetOutputCount(obj, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_input_object(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_objectGetInputObject(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_input_output(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_uint()
	err = _libaudioverse.Lav_objectGetInputOutput(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_set_input(obj, input, parent, output):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	parent = getattr(parent, 'handle', parent)
	if isinstance(parent, collections.Sized):
		parent = (LavObject*len(parent))(*parent)

	err = _libaudioverse.Lav_objectSetInput(obj, input, parent, output)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_reset_property(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	err = _libaudioverse.Lav_objectResetProperty(obj, slot)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_set_int_property(obj, slot, value):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	err = _libaudioverse.Lav_objectSetIntProperty(obj, slot, value)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_set_float_property(obj, slot, value):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	err = _libaudioverse.Lav_objectSetFloatProperty(obj, slot, value)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_set_double_property(obj, slot, value):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	err = _libaudioverse.Lav_objectSetDoubleProperty(obj, slot, value)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_set_string_property(obj, slot, value):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	value = getattr(value, 'handle', value)

	err = _libaudioverse.Lav_objectSetStringProperty(obj, slot, value)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_set_float3_property(obj, slot, v1, v2, v3):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	err = _libaudioverse.Lav_objectSetFloat3Property(obj, slot, v1, v2, v3)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_set_float6_property(obj, slot, v1, v2, v3, v4, v5, v6):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	err = _libaudioverse.Lav_objectSetFloat6Property(obj, slot, v1, v2, v3, v4, v5, v6)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_get_int_property(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_objectGetIntProperty(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_float_property(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_float()
	err = _libaudioverse.Lav_objectGetFloatProperty(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_double_property(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_double()
	err = _libaudioverse.Lav_objectGetDoubleProperty(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_string_property(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_char_p()
	err = _libaudioverse.Lav_objectGetStringProperty(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_float3_property(obj, slot, v1, v2, v3):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	v1 = getattr(v1, 'handle', v1)
	if isinstance(v1, collections.Sized):
		v1 = (ctypes.c_float*len(v1))(*v1)
	v2 = getattr(v2, 'handle', v2)
	if isinstance(v2, collections.Sized):
		v2 = (ctypes.c_float*len(v2))(*v2)
	v3 = getattr(v3, 'handle', v3)
	if isinstance(v3, collections.Sized):
		v3 = (ctypes.c_float*len(v3))(*v3)

	err = _libaudioverse.Lav_objectGetFloat3Property(obj, slot, v1, v2, v3)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_get_float6_property(obj, slot, v1, v2, v3, v4, v5, v6):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	v1 = getattr(v1, 'handle', v1)
	if isinstance(v1, collections.Sized):
		v1 = (ctypes.c_float*len(v1))(*v1)
	v2 = getattr(v2, 'handle', v2)
	if isinstance(v2, collections.Sized):
		v2 = (ctypes.c_float*len(v2))(*v2)
	v3 = getattr(v3, 'handle', v3)
	if isinstance(v3, collections.Sized):
		v3 = (ctypes.c_float*len(v3))(*v3)
	v4 = getattr(v4, 'handle', v4)
	if isinstance(v4, collections.Sized):
		v4 = (ctypes.c_float*len(v4))(*v4)
	v5 = getattr(v5, 'handle', v5)
	if isinstance(v5, collections.Sized):
		v5 = (ctypes.c_float*len(v5))(*v5)
	v6 = getattr(v6, 'handle', v6)
	if isinstance(v6, collections.Sized):
		v6 = (ctypes.c_float*len(v6))(*v6)

	err = _libaudioverse.Lav_objectGetFloat6Property(obj, slot, v1, v2, v3, v4, v5, v6)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_get_int_property_range(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination_lower = ctypes.c_int()
	destination_upper = ctypes.c_int()
	err = _libaudioverse.Lav_objectGetIntPropertyRange(obj, slot, 		ctypes.byref(destination_lower), ctypes.byref(destination_upper))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination_lower, 'value', destination_lower))
	retval.append(getattr(destination_upper, 'value', destination_upper))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_float_property_range(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination_lower = ctypes.c_float()
	destination_upper = ctypes.c_float()
	err = _libaudioverse.Lav_objectGetFloatPropertyRange(obj, slot, 		ctypes.byref(destination_lower), ctypes.byref(destination_upper))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination_lower, 'value', destination_lower))
	retval.append(getattr(destination_upper, 'value', destination_upper))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_double_property_range(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination_lower = ctypes.c_double()
	destination_upper = ctypes.c_double()
	err = _libaudioverse.Lav_objectGetDoublePropertyRange(obj, slot, 		ctypes.byref(destination_lower), ctypes.byref(destination_upper))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination_lower, 'value', destination_lower))
	retval.append(getattr(destination_upper, 'value', destination_upper))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_property_indices(obj):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.POINTER(ctypes.c_int)()
	err = _libaudioverse.Lav_objectGetPropertyIndices(obj, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_property_name(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_char_p()
	err = _libaudioverse.Lav_objectGetPropertyName(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_replace_float_array_property(obj, slot, length, values):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	values = getattr(values, 'handle', values)
	if isinstance(values, collections.Sized):
		values = (ctypes.c_float*len(values))(*values)

	err = _libaudioverse.Lav_objectReplaceFloatArrayProperty(obj, slot, length, values)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_read_float_array_property(obj, slot, index):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_float()
	err = _libaudioverse.Lav_objectReadFloatArrayProperty(obj, slot, index, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_write_float_array_property(obj, slot, start, stop, values):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	values = getattr(values, 'handle', values)
	if isinstance(values, collections.Sized):
		values = (ctypes.c_float*len(values))(*values)

	err = _libaudioverse.Lav_objectWriteFloatArrayProperty(obj, slot, start, stop, values)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_get_float_array_property_default(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destinationLength = ctypes.c_uint()
	destinationArray = ctypes.POINTER(ctypes.c_float)()
	err = _libaudioverse.Lav_objectGetFloatArrayPropertyDefault(obj, slot, 		ctypes.byref(destinationLength), ctypes.byref(destinationArray))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destinationLength, 'value', destinationLength))
	retval.append(getattr(destinationArray, 'value', destinationArray))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_float_array_property_length(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_uint()
	err = _libaudioverse.Lav_objectGetFloatArrayPropertyLength(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_replace_int_array_property(obj, slot, length, values):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	values = getattr(values, 'handle', values)
	if isinstance(values, collections.Sized):
		values = (ctypes.c_int*len(values))(*values)

	err = _libaudioverse.Lav_objectReplaceIntArrayProperty(obj, slot, length, values)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_read_int_array_property(obj, slot, index):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_objectReadIntArrayProperty(obj, slot, index, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_write_int_array_property(obj, slot, start, stop, values):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	values = getattr(values, 'handle', values)
	if isinstance(values, collections.Sized):
		values = (ctypes.c_int*len(values))(*values)

	err = _libaudioverse.Lav_objectWriteIntArrayProperty(obj, slot, start, stop, values)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def object_get_int_array_property_default(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destinationLength = ctypes.c_uint()
	destinationArray = ctypes.POINTER(ctypes.c_int)()
	err = _libaudioverse.Lav_objectGetIntArrayPropertyDefault(obj, slot, 		ctypes.byref(destinationLength), ctypes.byref(destinationArray))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destinationLength, 'value', destinationLength))
	retval.append(getattr(destinationArray, 'value', destinationArray))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_int_array_property_length(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_int()
	err = _libaudioverse.Lav_objectGetIntArrayPropertyLength(obj, slot, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_array_property_length_range(obj, slot):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destinationMin = ctypes.c_uint()
	destinationMax = ctypes.c_uint()
	err = _libaudioverse.Lav_objectGetArrayPropertyLengthRange(obj, slot, 		ctypes.byref(destinationMin), ctypes.byref(destinationMax))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destinationMin, 'value', destinationMin))
	retval.append(getattr(destinationMax, 'value', destinationMax))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_callback_handler(obj, callback):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = _libaudioverse.LavEventCallback()
	err = _libaudioverse.Lav_objectGetCallbackHandler(obj, callback, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_get_callback_user_data_pointer(obj, callback):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)

	destination = ctypes.c_void_p()
	err = _libaudioverse.Lav_objectGetCallbackUserDataPointer(obj, callback, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def object_set_callback(obj, callback, handler, userData):
	obj = getattr(obj, 'handle', obj)
	if isinstance(obj, collections.Sized):
		obj = (LavObject*len(obj))(*obj)
	userData = getattr(userData, 'handle', userData)
	if isinstance(userData, collections.Sized):
		userData = (None*len(userData))(*userData)

	err = _libaudioverse.Lav_objectSetCallback(obj, callback, handler, userData)
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)

def create_sine_object(sim):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createSineObject(sim, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_file_object(sim, path):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)
	path = getattr(path, 'handle', path)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createFileObject(sim, path, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_hrtf_object(simulation, hrtfPath):
	simulation = getattr(simulation, 'handle', simulation)
	if isinstance(simulation, collections.Sized):
		simulation = (LavSimulation*len(simulation))(*simulation)
	hrtfPath = getattr(hrtfPath, 'handle', hrtfPath)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createHrtfObject(simulation, hrtfPath, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_mixer_object(sim, maxParents, inputsPerParent):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createMixerObject(sim, maxParents, inputsPerParent, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_attenuator_object(sim, numChannels):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createAttenuatorObject(sim, numChannels, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_hard_limiter_object(sim, numInputs):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createHardLimiterObject(sim, numInputs, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_delay_object(sim, lines):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createDelayObject(sim, lines, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_amplitude_panner_object(sim):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createAmplitudePannerObject(sim, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_world_object(sim, hrtfPath):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)
	hrtfPath = getattr(hrtfPath, 'handle', hrtfPath)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createWorldObject(sim, hrtfPath, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

def create_source_object(sim, environment):
	sim = getattr(sim, 'handle', sim)
	if isinstance(sim, collections.Sized):
		sim = (LavSimulation*len(sim))(*sim)
	environment = getattr(environment, 'handle', environment)
	if isinstance(environment, collections.Sized):
		environment = (LavObject*len(environment))(*environment)

	destination = ctypes.POINTER(_libaudioverse.LavObject)()
	err = _libaudioverse.Lav_createSourceObject(sim, environment, 		ctypes.byref(destination))
	if err != _libaudioverse.Lav_ERROR_NONE:
		raise make_error_from_code(err)
	retval = []
	retval.append(getattr(destination, 'value', destination))
	return tuple(retval) if len(retval) > 1 else retval[0]

