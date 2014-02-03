from ctypes import POINTER, CFUNCTYPE, cdll, c_float, c_int, c_char_p, c_void_p, c_uint, c_double
import sys
import os

al_soft = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'soft_oal.dll'))
libsndfile = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libsndfile-1.dll'))
ca_module = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'camlorn_audio_c.dll'))

# Some constants from al.h that we need.
AL_NONE = 0
AL_INVERSE_DISTANCE = 0xD001
AL_INVERSE_DISTANCE_CLAMPED = 0xd002
AL_LINEAR_DISTANCE = 0xD003
AL_LINEAR_DISTANCE_CLAMPED = 0xD004
AL_EXPONENT_DISTANCE = 0xD005
AL_EXPONENT_DISTANCE_CLAMPED = 0xD006

#some constants from camlorn_audio:
#the error codes and the like.
CERROR_INVALIDHANDLE = -1
CERROR_COULDNOTDETERMINECAUSE = -2

#errors from the actual camlorn_audio proper.
NO_CONTEXT_ERROR= 1
UNSUPPORTED_CHANNEL_COUNT_ERROR= 2
ARGUMENT_OUT_OF_RANGE_ERROR= 3
COULD_NOT_CREATE_BUFFER_ERROR= 4
COULD_NOT_CREATE_SOURCE_ERROR= 5
COULD_NOT_CREATE_FILTER_ERROR = 6
COULD_NOT_CREATE_EFFECT_ERROR = 7
COULD_NOT_CREATE_AUXILIARY_EFFECT_SLOT_ERROR = 8
INTERNAL_FILE_ERROR = 9

CA_getLastErrorCode = CFUNCTYPE(c_char_p)(('CA_getLastErrorCode', ca_module))
CA_getLastErrorMessage = CFUNCTYPE(c_char_p)(('CA_getLastErrorMessage', ca_module))
CA_getLastErrorLine = CFUNCTYPE(c_int)(('CA_getLastErrorLine', ca_module))
CA_getLastErrorFile = CFUNCTYPE(c_char_p)(('CA_getLastErrorFile', ca_module))
CA_getLastErrorFunction = CFUNCTYPE(c_char_p)(('CA_getLastErrorFunction', ca_module))

#initialize camlorn_audio.
#the parameter order is hrtf, channels, frequency, backendOrder.
CA_initCamlornAudio = CFUNCTYPE(c_int, c_int, c_char_p, c_uint, c_char_p, c_int, c_uint, c_char_p)(('CA_initCamlornAudio', ca_module))


#the constructors

CA_newSound3d = CFUNCTYPE(c_void_p)(('CA_newSound3d', ca_module))

CA_newStreamingSound3d = CFUNCTYPE(c_void_p)(('CA_newStreamingSound3d', ca_module))

CA_newMusic = CFUNCTYPE(c_void_p)(('CA_newMusic', ca_module))

CA_newStreamingMusic = CFUNCTYPE(c_void_p)(('CA_newStreamingMusic', ca_module))


CA_newEcho = CFUNCTYPE(c_void_p)(('CA_newEcho', ca_module))

CA_newReverb = CFUNCTYPE(c_void_p)(('CA_newReverb', ca_module))

CA_newEaxReverb = CFUNCTYPE(c_void_p)(('CA_newEaxReverb', ca_module))

CA_newViewpoint = CFUNCTYPE(c_void_p)(('CA_newViewpoint', ca_module))

CA_newFilter = CFUNCTYPE(c_void_p)(('CA_newFilter', ca_module))

#frees any object returned by any camlorn_audio constructor.
CA_free = CFUNCTYPE(None, c_void_p)(('CA_free', ca_module))

#Error callbacks and handling
CA_ErrorCallbackFunction = CFUNCTYPE(c_int, c_char_p, c_int, c_int, c_char_p, c_int)

# the general cases, property getters and setters.
CA_SoundBase_play = CFUNCTYPE(c_int, c_void_p)(('CA_SoundBase_play', ca_module))
CA_SoundBase_pause = CFUNCTYPE(c_int, c_void_p)(('CA_SoundBase_pause', ca_module))
CA_SoundBase_setVolume = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_SoundBase_setVolume', ca_module))
CA_SoundBase_stop = CFUNCTYPE(c_int, c_void_p)(('CA_SoundBase_stop', ca_module))
CA_SourceHelper3D_setPosition = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_SourceHelper3D_setPosition', ca_module))
CA_SourceHelper3D_setVelocity = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_SourceHelper3D_setVelocity', ca_module))
CA_SourceHelper3D_setHeadRelative = CFUNCTYPE(c_int, c_void_p, c_int)(('CA_SourceHelper3D_setHeadRelative', ca_module))

CA_SoundBase_getLooping = CFUNCTYPE(c_int, c_void_p)(('CA_SoundBase_getLooping', ca_module))
CA_SoundBase_setLooping = CFUNCTYPE(c_int, c_void_p, c_int)(('CA_SoundBase_setLooping', ca_module))
CA_SoundBase_setPitchBend = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_SoundBase_setPitchBend', ca_module))
CA_SoundBase_seek = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_SoundBase_seek', ca_module))
CA_SoundBase_getLength = CFUNCTYPE(c_double, c_void_p)(('CA_SoundBase_getLength', ca_module))

CA_SourceHelper3D_setReferenceDistance = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_SourceHelper3D_setReferenceDistance', ca_module))
CA_SourceHelper3D_setRolloffFactor = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_SourceHelper3D_setRolloffFactor', ca_module))
CA_SourceHelper3D_setMaxDistance = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_SourceHelper3D_setMaxDistance', ca_module))
CA_SourceHelper3D_setDistanceModel = CFUNCTYPE(c_int, c_void_p, c_int)(('CA_SourceHelper3D_setDistanceModel', ca_module))

CA_FileSetter_setFile = CFUNCTYPE(c_int, c_void_p, c_char_p)(('CA_FileSetter_setFile', ca_module))

#EfxCapable
CA_EfxCapable_setDryFilter = CFUNCTYPE(c_int, c_void_p, c_void_p)(('CA_EfxCapable_setDryFilter', ca_module))
CA_EfxCapable_getDryFilter = CFUNCTYPE(c_void_p, c_void_p)(('CA_EfxCapable_getDryFilter', ca_module))
CA_EfxCapable_clearDryFilter = CFUNCTYPE(c_int, c_void_p)(('CA_EfxCapable_clearDryFilter', ca_module))
CA_EfxCapable_setFilterForSlot = CFUNCTYPE(c_int, c_void_p, c_void_p, c_uint)(('CA_EfxCapable_setFilterForSlot', ca_module))
CA_EfxCapable_getFilterForSlot = CFUNCTYPE(c_void_p, c_void_p, c_uint)(('CA_EfxCapable_getFilterForSlot', ca_module))
CA_EfxCapable_clearFilterForSlot = CFUNCTYPE(c_int, c_void_p, c_uint)(('CA_EfxCapable_clearFilterForSlot', ca_module))
CA_EfxCapable_setEffectForSlot = CFUNCTYPE(c_int, c_void_p, c_void_p, c_uint)(('CA_EfxCapable_setEffectForSlot', ca_module))
CA_EfxCapable_getEffectForSlot = CFUNCTYPE(c_void_p, c_void_p, c_uint)(('CA_EfxCapable_getEffectForSlot', ca_module))
CA_EfxCapable_clearEffectForSlot = CFUNCTYPE(c_int, c_void_p, c_uint)(('CA_EfxCapable_clearEffectForSlot', ca_module))
CA_EfxCapable_setAirAbsorptionFactor = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EfxCapable_setAirAbsorptionFactor', ca_module))

#filters.
CA_Filter_setFilterType = CFUNCTYPE(c_int, c_void_p, c_int)(('CA_Filter_setFilterType', ca_module))
CA_Filter_setGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Filter_setGain', ca_module))
CA_Filter_setGainHF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Filter_setGainHF', ca_module))
CA_Filter_setGainLF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Filter_setGainLF', ca_module))

#Echo
CA_Echo_setDelay = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Echo_setDelay', ca_module))
CA_Echo_setLRDelay = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Echo_setLRDelay', ca_module))
CA_Echo_setDamping = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Echo_setDamping', ca_module))
CA_Echo_setFeedback = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Echo_setFeedback', ca_module))
CA_Echo_setSpread = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Echo_setSpread', ca_module))

#Reverb
CA_Reverb_setReverbDensity = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setReverbDensity', ca_module))
CA_Reverb_setDiffusion = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setDiffusion', ca_module))
CA_Reverb_setGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setGain', ca_module))
CA_Reverb_setGainHF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setGainHF', ca_module))
CA_Reverb_setDecayTime = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setDecayTime', ca_module))
CA_Reverb_setDecayHFRatio = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setDecayHFRatio', ca_module))
CA_Reverb_setReflectionsGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setReflectionsGain', ca_module))
CA_Reverb_setReflectionsDelay = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setReflectionsDelay', ca_module))
CA_Reverb_setLateReverbGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setLateReverbGain', ca_module))
CA_Reverb_setLateReverbDelay = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setLateReverbDelay', ca_module))
CA_Reverb_setAirAbsorptionGainHF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setAirAbsorptionGainHF', ca_module))
CA_Reverb_setRoomRolloffFactor = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_Reverb_setRoomRolloffFactor', ca_module))
CA_Reverb_setDecayHFLimit = CFUNCTYPE(c_int, c_void_p, c_int)(('CA_Reverb_setDecayHFLimit', ca_module))

#EaxReverb
CA_EaxReverb_setReverbDensity = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setReverbDensity', ca_module))
CA_EaxReverb_setDiffusion = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setDiffusion', ca_module))
CA_EaxReverb_setGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setGain', ca_module))
CA_EaxReverb_setGainHF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setGainHF', ca_module))
CA_EaxReverb_setGainLF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setGainLF', ca_module))
CA_EaxReverb_setDecayTime = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setDecayTime', ca_module))
CA_EaxReverb_setDecayHFRatio = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setDecayHFRatio', ca_module))
CA_EaxReverb_setDecayLFRatio = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setDecayLFRatio', ca_module))
CA_EaxReverb_setReflectionsGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setReflectionsGain', ca_module))
CA_EaxReverb_setReflectionsDelay = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setReflectionsDelay', ca_module))
CA_EaxReverb_setLateReverbGain = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setLateReverbGain', ca_module))
CA_EaxReverb_setLateReverbDelay = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setLateReverbDelay', ca_module))
CA_EaxReverb_setEchoTime = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setEchoTime', ca_module))
CA_EaxReverb_setEchoDepth = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setEchoDepth', ca_module))
CA_EaxReverb_setModulationTime = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setModulationTime', ca_module))
CA_EaxReverb_setModulationDepth = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setModulationDepth', ca_module))
CA_EaxReverb_setAirAbsorptionGainHF = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setAirAbsorptionGainHF', ca_module))
CA_EaxReverb_setHFReference = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setHFReference', ca_module))
CA_EaxReverb_setLFReference = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setLFReference', ca_module))
CA_EaxReverb_setRoomRolloffFactor = CFUNCTYPE(c_int, c_void_p, c_float)(('CA_EaxReverb_setRoomRolloffFactor', ca_module))
CA_EaxReverb_setDecayHFLimit = CFUNCTYPE(c_int, c_void_p, c_int)(('CA_EaxReverb_setDecayHFLimit', ca_module))
CA_EaxReverb_setReflectionsPan = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_EaxReverb_setReflectionsPan', ca_module))
CA_EaxReverb_setLateReverbPan = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_EaxReverb_setLateReverbPan', ca_module))

#viewpoints.
CA_Viewpoint_setAtVector = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_Viewpoint_setAtVector', ca_module))
CA_Viewpoint_setUpVector = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_Viewpoint_setUpVector', ca_module))
CA_Viewpoint_setOrientation = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float, c_float, c_float, c_float)(('CA_Viewpoint_setOrientation', ca_module))
CA_Viewpoint_setVelocity = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_Viewpoint_setVelocity', ca_module))
CA_Viewpoint_setPosition = CFUNCTYPE(c_int, c_void_p, c_float, c_float, c_float)(('CA_Viewpoint_setPosition', ca_module))
CA_Viewpoint_makeActive = CFUNCTYPE(c_int, c_void_p)(('CA_Viewpoint_makeActive', ca_module))
CA_Viewpoint_isActive = CFUNCTYPE(c_int, c_void_p)(('CA_Viewpoint_isActive', ca_module))
