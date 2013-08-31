from camlorn_audio import *
import time
from math import *
init_camlorn_audio()
s = Sound3D()
s.set_file(r'../examples/sounds/test.wav')
s.set_looping(True)
s.set_position(0, 0, -3)
s.play()
v = Viewpoint()
v.make_active()

for i in xrange(200):
 v.set_at_vector(cos(2*pi*i/200.0), 0, -sin(2*pi*i/200.0))
 time.sleep(1/20.0)