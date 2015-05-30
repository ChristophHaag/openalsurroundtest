#!/usr/bin/env python2
import time, openal
from operator import sub,add
from sys import argv

import threading

from bottle import route, run, template
import openal
from operator import sub,add

device = openal.Device()
contextlistener = device.ContextListener()

contextlistener.position = 0, 0, 0
contextlistener.velocity = 0, 0, 0
contextlistener.orientation = 0, 1, 0, 0, 0, 1

sources = [ contextlistener.get_source() for i in range(0,len(argv)-1) ]

for s in sources:
	s = sources[0]
	s.buffer = openal.Buffer(argv[1])
	s.looping = True
	s.position = 10,0,0
	s.gain = 1
	s.play()

#source2 = sources[1]
#buffer2 = openal.Buffer('03-2.wav')
#source2.buffer = buffer2
#source2.looping = True
#source2.position = 10,10,10
#source2.gain = 0.5
#source2.play()


class sourcemover(threading.Thread):
	def __init__(self,source):
		threading.Thread.__init__(self)
		self.source = source
	def run(self):
		ops = [sub, add]
		while True:
			sources[self.source].position = ops[0](sources[self.source].position[0], 0.5), sources[self.source].position[1], sources[self.source].position[2]
			print("\t".join([str(round(p,4)) for p in sources[self.source].position]))
			time.sleep(0.2)
			if abs(sources[self.source].position[0]) > 10:
				ops = list(reversed(ops))

sm1 = sourcemover(0)
sm1.daemon = True
sm1.start()

@route('/listenerpos/<x>/<y>/<z>/')
def listenerpos(x,y,z):
	contextlistener.position = float(x),float(y),float(z)
	return "source position: " + "\t".join([str(round(p,4)) for p in sources[0].position]) + "\n<br>listener position: " + "\t".join([str(round(lp,4)) for lp in contextlistener.position])

run(host='0.0.0.0', port=8080)
