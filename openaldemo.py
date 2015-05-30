#!/usr/bin/env python2
import time, openal
from operator import sub,add
from sys import argv

contextlistener = openal.Device().ContextListener()
contextlistener.position = 0, 0, 0
contextlistener.velocity = 0, 0, 0
contextlistener.orientation = 0, 1, 0, 0, 0, 1

source1 = contextlistener.get_source()
source1.buffer = openal.Buffer(argv[1])
source1.looping = True
source1.position = 0,0,0
source1.play()

ops = [sub, add]
while True:
	source1.position = ops[0](source1.position[0], 0.5), source1.position[1], source1.position[2]
	print("\t".join([str(round(p,4)) for p in source1.position]))
	time.sleep(0.2)
	if abs(source1.position[0]) > 10:
		ops = list(reversed(ops))
