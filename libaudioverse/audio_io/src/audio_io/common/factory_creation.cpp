#include <audio_io/audio_io.hpp>
#include <audio_io/private/audio_outputs.hpp>
#include <audio_io/private/logging.hpp>
#include <memory>
#include <utility>

namespace audio_io {
//the functionality here is all public.

const std::pair<const char*, const implementation::OutputDeviceFactoryCreationFunction> outputDeviceFactoryCreators[] = {
	#ifdef AUDIO_IO_USE_WASAPI
	{"Wasapi", implementation::createWasapiOutputDeviceFactory},
	#endif
	#ifdef AUDIO_IO_USE_WINMM
	{"winmm", implementation::createWinmmOutputDeviceFactory},
	#endif
	#ifdef AUDIO_IO_USE_ALSA
	{"alsa", implementation::createAlsaOutputDeviceFactory},
	#endif
};

std::unique_ptr<OutputDeviceFactory> getOutputDeviceFactory() {
	OutputDeviceFactory* fact=nullptr;
	for(int i=0; i < sizeof(outputDeviceFactoryCreators)/sizeof(outputDeviceFactoryCreators[0]); i++) {
		implementation::logInfo("Attempting to use device factory %s.", outputDeviceFactoryCreators[i].first);
		fact = outputDeviceFactoryCreators[i].second();
		if(fact) break;
	}
	if(fact == nullptr) {
		implementation::logCritical("Failed to create a device factory.  Audio output is unavailable on this system.");
		throw NoBackendError();
	}
	return std::unique_ptr<OutputDeviceFactory>(fact);
}

}