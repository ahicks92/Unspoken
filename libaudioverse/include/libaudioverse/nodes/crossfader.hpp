/**Copyright (C) Austin Hicks, 2014
This file is part of Libaudioverse, a library for 3D and environmental audio simulation, and is released under the terms of the Gnu General Public License Version 3 or (at your option) any later version.
A copy of the GPL, as well as other important copyright and licensing information, may be found in the file 'LICENSE' in the root of the Libaudioverse repository.  Should this file be missing or unavailable to you, see <http://www.gnu.org/licenses/>.*/
#pragma once
#include "../private/node.hpp"
#include <memory>
namespace libaudioverse_implementation {

class Simulation;
class Node;

class CrossfaderNode: public Node {
	public:
	CrossfaderNode(std::shared_ptr<Simulation> sim, int channels, int inputs);
	void crossfade(float duration, int input);
	//Immediately finish the current crossfade.
	void finishCrossfade();
	void process();
	private:
	int channels = 0;
	int current = 0, target = 0;
	float current_weight = 1.0, target_weight = 0.0, delta = 0.0;
	bool crossfading = false;
};

}