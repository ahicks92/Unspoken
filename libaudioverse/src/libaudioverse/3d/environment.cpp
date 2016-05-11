/**Copyright (C) Austin Hicks, 2014-2016
This file is part of Libaudioverse, a library for realtime audio applications.
This code is dual-licensed.  It is released under the terms of the Mozilla Public License version 2.0 or the Gnu General Public License version 3 or later.
You may use this code under the terms of either license at your option.
A copy of both licenses may be found in license.gpl and license.mpl at the root of this repository.
If these files are unavailable to you, see either http://www.gnu.org/licenses/ (GPL V3 or later) or https://www.mozilla.org/en-US/MPL/2.0/ (MPL 2.0).*/
#include <libaudioverse/3d/source.hpp>
#include <libaudioverse/3d/environment.hpp>
#include <libaudioverse/nodes/gain.hpp>
#include <libaudioverse/nodes/buffer.hpp>
#include <libaudioverse/private/properties.hpp>
#include <libaudioverse/private/macros.hpp>
#include <libaudioverse/private/simulation.hpp>
#include <libaudioverse/private/memory.hpp>
#include <libaudioverse/private/hrtf.hpp>
#include <libaudioverse/private/buffer.hpp>
#include <libaudioverse/private/helper_templates.hpp>
#include <libaudioverse/libaudioverse.h>
#include <libaudioverse/libaudioverse_properties.h>
#include <libaudioverse/libaudioverse3d.h>
#include <stdlib.h>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/transform.hpp>
#include <algorithm>
#include <vector>
#include <set>
#include <tuple>
#include <memory>

namespace libaudioverse_implementation {

EnvironmentNode::EnvironmentNode(std::shared_ptr<Simulation> simulation, std::shared_ptr<HrtfData> hrtf): Node(Lav_OBJTYPE_ENVIRONMENT_NODE, simulation, 0, 8)  {
	this->hrtf = hrtf;
	int channels = getProperty(Lav_ENVIRONMENT_OUTPUT_CHANNELS).getIntValue();
	appendOutputConnection(0, channels);
	//Allocate the 8 internal buffers.
	for(int i = 0; i < 8; i++) source_buffers.push_back(allocArray<float>(simulation->getBlockSize()));
	environment_info.world_to_listener_transform = glm::lookAt(
		glm::vec3(0.0f, 0.0f, 0.0f),
		glm::vec3(0.0f, 0.0f, -1.0f),
		glm::vec3(0.0f, 1.0f, 0.0f));
	setShouldZeroOutputBuffers(false);
}

std::shared_ptr<EnvironmentNode> createEnvironmentNode(std::shared_ptr<Simulation> simulation, std::shared_ptr<HrtfData> hrtf) {
	auto ret = standardNodeCreation<EnvironmentNode>(simulation, hrtf);
	simulation->registerNodeForWillTick(ret);
	return ret;
}

EnvironmentNode::~EnvironmentNode() {
	for(auto p: source_buffers) freeArray(p);
}

void EnvironmentNode::willTick() {
	if(werePropertiesModified(this, Lav_ENVIRONMENT_OUTPUT_CHANNELS)) {
		int channels = getProperty(Lav_ENVIRONMENT_OUTPUT_CHANNELS).getIntValue();
		getOutputConnection(0)->reconfigure(0, channels);
	}
	if(werePropertiesModified(this, Lav_3D_POSITION, Lav_3D_ORIENTATION)) {
		//update the matrix.
		//Important: look at the glsl constructors. Glm copies them, and there is nonintuitive stuff here.
		const float* pos = getProperty(Lav_3D_POSITION).getFloat3Value();
		const float* atup = getProperty(Lav_3D_ORIENTATION).getFloat6Value();
		auto at = glm::vec3(atup[0], atup[1], atup[2]);
		auto up = glm::vec3(atup[3], atup[4], atup[5]);
		auto right = glm::cross(at, up);
		auto m = glm::mat4(
		right.x, up.x, -at.x, 0,
		right.y, up.y, -at.y, 0,
		right.z, up.z, -at.z, 0,
		0, 0, 0, 1);
		//Above is a rotation matrix, which works presuming the player is at (0, 0).
		//Pass the translation through it, so that we can bake the translation in.
		auto posvec = m*glm::vec4(pos[0], pos[1], pos[2], 1.0f);
		//[column][row] because GLSL.
		m[3][0] = -posvec.x;
		m[3][1] = -posvec.y;
		m[3][2] = -posvec.z;
		environment_info.world_to_listener_transform = m;
	}
	environment_info.distance_model = getProperty(Lav_ENVIRONMENT_DISTANCE_MODEL).getIntValue();
	if(environment_info.distance_model == Lav_DISTANCE_MODEL_DELEGATE) environment_info.distance_model = Lav_DISTANCE_MODEL_LINEAR;
	environment_info.panning_strategy = getProperty(Lav_ENVIRONMENT_PANNING_STRATEGY).getIntValue();
	if(environment_info.panning_strategy == Lav_PANNING_STRATEGY_DELEGATE) environment_info.panning_strategy = Lav_PANNING_STRATEGY_STEREO;
	//give the new environment to the sources.
	//this is a set of weak pointers.
	filterWeakPointers(sources, [&](std::shared_ptr<SourceNode> &s) {
		s->update(environment_info);
	});
	for(auto p: source_buffers) std::fill(p, p+block_size, 0.0f);
}

void EnvironmentNode::process() {
	for(int i = 0; i < source_buffers.size(); i++) std::copy(source_buffers[i], source_buffers[i]+block_size, output_buffers[i]);
}

std::shared_ptr<HrtfData> EnvironmentNode::getHrtf() {
	return hrtf;
}

void EnvironmentNode::registerSourceForUpdates(std::shared_ptr<SourceNode> source, bool useEffectSends) {
	sources.insert(source);
	if(useEffectSends) {
		for(int i = 0; i < effect_sends.size(); i++) {
			if(effect_sends[i].connect_by_default) source->feedEffect(i);
		}
	}
	//Sources count as dependencies, so we need to invalidate.
	simulation->invalidatePlan();
}

void EnvironmentNode::playAsync(std::shared_ptr<Buffer> buffer, float x, float y, float z, bool isDry) {
	auto e = std::static_pointer_cast<EnvironmentNode>(shared_from_this());
	std::shared_ptr<Node> b;
	std::shared_ptr<SourceNode> s;
	bool fromCache = false;
	if(play_async_source_cache.empty()) {
		s = std::static_pointer_cast<SourceNode>(createSourceNode(simulation, e));
		b = createBufferNode(simulation);
	}
	else {
		std::tie(b, s) = play_async_source_cache.back();
		play_async_source_cache.pop_back();
		fromCache = true;
	}
	b->getProperty(Lav_BUFFER_BUFFER).setBufferValue(buffer);
	if(fromCache == false) b->connect(0, s, 0);
	b->getProperty(Lav_BUFFER_POSITION).setDoubleValue(0.0);
	s->getProperty(Lav_3D_POSITION).setFloat3Value(x, y, z);
		if(isDry) {
		for(int i = 0; i < effect_sends.size(); i++) {
			s->stopFeedingEffect(i);
		}
	}
	else {
		//This might be from the cache and previously used as dry.
		for(int i = 0; i < effect_sends.size(); i++) {
			s->feedEffect(i);
		}
	}
	if(fromCache) s->setState(Lav_NODESTATE_PLAYING);
	auto simulation = this->simulation;
	//We've just done a bunch of stuff that invalidates the plan, so maybe we can squeeze in a bit more.
	//If we update the source, it might cull.  We can then reset it to avoid HRTF crossfading.
	s->update(environment_info);
	s->reset(); //Avoid crossfading the hrtf.	
	//This needs rewriting on whatever we replace events with.
	/*b->getEvent(Lav_BUFFER_END_EVENT).setHandler([b, e, s, simulation] (std::shared_ptr<Node> unused1, void* unused2) mutable {
		//Recall that events do not hold locks when fired.
		//So lock the simulation.
		LOCK(*simulation);
		if(e->play_async_source_cache.size() < e->play_async_source_cache_limit) {
			//Sleep the source, clear the buffer.
			s->setState(Lav_NODESTATE_PAUSED);
			b->getProperty(Lav_BUFFER_BUFFER).setBufferValue(nullptr);
			e->play_async_source_cache.emplace_back(b, s);
		}
		else {
			//Otherwise, let go.
			s->isolate();
			b->isolate();
		}
		//We let go of them so that they can delete if they want to.
		//We don't want to extend lifetime guarantees into the event firing, as this event may remain set for a time.
		b.reset();
		s.reset();
		e.reset();
	});*/
}

int EnvironmentNode::addEffectSend(int channels, bool isReverb, bool connectByDefault) {
	if(channels != 1 && channels != 2 && channels != 4 && channels != 6 && channels != 8)
	ERROR(Lav_ERROR_RANGE, "Channel count for an effect send needs to be 1, 2, 4, 6, or 8.");
	if(channels != 4 && isReverb)
	ERROR(Lav_ERROR_RANGE, "Reverb effects sends must have 4 channels.");
	EffectSendConfiguration send;
	send.channels = channels;
	send.start = (int)source_buffers.size();
	send.is_reverb = isReverb;
	send.connect_by_default = connectByDefault;
	//Resize the output gain node to have room, and append new connections.
	int oldSize = source_buffers.size();
	int newSize = oldSize+send.channels;
	resize(0, newSize);
	appendOutputConnection(oldSize, send.channels);
	for(int i = 0; i < send.channels; i++) source_buffers.push_back(allocArray<float>(simulation->getBlockSize()));
	int index = effect_sends.size();
	effect_sends.push_back(send);
	for(auto &i: sources) {
		auto s = i.lock();
		if(s) s->feedEffect(index);
	}
	return index;
}

EffectSendConfiguration& EnvironmentNode::getEffectSend(int which) {
	if(which < 0 || which > effect_sends.size()) ERROR(Lav_ERROR_RANGE, "Invalid effect send.");
	return effect_sends[which];
}

int EnvironmentNode::getEffectSendCount() {
	return (int)effect_sends.size();
}

//begin public api

Lav_PUBLIC_FUNCTION LavError Lav_createEnvironmentNode(LavHandle simulationHandle, const char*hrtfPath, LavHandle* destination) {
	PUB_BEGIN
	auto simulation = incomingObject<Simulation>(simulationHandle);
	LOCK(*simulation);
	auto hrtf = createHrtfFromString(hrtfPath, simulation->getSr());
	auto retval = createEnvironmentNode(simulation, hrtf);
	*destination = outgoingObject<Node>(retval);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_environmentNodePlayAsync(LavHandle nodeHandle, LavHandle bufferHandle, float x, float y, float z, int isDry) {
	PUB_BEGIN
	auto e = incomingObject<EnvironmentNode>(nodeHandle);
	auto b = incomingObject<Buffer>(bufferHandle);
	LOCK(*e);
	//==1 gets rid of a VC++ warning.
	e->playAsync(b, x, y, z, isDry == 1);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_environmentNodeAddEffectSend(LavHandle nodeHandle, int channels, int isReverb, int connectByDefault, int* destination) {
	PUB_BEGIN
	auto e = incomingObject<EnvironmentNode>(nodeHandle);
	LOCK(*e);
	//The == 1 gets rid of a VC++ performance warning.
	//We add 1 here because the external world needs to deal in indexes that are the same as the outputs to use.
	//The internal world uses 0-based indexes because it rarely deals with the environment's outputs.
	*destination = e->addEffectSend(channels, isReverb == 1, connectByDefault == 1)+1;
	PUB_END
}

}