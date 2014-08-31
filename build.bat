@echo off
cd libaudioverse
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE:STRING=Release -G "NMake Makefiles JOM" ..
jom /j20
cd ../..
xcopy "libaudioverse/build/bindings/python/libaudioverse" "addon/globalPlugins/Unspoken/libaudioverse" /i /s /e /y 
scons
