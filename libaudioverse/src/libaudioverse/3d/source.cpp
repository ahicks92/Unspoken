/**Copyright (C) Austin Hicks, 2014
This file is part of Libaudioverse, a library for 3D and environmental audio simulation, and is released under the terms of the Gnu General Public License Version 3 or (at your option) any later version.
A copy of the GPL, as well as other important copyright and licensing information, may be found in the file 'LICENSE' in the root of the Libaudioverse repository.  Should this file be missing or unavailable to you, see <http://www.gnu.org/licenses/>.*/

#include <libaudioverse/3d/source.hpp>
#include <libaudioverse/3d/environment.hpp>
#include <libaudioverse/private/properties.hpp>
#include <libaudioverse/private/macros.hpp>
#include <libaudioverse/private/constants.hpp>
#include <libaudioverse/private/simulation.hpp>
#include <libaudioverse/private/creators.hpp>
#include <libaudioverse/private/memory.hpp>
#include <libaudioverse/nodes/panner.hpp>
#include <libaudioverse/libaudioverse.h>
#include <libaudioverse/libaudioverse_properties.h>
#include <libaudioverse/libaudioverse3d.h>
#include <libaudioverse/private/error.hpp>
#include <math.h>
#include <stdlib.h>
#include <glm/glm.hpp>
#include <memory>
#include <set>
#include <vector>
#include <map>

namespace libaudioverse_implementation {

SourceNode::SourceNode(std::shared_ptr<Simulation> simulation, std::shared_ptr<EnvironmentNode> environment): SubgraphNode(Lav_OBJTYPE_SOURCE_NODE, simulation) {
	input = createGainNode(simulation);
	input->resize(1, 1);
	input->appendInputConnection(0, 1);
	input->appendOutputConnection(0, 1);
	panner_node = createMultipannerNode(simulation, environment->getHrtf());
	panner_node->connect(0, environment->getOutputNode(), 0);
	this->environment = environment;
	//we have to read off these defaults manually, and it must always be the last thing in the constructor.
	getProperty(Lav_SOURCE_DISTANCE_MODEL).setIntValue(environment->getProperty(Lav_ENVIRONMENT_DEFAULT_DISTANCE_MODEL).getIntValue());
	getProperty(Lav_SOURCE_MAX_DISTANCE).setFloatValue(environment->getProperty(Lav_ENVIRONMENT_DEFAULT_MAX_DISTANCE).getFloatValue());
	getProperty(Lav_SOURCE_PANNER_STRATEGY).setIntValue(environment->getProperty(Lav_ENVIRONMENT_DEFAULT_PANNER_STRATEGY).getIntValue());
	getProperty(Lav_SOURCE_SIZE).setFloatValue(environment->getProperty(Lav_ENVIRONMENT_DEFAULT_SIZE).getFloatValue());
	getProperty(Lav_SOURCE_REVERB_DISTANCE).setFloatValue(environment->getProperty(Lav_ENVIRONMENT_DEFAULT_REVERB_DISTANCE).getFloatValue());
	input->connect(0, panner_node, 0);
	setInputNode(input);
	
	//Configure tyhe effect send panners.
	std::shared_ptr<AmplitudePannerNode> p;
	p = std::static_pointer_cast<AmplitudePannerNode>(createAmplitudePannerNode(simulation));
	p->configureStandardChannelMap(2);
	effect_panners.push_back(p);
	p = std::static_pointer_cast<AmplitudePannerNode>(createAmplitudePannerNode(simulation));
	p->configureStandardChannelMap(4);
	effect_panners.push_back(p);
	p = std::static_pointer_cast<AmplitudePannerNode>(createAmplitudePannerNode(simulation));
	p->configureStandardChannelMap(6);
	effect_panners.push_back(p);
	p = std::static_pointer_cast<AmplitudePannerNode>(createAmplitudePannerNode(simulation));
	p->configureStandardChannelMap(8);
	effect_panners.push_back(p);
	//Actually connect the input to them.
	for(auto &i: effect_panners) input->connect(0, i, 0);
}

void SourceNode::forwardProperties() {
	panner_node->forwardProperty(Lav_PANNER_STRATEGY, std::static_pointer_cast<Node>(shared_from_this()), Lav_SOURCE_PANNER_STRATEGY);
}

std::shared_ptr<Node> createSourceNode(std::shared_ptr<Simulation> simulation, std::shared_ptr<EnvironmentNode> environment) {
	auto temp = standardNodeCreation<SourceNode>(simulation, environment);
	temp->forwardProperties();
	environment->registerSourceForUpdates(temp);
	return temp;
}

SourceNode::~SourceNode() {
	//Since connections are currently strong, break them.
	panner_node->isolate();
	//Also isolate all of the panners in the effect sends.
	for(auto &i: effect_panners) i->isolate();
	for(auto &i: outgoing_effects) i.second->isolate();
	for(auto &i: outgoing_effects_reverb) i.second->isolate();
}

void SourceNode::feedEffect(int which) {
	if(outgoing_effects.count(which) || outgoing_effects_reverb.count(which)) return; //already feeding, so no-op.
	auto &info = environment->getEffectSend(which);
	auto gain = createGainNode(simulation);
	gain->resize(info.channels, info.channels);
	gain->appendInputConnection(0, info.channels);
	gain->appendOutputConnection(0, info.channels);
	if(info.is_reverb) outgoing_effects_reverb[which] = gain;
	else outgoing_effects[which] = gain;
	auto pan = getPannerForEffectChannels(info.channels);
	pan->connect(0, gain, 0);
	auto out = environment->getOutputNode();
	gain->connect(0, out, which+1);
	//By forwarding this to the panner, we can control only one object. This prevents a great deal of iteration.
	gain->forwardProperty(Lav_NODE_STATE, panner_node, Lav_NODE_STATE);
}

void SourceNode::stopFeedingEffect(int which) {
	std::shared_ptr<Node> isolating = nullptr;
	if(outgoing_effects.count(which)) {
		isolating = outgoing_effects[which];
		outgoing_effects.erase(which);
	}
	else if(outgoing_effects_reverb.count(which)) {
		isolating = outgoing_effects_reverb[which];
		outgoing_effects_reverb.erase(which);
	}
	if(isolating) isolating->isolate();
}

std::shared_ptr<Node> SourceNode::getPannerForEffectChannels(int channels) {
	switch(channels) {
		case 1: return input;
		case 2: return effect_panners[0];
		case 4: return effect_panners[1];
		case 6: return effect_panners[2];
		case 8: return effect_panners[3];
		default: return nullptr;
	}
}

//helper function: calculates gains given distance models.
float calculateGainForDistanceModel(int model, float distance, float maxDistance, float referenceDistance) {
	float retval = 1.0f;
	float adjustedDistance = std::max<float>(0.0f, distance-referenceDistance);
		if(adjustedDistance > maxDistance) {
		retval = 0.0f;
	}
	else {
		switch(model) {
			case Lav_DISTANCE_MODEL_LINEAR: retval = 1.0f-(adjustedDistance/maxDistance); break;
			case Lav_DISTANCE_MODEL_EXPONENTIAL: retval = 1.0f/adjustedDistance; break;
			case Lav_DISTANCE_MODEL_INVERSE_SQUARE: retval = 1.0f/(adjustedDistance*adjustedDistance); break;
		}
	}

	//safety clamping.  Some of the equations above will go negative after max_distance.
	if(retval < 0.0f) retval = 0.0f;
	return retval;
}

void SourceNode::update(EnvironmentInfo &env) {
	//first, extract the vector of our position.
	const float* pos = getProperty(Lav_3D_POSITION).getFloat3Value();
	bool isHeadRelative = getProperty(Lav_SOURCE_HEAD_RELATIVE).getIntValue() == 1;
	glm::vec4 npos;
	if(isHeadRelative) npos = glm::vec4(pos[0], pos[1], pos[2], 1.0);
	else npos = env.world_to_listener_transform*glm::vec4(pos[0], pos[1], pos[2], 1.0f);
	//npos is now easy to work with.
	float distance = glm::length(npos);
	float maxDistance = getProperty(Lav_SOURCE_MAX_DISTANCE).getFloatValue();
	//We get maxDistance early so we can do the state update; if this says cull, we bail out now.
	handleStateUpdates(distance > maxDistance);
	if(culled) return;
	float xz = sqrtf(npos.x*npos.x+npos.z*npos.z);
	//elevation and azimuth, in degrees.
	float elevation = atan2f(npos.y, xz)/PI*180.0f;
	float azimuth = atan2(npos.x, -npos.z)/PI*180.0f;
	if(elevation > 90.0f) elevation = 90.0f;
	if(elevation < -90.0f) elevation = -90.0f;
	int distanceModel = getProperty(Lav_SOURCE_DISTANCE_MODEL).getIntValue();
	float referenceDistance = getProperty(Lav_SOURCE_SIZE).getFloatValue();
	float reverbDistance = getProperty(Lav_SOURCE_REVERB_DISTANCE).getFloatValue();
	float dryGain = calculateGainForDistanceModel(distanceModel, distance, maxDistance, referenceDistance);
	float unscaledReverbMultiplier = 1.0f-calculateGainForDistanceModel(distanceModel, distance, reverbDistance, 0.0f);
	float minReverbLevel = getProperty(Lav_SOURCE_MIN_REVERB_LEVEL).getFloatValue();
	float maxReverbLevel = getProperty(Lav_SOURCE_MAX_REVERB_LEVEL).getFloatValue();
	float scaledReverbMultiplier = minReverbLevel+(maxReverbLevel-minReverbLevel)*unscaledReverbMultiplier;
	float reverbGain = dryGain*scaledReverbMultiplier;
	//Question: are we going to actually send to a reverb? If so, make room in the dry gain for it.
	if(outgoing_effects_reverb.size()) {
		dryGain *= 1.0f-scaledReverbMultiplier;
		//And also make sure that we distribute it equally among them.
		reverbGain /= outgoing_effects_reverb.size();
	}
	//Bring in mul.
	float mul = getProperty(Lav_NODE_MUL).getFloatValue();
	dryGain*=mul;
	reverbGain*=mul;
	//Set the output panner, a multipanner.
	panner_node->getProperty(Lav_PANNER_AZIMUTH).setFloatValue(azimuth);
	panner_node->getProperty(Lav_PANNER_ELEVATION).setFloatValue(elevation);
	panner_node->getProperty(Lav_PANNER_DISTANCE).setFloatValue(distance);
	panner_node ->getProperty(Lav_NODE_MUL).setFloatValue(dryGain);
	//Set the panners for effect sends; note that these are not multipanners and only have azimuth and elevation.
	for(auto &i: effect_panners) {
		i->getProperty(Lav_PANNER_AZIMUTH).setFloatValue(azimuth);
		i->getProperty(Lav_PANNER_ELEVATION).setFloatValue(elevation);
	}
	//Set the gains for non-reverb sends.
	for(auto &i: outgoing_effects) {
		i.second->getProperty(Lav_NODE_MUL).setFloatValue(dryGain);
	}
	//And reverb sends.
	for(auto &i: outgoing_effects_reverb) {
		i.second->getProperty(Lav_NODE_MUL).setFloatValue(reverbGain);
	}
}

void SourceNode::handleStateUpdates(bool shouldCull) {
	//This has four cases.
	//If we are culled and need to be culled, we need to set our input's state.
	if(culled && shouldCull) {
		if(getState() != Lav_NODESTATE_PAUSED) input->setState(Lav_NODESTATE_ALWAYS_PLAYING);
		else input->setState(Lav_NODESTATE_PAUSED);
	}
	//If we are culled and don't need to be culled, input goes to playing and panner goes to whatever we are.
	else if(culled && shouldCull == false) {
		input->setState(Lav_NODESTATE_PLAYING);
		panner_node->setState(getState());
	}
	//If we aren't culled but need to be, then cull us.
	if(culled == false && shouldCull) {
		//Input goes to either paused or always playing, panner goes to paused.
		panner_node->setState(Lav_NODESTATE_PAUSED);
		if(getState() != Lav_NODESTATE_PAUSED) input->setState(Lav_NODESTATE_ALWAYS_PLAYING);
		else input->setState(Lav_NODESTATE_PAUSED);
	}
	//Otherwise, the panner reflects our state.
	else panner_node->setState(getState());
}

void SourceNode::visitDependenciesUnconditional(std::function<void(std::shared_ptr<Job>&)> &pred) {
	SubgraphNode::visitDependenciesUnconditional(pred);
	auto j = std::static_pointer_cast<Job>(panner_node);
	pred(j);
}

Lav_PUBLIC_FUNCTION LavError Lav_createSourceNode(LavHandle simulationHandle, LavHandle environmentHandle, LavHandle* destination) {
	PUB_BEGIN
	auto simulation = incomingObject<Simulation>(simulationHandle);
	LOCK(*simulation);
	auto retval = createSourceNode(simulation, incomingObject<EnvironmentNode>(environmentHandle));
	*destination = outgoingObject<Node>(retval);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_sourceNodeFeedEffect(LavHandle nodeHandle, int effect) {
	PUB_BEGIN
	auto s = incomingObject<SourceNode>(nodeHandle);
	LOCK(*s);
	//Note that external indexes are 1-based.
	s->feedEffect(effect-1);
	PUB_END
}

Lav_PUBLIC_FUNCTION LavError Lav_sourceNodeStopFeedingEffect(LavHandle nodeHandle, int effect) {
	PUB_BEGIN
	auto s = incomingObject<SourceNode>(nodeHandle);
	LOCK(*s);
	//Note that external indexes are 1-based.
	s->stopFeedingEffect(effect-1);
	PUB_END
}

}