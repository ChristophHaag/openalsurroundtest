#!/usr/bin/env python2
import time, openal
import threading

from sys import argv,exit

import math
def ir(val):
	return int(round(val,0))

device = openal.Device()
contextlistener = device.ContextListener()

contextlistener.position = 5, 5, 0
contextlistener.velocity = 0, 0, 0
contextlistener.orientation = 0, 1, 0, 0, 0, 1

listener = { 'obj' : contextlistener,
			'char' : '@',
			'c' : (ir(contextlistener.position[0]), ir(contextlistener.position[1]), ir(contextlistener.position[2])),
			'marked' : False}
sources = [ {   'obj':contextlistener.get_source(),
				'char' : str(i),
				'c' : (i, 0, 0),
				'marked' : False } for i in range(0,len(argv)-1)]

for i,s in enumerate(sources):
	s['obj'].buffer = openal.Buffer(argv[i+1])
	s['obj'].looping = True
	s['obj'].position = i, 0, 0
	s['obj'].gain = 1

[s['obj'].play() for s in sources]

import pygcurse,pygame
from pygame.locals import *

def upgrid(obj):
	# todo: position is float
	if (obj['c'][0], obj['c'][1], obj['c'][2]) != obj['obj'].position:
		obj['c'] = ir(obj['obj'].position[0]), ir(obj['obj'].position[1]), ir(obj['obj'].position[2])

def uppos(obj):
	obj['obj'].position = obj['c'][0], obj['c'][1], obj['c'][2]

def move_obj_on_grid(obj, old, new):
	fro = (old[0], old[1], old[2])
	to = (new[0], new[1], new[2])
	win.putchars(".", old[0],old[1])
	win.putchars(obj['char'],new[0],new[1])
	obj['c'] = to
	print("moved object " + repr(old) + " " + repr(new))

	
	#obj['c'] = to

win = pygcurse.PygcurseWindow(11, 11, 'musiVerse Editor')
win.fill(".")
for i,s in enumerate(sources):
	win.putchars(str(i), x=s['c'][0], y=s['c'][1])
win.putchars("@", x=listener['c'][0], y=listener['c'][1])

import random
class sourcemover(threading.Thread):
	def __init__(self,source):
		threading.Thread.__init__(self)
		random.seed()
		self.source = source

		self.length = ir(random.uniform(2,5))
		self.angle_stepsize = 0.1
		self.sleeptime = random.uniform(0.01,0.3)
		self.angle = random.uniform(0,2*math.pi)
		self.x = self.length * math.cos(self.angle)
		self.y = self.length * math.sin(self.angle)
		old = sources[self.source]['c']
		new = (ir(self.x + listener['obj'].position[0]), + ir(self.y + listener['obj'].position[1]), 0)
		upgrid(sources[self.source])
		move_obj_on_grid(sources[self.source], old, new)
	def run(self):
		while True:
			while self.angle < 2 * math.pi:

				old = (ir(self.x + listener['obj'].position[0]), + ir(self.y + listener['obj'].position[1]), 0)
				
				self.x = self.length * math.cos(self.angle)
				self.y = self.length * math.sin(self.angle)

				new = (ir(self.x + listener['obj'].position[0]), + ir(self.y + listener['obj'].position[1]), 0)

				sources[self.source]['obj'].position = new

				upgrid(sources[self.source])
				move_obj_on_grid(sources[self.source], old, new)
				
				self.angle = self.angle + self.angle_stepsize
				time.sleep(self.sleeptime)
			self.angle = 0

sourcemovers = [sourcemover(i) for i in range(len(sources))]
for sm in sourcemovers:
	sm.daemon = True
	sm.start()

while True:
	event = pygame.event.wait()
	if event.type == QUIT:
		pygame.quit()
		exit()
	elif event.type == MOUSEBUTTONUP:
		print("marked: " + repr([cs for cs in sources if cs['marked']]))
		x, y = win.getcoordinatesatpixel(event.pos)
		ch = win._screenchar[x][y]
		print("x: %d, y: %d, char: %s" %(x,y,ch))

		clickedsources = [s for s in sources if s['c'][0] == x and s['c'][1] == y]
		print("choose sources: " + repr(clickedsources))
		
		if len(clickedsources) > 0:		# click on source
			if not any([cs['marked'] for cs in sources]): # if no source is marked
				win.reversecolors(region=(x,y,1,1))
				for cs in clickedsources: # we mark the (plural?!?) clicked
					cs['marked'] = True
		elif x == listener['c'][0] and y == listener['c'][1]:
			win.reversecolors(region=(x,y,1,1))
			listener['marked'] = True

		else: # clicked in empty area
			if any([cs['marked'] for cs in sources]): # if a source is marked
				for cs in [cs for cs in sources if cs['marked'] ]: # iterate over all marked sources
					win.reversecolors(region=(cs['c'][0],cs['c'][1],1,1)) # remove visual marking from clicked area
					cs['marked'] = False
					old = cs['c']
					new = x, y, 0
					move_obj_on_grid(cs, old, new)
					uppos(cs)
			elif listener['marked']:
				win.reversecolors(region=(listener['c'][0],listener['c'][1],1,1))
				listener['marked'] = False
				old = listener['c']
				new = x, y, 0
				move_obj_on_grid(listener, old, new)
				uppos(listener)

pygcurse.waitforkeypress()
