#!/usr/bin/env python2
import time, openal, threading, math
from sys import argv,exit

def ir(val):
	if val > 0:
		return int(val + 0.5)
	else:
		return int(val - 0.5)

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
objects = sources + [listener]

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

win = pygcurse.PygcurseWindow(11, 11, 'musiVerse Editor')
win.fill(".")
for i,s in enumerate(sources):
	win.putchars(str(i), x=s['c'][0], y=s['c'][1])
win.putchars("@", x=listener['c'][0], y=listener['c'][1])

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

		clickedobjects = [o for o in objects if o['c'][0] == x and o['c'][1] == y]
		print("chose objects: " + repr(clickedobjects))
		if len(clickedobjects) > 0:		# click on object
			if not any([ob['marked'] for ob in objects]): # if no object is marked
				win.reversecolors(region=(x,y,1,1))
				for ob in clickedobjects: # we mark the (plural?!?) clicked
					ob['marked'] = True
		else: # clicked in empty area
			if any([o['marked'] for o in objects]): # if a source is marked
				for o in [o for o in objects if o['marked'] ]: # iterate over all marked sources
					win.reversecolors(region=(o['c'][0],o['c'][1],1,1)) # remove visual marking from clicked area
					o['marked'] = False
					old = o['c']
					new = x, y, 0
					move_obj_on_grid(o, old, new)
					uppos(o)
	elif event.type == KEYDOWN:
		if event.key == K_w:
			for i in range(0,10):
				listener['obj'].position = listener['obj'].position[0], listener['obj'].position[1], listener['obj'].position[2] - 0.1
				time.sleep(0.05)
			print("new listener pos: " + repr(listener['obj'].position))
		elif event.key == K_s:
			for i in range(0,10):
				listener['obj'].position = listener['obj'].position[0], listener['obj'].position[1], listener['obj'].position[2] + 0.1
				time.sleep(0.05)
			print("new listener pos: " + repr(listener['obj'].position))