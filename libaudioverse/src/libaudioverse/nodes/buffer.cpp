/**Copyright (C) Austin Hicks, 2014-2016
This file is part of Libaudioverse, a library for realtime audio applications.
This code is dual-licensed.  It is released under the terms of the Mozilla Public License version 2.0 or the Gnu General Public License version 3 or later.
You may use this code under the terms of either license at your option.
A copy of both licenses may be found in license.gpl and license.mpl at the root of this repository.
If these files are unavailable to you, see either http://www.gnu.org/licenses/ (GPL V3 or later) or https://www.mozilla.org/en-US/MPL/2.0/ (MPL 2.0).*/
#include <math.h>
#include <stdlib.h>
#include <libaudioverse/libaudioverse.h>
#include <libaudioverse/libaudioverse_properties.h>
#include <libaudioverse/nodes/buffer.hpp>
#include <libaudioverse/private/node.hpp>
#include <libaudioverse/private/simulation.hpp>
#include <libaudioverse/private/properties.hpp>
#include <libaudioverse/private/dspmath.hpp>
#include <libaudioverse/private/macros.hpp>
#include <libaudioverse/private/memory.hpp>
#include <libaudioverse/private/constants.hpp>
#include <libaudioverse/private/buffer.hpp>
#include <limits>
#include <vector>
#include <memory>

namespace libaudioverse_implementation {

BufferNode::BufferNode(std::shared_ptr<Simulation> simulation): Node(Lav_OBJTYPE_BUFFER_NODE, simulation, 0, 1),
player(simulation->getBlockSize(), simulation->getSr()) {
	appendOutputConnection(0, 1);
	getProperty(Lav_BUFFER_BUFFER).setPostChangedCallback([&] () {bufferChanged();});
	end_callback = std::make_shared<Callback<void()>>();
}

std::shared_ptr<Node> createBufferNode(std::shared_ptr<Simulation> simulation) {
	return standardNodeCreation<BufferNode>(simulation);
}

void BufferNode::bufferChanged() {
	auto buff = getProperty(Lav_BUFFER_BUFFER).getBufferValue();
	double maxPosition = 0.0;
	int newChannels= 0;
	if(buff==nullptr) {
		resize(0, 1);
		getOutputConnection(0)->reconfigure(0, 1);
	}
	else {
		newChannels = buff->getChannels() > 0 ? buff->getChannels() : 1;
		resize(0, newChannels);
		getOutputConnection(0)->reconfigure(0, newChannels);
		maxPosition =buff->getDuration();
	}
	player.setBuffer(buff);
	getProperty(Lav_BUFFER_POSITION).setDoubleValue(0.0); //the callback handles changing everything else.
	getProperty(Lav_BUFFER_POSITION).setDoubleRange(0.0, maxPosition);
}

void BufferNode::positionChanged() {
	player.setPosition(getProperty(Lav_BUFFER_POSITION).getDoubleValue());
}

void BufferNode::process() {
	auto buff = getProperty(Lav_BUFFER_BUFFER).getBufferValue();
	if(buff == nullptr) return;
	if(werePropertiesModified(this, Lav_BUFFER_POSITION)) player.setPosition(getProperty(Lav_BUFFER_POSITION).getDoubleValue());
	if(werePropertiesModified(this, Lav_BUFFER_RATE)) player.setRate(getProperty(Lav_BUFFER_RATE).getDoubleValue());
	if(werePropertiesModified(this, Lav_BUFFER_LOOPING)) player.setIsLooping(getProperty(Lav_BUFFER_LOOPING).getIntValue() != 0);
	int prevEndedCount = player.getEndedCount();
	player.process(buff->getChannels(), &output_buffers[0]);
	getProperty(Lav_BUFFER_POSITION).setDoubleValue(player.getPosition());
	for(int i = player.getEndedCount(); i > prevEndedCount; i--) {
		simulation->enqueueTask([=] () {(*end_callback)();});
	}
	getProperty(Lav_BUFFER_ENDED_COUNT).setIntValue(player.getEndedCount());
}

//begin public api
Lav_PUBLIC_FUNCTION LavError Lav_createBufferNode(LavHandle simulationHandle, LavHandle* destination) {
	PUB_BEGIN
	auto simulation = incomingObject<Simulation>(simulationHandle);
	LOCK(*simulation);
	auto retval = createBufferNode(simulation);
	*destination = outgoingObject<Node>(retval);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_bufferNodeSetEndCallback(LavHandle nodeHandle, LavParameterlessCallback callback, void* userdata) {
	PUB_BEGIN
	auto n = incomingObject<BufferNode>(nodeHandle);
	if(callback) {
		n->end_callback->setCallback(wrapParameterlessCallback(n, callback, userdata));
	}
	else n->end_callback->clear();
	PUB_END
}

}