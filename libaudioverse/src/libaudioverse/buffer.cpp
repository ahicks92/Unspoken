/**Copyright (C) Austin Hicks, 2014
This file is part of Libaudioverse, a library for 3D and environmental audio simulation, and is released under the terms of the Gnu General Public License Version 3 or (at your option) any later version.
A copy of the GPL, as well as other important copyright and licensing information, may be found in the file 'LICENSE' in the root of the Libaudioverse repository.  Should this file be missing or unavailable to you, see <http://www.gnu.org/licenses/>.*/

#include <libaudioverse/libaudioverse.h>
#include <libaudioverse/private/file.hpp>
#include <libaudioverse/private/buffer.hpp>
#include <libaudioverse/private/simulation.hpp>
#include <libaudioverse/private/kernels.hpp>
#include <libaudioverse/private/memory.hpp>
#include <libaudioverse/private/error.hpp>
#include <libaudioverse/private/macros.hpp>
#include <algorithm>

namespace libaudioverse_implementation {

Buffer::Buffer(std::shared_ptr<Simulation> simulation): ExternalObject(Lav_OBJTYPE_BUFFER) {
	this->simulation = simulation;
}

std::shared_ptr<Buffer> createBuffer(std::shared_ptr<Simulation>simulation) {
	return std::shared_ptr<Buffer>(new Buffer(simulation), ObjectDeleter(simulation));
}

Buffer::~Buffer() {
	if(data) delete[] data;
	if(remixing_workspace) freeArray(remixing_workspace);
}

std::shared_ptr<Simulation> Buffer::getSimulation() {
	return simulation;
}

int Buffer::getLength() {
	return frames;
}

double Buffer::getDuration() {
	return frames / simulation->getSr();
}

int Buffer::getChannels() {
	return channels;
}

void Buffer::loadFromArray(int sr, int channels, int frames, float* inputData) {
	int simulationSr= (int)simulation->getSr();
	staticResamplerKernel(sr, simulationSr, channels, frames, inputData, &(this->frames), &data);
	if(data==nullptr) ERROR(Lav_ERROR_MEMORY);
	data_end=data+this->frames*channels;
	this->channels = channels;
}

int Buffer::writeData(int startFrame, int channels, int frames, float** outputs) {
	//Figure out how much we can write.
	int canWrite = std::max(startFrame-this->frames, 0);
	int willWrite = std::min(canWrite, frames);
	if(willWrite == 0) return 0;
	ensureRemixingWorkspace(channels*willWrite);
	audio_io::remixAudioInterleaved(willWrite, this->channels, data+this->channels*startFrame, channels, remixing_workspace);
	for(int i = 0; i < willWrite; i++) {
		for(int chan = 0; chan < channels; chan++) {
			outputs[chan][i] = remixing_workspace[chan*channels+i];
		}
	}
	return willWrite;
}

float Buffer::getSample(int frame, int channel) {
	return data[frame*channels+channel];
}

float Buffer::getSampleWithMixingMatrix(int frame, int channel, int maxChannels) {
	if(frame > this->frames) return 0.0f;
	ensureRemixingWorkspace(maxChannels);
	audio_io::remixAudioInterleaved(1, this->channels, data+frame*this->channels, maxChannels, remixing_workspace);
	return remixing_workspace[channel];
}

void Buffer::normalize() {
	float min = *std::min_element(data, data+channels*frames);
	float max = *std::max_element(data, data+channels*frames);
	float normfactor = std::max(abs(min), abs(max));
	normfactor = 1.0f/normfactor;
	scalarMultiplicationKernel(channels*frames, normfactor, data, data);
}

void Buffer::ensureRemixingWorkspace(int length) {
	if(remixing_workspace_length >= length) return;
	else {
		if(remixing_workspace) {
			freeArray(remixing_workspace);
			remixing_workspace = nullptr;
		}
		remixing_workspace = allocArray<float>(length);
	}
}

void Buffer::lock() {
	simulation->lock();
}

void Buffer::unlock() {
	simulation->unlock();
}

//begin public api

Lav_PUBLIC_FUNCTION LavError Lav_createBuffer(LavHandle simulationHandle, LavHandle* destination) {
	PUB_BEGIN
	auto simulation = incomingObject<Simulation>(simulationHandle);
	LOCK(*simulation);
	*destination = outgoingObject(createBuffer(simulation));
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferGetSimulation(LavHandle handle, LavHandle* destination) {
	PUB_BEGIN
	auto b= incomingObject<Buffer>(handle);
	*destination = outgoingObject(b->getSimulation());
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferLoadFromFile(LavHandle bufferHandle, const char* path) {
	PUB_BEGIN
	auto buff =incomingObject<Buffer>(bufferHandle);
	FileReader f{};
	f.open(path);
	float* data = allocArray<float>(f.getSampleCount());
	f.readAll(data);
	{
		LOCK(*buff);
		buff->loadFromArray(f.getSr(), f.getChannelCount(), f.getSampleCount()/f.getChannelCount(), data);
	}
	freeArray(data);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferLoadFromArray(LavHandle bufferHandle, int sr, int channels, int frames, float* data) {
	PUB_BEGIN
	auto buff=incomingObject<Buffer>(bufferHandle);
	LOCK(*buff);
	buff->loadFromArray(sr, channels, frames, data);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferNormalize(LavHandle bufferHandle) {
	PUB_BEGIN
	auto b = incomingObject<Buffer>(bufferHandle);
	LOCK(*b);
	b->normalize();
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferGetDuration(LavHandle bufferHandle, float* destination) {
	PUB_BEGIN
	auto b = incomingObject<Buffer>(bufferHandle);
	LOCK(*b);
	*destination = b->getDuration();
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferGetLengthInSamples(LavHandle bufferHandle, int* destination) {
	PUB_BEGIN
	auto b = incomingObject<Buffer>(bufferHandle);
	LOCK(*b);
	*destination = b->getLength();
	PUB_END
}

}