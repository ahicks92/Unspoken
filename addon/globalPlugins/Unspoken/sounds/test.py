from camlorn_audio import *
from glob import *

init_camlorn_audio()

x = dict()
for i in glob('*.wav'):
 x[i] = Sound3D(i)

for i, s in x.iteritems():
 print i
 s.play()
 raw_input()

x2 = dict()
for i in glob('*.wav'):
 x2[i] = Sound3D(i)

for i, s in x2.iteritems():
 print i
 s.play()
 raw_input()