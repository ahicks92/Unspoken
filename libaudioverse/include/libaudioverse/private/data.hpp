/**Copyright (C) Austin Hicks, 2014-2016
This file is part of Libaudioverse, a library for realtime audio applications.
This code is dual-licensed.  It is released under the terms of the Mozilla Public License version 2.0 or the Gnu General Public License version 3 or later.
You may use this code under the terms of either license at your option.
A copy of both licenses may be found in license.gpl and license.mpl at the root of this repository.
If these files are unavailable to you, see either http://www.gnu.org/licenses/ (GPL V3 or later) or https://www.mozilla.org/en-US/MPL/2.0/ (MPL 2.0).*/
#pragma once

namespace libaudioverse_implementation {

//contains the extern declarations for various static data.

//This is the HRTF array, which is autogenerated by a build step as needed.
extern char default_hrtf[];
extern unsigned int default_hrtf_size;

//These are the default panning maps, used by things like the multipanner.
extern float standard_panning_map_stereo[];
extern float standard_panning_map_surround40[];
extern float standard_panning_map_surround51[];
extern float standard_panning_map_surround71[];

}