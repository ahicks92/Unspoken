@echo off
del *.nvda-addon
cd libaudioverse
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE:STRING=Release -G "NMake Makefiles JOM" ..
jom
cd ../..
xcopy "libaudioverse/build/bindings/python/libaudioverse" "addon/globalPlugins/Unspoken/deps/libaudioverse" /i /y 
scons
