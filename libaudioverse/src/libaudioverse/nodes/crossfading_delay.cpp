/**Copyright (C) Austin Hicks, 2014
This file is part of Libaudioverse, a library for 3D and environmental audio simulation, and is released under the terms of the Gnu General Public License Version 3 or (at your option) any later version.
A copy of the GPL, as well as other important copyright and licensing information, may be found in the file 'LICENSE' in the root of the Libaudioverse repository.  Should this file be missing or unavailable to you, see <http://www.gnu.org/licenses/>.*/
#include <libaudioverse/libaudioverse.h>
#include <libaudioverse/libaudioverse_properties.h>
#include <libaudioverse/private/simulation.hpp>
#include <libaudioverse/private/node.hpp>
#include <libaudioverse/private/properties.hpp>
#include <libaudioverse/private/macros.hpp>
#include <libaudioverse/private/memory.hpp>
#include <libaudioverse/implementations/delayline.hpp>
#include <memory>

namespace libaudioverse_implementation {

class CrossfadingDelayNode: public Node {
	public:
	CrossfadingDelayNode(std::shared_ptr<Simulation> simulation, float maxDelay, int channels);
	~CrossfadingDelayNode();
	void process();
	protected:
	void delayChanged();
	void recomputeDelta();
	//These do not touch the line. They keep properties in sync.
	//updateDelayInSamples is called when delay changes; updateDelay when delay_samples changes.
	void updateDelaySamples();
	void updateDelay();
	//Flag to prevent "ping-pong" in the above callbacks.
	bool is_syncing_properties = false;
	//Either 0, Lav_DELAY_DELAY, or Lav_DELAY_DELAY_SAMPLES.
	int last_updated_delay_property = 0;
	unsigned int delay_line_length = 0;
	CrossfadingDelayLine **lines;
	int channels;
};

CrossfadingDelayNode::CrossfadingDelayNode(std::shared_ptr<Simulation> simulation, float maxDelay, int channels): Node(Lav_OBJTYPE_CROSSFADING_DELAY_NODE, simulation, channels, channels) {
	if(channels <= 0) ERROR(Lav_ERROR_RANGE, "lineCount must be greater than 0.");
	this->channels = channels;
	lines = new CrossfadingDelayLine*[channels];
	for(unsigned int i = 0; i < channels; i++) lines[i] = new CrossfadingDelayLine(maxDelay, simulation->getSr());
	getProperty(Lav_DELAY_DELAY).setFloatRange(0.0f, maxDelay);
	getProperty(Lav_DELAY_DELAY_SAMPLES).setDoubleRange(0.0, maxDelay*(double)simulation->getSr());
	//These callbacks make these two properties be linked, such that updating one updates the other.
	getProperty(Lav_DELAY_DELAY).setPostChangedCallback([&] () {updateDelaySamples();});
	getProperty(Lav_DELAY_DELAY_SAMPLES).setPostChangedCallback([&] () {updateDelay();});
	//finally, set the read-only max delay.
	getProperty(Lav_DELAY_DELAY_MAX).setFloatValue(maxDelay);
	//Setup as though we just changed delay.
	last_updated_delay_property = Lav_DELAY_DELAY;
	appendInputConnection(0, channels);
	appendOutputConnection(0, channels);
}

std::shared_ptr<Node> createCrossfadingDelayNode(std::shared_ptr<Simulation> simulation, float maxDelay, unsigned int channels) {
	return standardNodeCreation<CrossfadingDelayNode>(simulation, maxDelay, channels);
}

CrossfadingDelayNode::~CrossfadingDelayNode() {
	for(int i=0; i < channels; i++) delete lines[i];
	delete[] lines;
}

void CrossfadingDelayNode::recomputeDelta() {
	float time = getProperty(Lav_DELAY_INTERPOLATION_TIME).getFloatValue();
	for(int i = 0; i < channels; i++) lines[i]->setInterpolationTime(time);
}

void CrossfadingDelayNode::delayChanged() {
	if(last_updated_delay_property == Lav_DELAY_DELAY) {
		float newDelay = getProperty(Lav_DELAY_DELAY).getFloatValue();
		for(int i = 0; i < channels; i++) lines[i]->setDelay(newDelay);
	}
	else {
		int delayInSamples = (int)getProperty(Lav_DELAY_DELAY_SAMPLES).getDoubleValue();
		for(int i = 0; i < channels; i++) lines[i]->setDelayInSamples(delayInSamples);
	}
	last_updated_delay_property = 0;
}

void CrossfadingDelayNode::updateDelaySamples() {
	if(is_syncing_properties) return; //The other callback is why we were called.
	double newValue = getProperty(Lav_DELAY_DELAY).getFloatValue()*(double)simulation->getSr();
	is_syncing_properties = true;
	getProperty(Lav_DELAY_DELAY_SAMPLES).setDoubleValue(newValue);
	is_syncing_properties = false;
	last_updated_delay_property = Lav_DELAY_DELAY;
}

void CrossfadingDelayNode::updateDelay() {
	if(is_syncing_properties) return; //The other callback is why we were called.
	double newValue = getProperty(Lav_DELAY_DELAY_SAMPLES).getDoubleValue()/simulation->getSr();
	is_syncing_properties = true;
	getProperty(Lav_DELAY_DELAY).setFloatValue(newValue);
	is_syncing_properties = false;
	last_updated_delay_property = Lav_DELAY_DELAY_SAMPLES;
}

void CrossfadingDelayNode::process() {
	if(last_updated_delay_property) delayChanged();
	if(werePropertiesModified(this, Lav_DELAY_INTERPOLATION_TIME)) recomputeDelta();
	float feedback = getProperty(Lav_DELAY_FEEDBACK).getFloatValue();
	//optimize the common case of not having feedback.
	//the only difference between these blocks is in the advance line.
	if(feedback == 0.0f) {
		for(unsigned int output = 0; output < num_output_buffers; output++) {
			auto &line = *lines[output];
			line.processBuffer(block_size, input_buffers[output], output_buffers[output]);
		}
	}
	else {
		for(unsigned int output = 0; output < num_output_buffers; output++) {
			auto &line = *lines[output];
			for(unsigned int i = 0; i < block_size; i++) {
				output_buffers[output][i] = line.computeSample();
				line.advance(input_buffers[output][i]+output_buffers[output][i]*feedback);
			}
		}
	}
}

//begin public api
Lav_PUBLIC_FUNCTION LavError Lav_createCrossfadingDelayNode(LavHandle simulationHandle, float maxDelay, int channels, LavHandle* destination) {
	PUB_BEGIN
	auto simulation =incomingObject<Simulation>(simulationHandle);
	LOCK(*simulation);
	auto d = createCrossfadingDelayNode(simulation, maxDelay, channels);
	*destination = outgoingObject(d);
	PUB_END
}

}