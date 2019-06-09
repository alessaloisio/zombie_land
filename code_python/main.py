#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################
#                                       #
#   ZOMBIE LAND :: ALOISIO Alessandro   #
#           2015 - 2016                 #
#                                       #
#########################################


import pygame, sys, glob, os, math, time
from pygame.locals import *
from pygame.transform import scale
from sys import platform as _platform
from random import randrange

# Ajouter le dossier de config dans le path
sys.path.append('inc')
from spritesheet import SpriteSheet

#import maps

FPS = 30
STARTIME = time.time()
MINWINWIDTH = 1156
MINWINHEIGHT = 610
FULLSCREENSWITCH = False

# COLOR          R    G    B
WHITE        = (255, 255, 255)
ORANGE		 = (255, 126, 0)
BLACK        = (  0,   0,   0)
BRIGHTRED    = (255,   0,   0)
RED          = (155,   0,   0)
BRIGHTGREEN  = (  0, 255,   0)
GREEN        = (  0, 155,   0)
BRIGHTBLUE   = (  0,   0, 255)
BLUE         = (  0,   0, 155)
BRIGHTYELLOW = (255, 255,   0)
YELLOW       = (155, 155,   0)
DARKGRAY     = ( 40,  40,  40)
bgColor = (154, 212, 226)

#########################################
#                                       #
#                 CLASS                 #
#                                       #
#########################################

class Bullets(pygame.sprite.Sprite):
	
	def __init__(self, where, start, end):
		pygame.sprite.Sprite.__init__(self)
		
		self.where = where
		
		self.start = start
		self.end = end
		
		self.posX = self.start[0] + 20
		self.posY = self.start[1] + 31
		
		self.weapon = 1
		self.speed = 20
		
		self.dimBullet = 4

	def newPos(self, dim = 4, color=ORANGE, speed=10):
		self.dimBullet = dim
		self.color = color
		self.speed = speed
		
		dx, dy = self.end[0] - self.start[0], self.end[1] - self.start[1]
		dist = math.hypot(dx, dy)
		dx, dy = dx / dist, dy / dist

		# speed
		dx *= self.speed
		dy *= self.speed

		# pos
		self.posX += dx
		self.posY += dy

		pygame.draw.circle(bulletsRect, self.color, (int(self.posX), int(self.posY)), self.dimBullet)
		
class Enemies(pygame.sprite.Sprite):
	
	def __init__(self, where, orientation, pos):
		pygame.sprite.Sprite.__init__(self)
		
		self.posX = pos[0]
		self.posY = pos[1]
		
		self.orientation = orientation
		self.where = where
		print("un new zombie")

#########################################
#                                       #
#                 MAIN                  #
#                                       #
#########################################

def main():
	global FPSCLOCK, screen, FULLWINHEIGHT, FULLWINWIDTH, WINWIDTH, WINHEIGHT, cursors, flags, mapRect, playerRect, posXMap, posYMap, speedMapMoving, player, posXPlayer, posYPlayer, speedPlayerMoving, selectTile, removeSelectTile, lastTimePlayer, lastTimeGun, enemies, bulletsRect, bulletsGroup, STARTIME, TITLEFONT, BASICFONT, shotSound, gameBreak, intervalShootGun, wave

	pygame.init()
	FPSCLOCK = pygame.time.Clock()

	# GET FULLSCREEN SIZE
	FULLWINWIDTH = pygame.display.Info().current_w
	FULLWINHEIGHT = pygame.display.Info().current_h

	screen = pygame.display.set_mode((MINWINWIDTH, MINWINHEIGHT), DOUBLEBUF)
	flags = screen.get_flags()
	pygame.display.set_caption('Zombie Land')
	
	# Longueur et largeur de la fenêtre
	WINWIDTH = screen.get_width()
	WINHEIGHT = screen.get_height()

	# FAVICON
	favicon = pygame.image.load('res/img/favicon.png')
	pygame.display.set_icon(favicon)

	# CURSORS
	cursors = {
		'DEFAULT': pygame.image.load('res/img/cursor.png').convert_alpha(),
		'PRESSED': pygame.image.load('res/img/cursor_pressed.png').convert_alpha()
	}
	pygame.mouse.set_pos(WINWIDTH/2, WINHEIGHT/2)

	# EVENTS
	pygame.key.set_repeat(1, FPS)
	lastTimePlayer = 0
	lastTimeGun = 0

	# FONTS
	TITLEFONT = pygame.font.Font('res/fonts/KenVectorBold.ttf', 40)
	BASICFONT = pygame.font.Font('res/fonts/KenVectorThin.ttf', 20)

	# SOUNDS
	pygame.mixer.music.load('res/sounds/MissionPlausible.ogg')
	pygame.mixer.music.play(-1)

	shotSound = pygame.mixer.Sound('res/sounds/GunShot.ogg')

	# Bouger la map quand on se déplace
	posXMap = -( (WINWIDTH // 2) + 132 + 32 )
	posYMap = -( (WINHEIGHT // 2) + 64 )
	speedMapMoving = 10

	# IMG
	selectTile = pygame.image.load('res/img/selectTile.png')

	# Generate MAP ISOMETRIC...
	genMap()

	# Player Position
	posXPlayer = int(round(WINWIDTH/2)) - 40/2
	posYPlayer = int(round(WINHEIGHT/2)) - 62/2

	# Enemy Spawn Manager
	spawnPos = [(1950, 300), (1050, 350), (1800, 850)]
	damageEnemy = 5
	timeStart = 0
	startSpeedEnemy = 3
	speedEnemy = startSpeedEnemy
	startDelaySpawnEnemy = 1.2
	delaySpawnEnemy = startDelaySpawnEnemy
	delayAttackEnemy = 0.02
	startWaveNbEnemy = 1
	waveNbEnemy = startWaveNbEnemy
	nbEnemyMap = 0
	enemyKilled = 0
	wave = 1
	timerEnemy = 0
	timerAttack = 0
	
	# Sprites PLayer/Enemies
	soldat = SpriteSheet("res/spritesheets/characters/soldat/soldat.png")
	player = {
		'up': soldat.get_image(158, 0, 37, 62),
		'NO': soldat.get_image(127, 0, 28, 62),
		'NE': soldat.get_image(197, 0, 43, 62),
		'down': soldat.get_image(0, 0, 38, 62),
		'SO': soldat.get_image(42, 0, 44, 62),
		'SE': soldat.get_image(294, 0, 26, 62),
		'left': soldat.get_image(86, 0, 125, 62),
		'right': soldat.get_image(249, 0, 41, 62)
	}

	enemies = {
		'up': pygame.image.load('res/spritesheets/characters/ZU.gif'),
		'NO': pygame.image.load('res/spritesheets/characters/ZNO.gif'),
		'NE': pygame.image.load('res/spritesheets/characters/ZNE.gif'),
		'down': pygame.image.load('res/spritesheets/characters/ZD.gif'),
		'SO': pygame.image.load('res/spritesheets/characters/ZSO.gif'),
		'SE': pygame.image.load('res/spritesheets/characters/ZSE.gif'),
		'left': pygame.image.load('res/spritesheets/characters/ZL.gif'),
		'right': pygame.image.load('res/spritesheets/characters/ZR.gif')
	}
	
	# Pygame Sprites Group
	bulletsGroup = pygame.sprite.Group()
	enemiesGroup = pygame.sprite.Group()

	# Other
	score = 0
	playerHealth = 100
	gameStart = False
	gameBreak = False
	startIntervalShootGun = 0.5
	intervalShootGun = startIntervalShootGun

	while True:

		# Gérer les évènements
		checkEvent(gameStart)

		# Menu
		if(gameStart != True):
			start = menuWindow()
			if(start):
				gameStart = True
			continue

		if(gameBreak != False):
			continue

		# Game Over Menu
		if(playerHealth <= 0):
			screen.fill(BLACK)

			gameOverText = TITLEFONT.render("Game Over", True, WHITE)
			screen.blit(gameOverText, ((WINWIDTH/2 - gameOverText.get_rect()[2]/2), (WINHEIGHT/2 - 100)))

			infoText = BASICFONT.render("Vous avez atteint la "+str(wave)+" vague(s) avec un score de "+str(score)+" !", True, WHITE)
			screen.blit(infoText, ((WINWIDTH/2 - infoText.get_rect()[2]/2), (WINHEIGHT/2)))

			# btn replay
			replayBtn = pygame.draw.rect(screen, WHITE, ((WINWIDTH/2 - 110 - 25), (WINHEIGHT/2 + 100), 110, 44))
			replayText = BASICFONT.render("Rejouer", True, BLACK)
			screen.blit(replayText, ((WINWIDTH/2 - 110 - 25 + ((110 - replayText.get_rect()[2]) / 2)), (WINHEIGHT/2 + 100 + ((44 - replayText.get_rect()[3]) / 2))))

			# btn home
			homeBtn = pygame.draw.rect(screen, WHITE, ((WINWIDTH/2 + 25), (WINHEIGHT/2 + 100), 110, 44))
			homeText = BASICFONT.render("Accueil", True, BLACK)
			screen.blit(homeText, ((WINWIDTH/2 + 25 + ((110 - homeText.get_rect()[2]) / 2), (WINHEIGHT/2 + 100 + ((44 - homeText.get_rect()[3]) / 2)))))

			if(pygame.mouse.get_pressed()[0]):

				# if pos cursor in rect of replay
				#     replayBtn[0] replayBtn[1] replayBtn[2] replayBtn[3]
				mousePos = pygame.mouse.get_pos()

				# Replay BTN
				if(mousePos[0] >= replayBtn[0] and mousePos[0] <= (replayBtn[0] + replayBtn[2]) and mousePos[1] >= replayBtn[1] and mousePos[1] <= (replayBtn[1] + replayBtn[3])):
					gameStart = True

				# Home BTN
				if(mousePos[0] >= homeBtn[0] and mousePos[0] <= (homeBtn[0] + homeBtn[2]) and mousePos[1] >= homeBtn[1] and mousePos[1] <= (homeBtn[1] + homeBtn[3])):
					gameStart = False

				score = 0
				playerHealth = 100
				bulletsGroup.empty()
				enemiesGroup.empty()
				
				STARTIME = time.time()

				waveNbEnemy = startWaveNbEnemy
				delaySpawnEnemy = startDelaySpawnEnemy
				speedEnemy = startSpeedEnemy
				intervalShootGun = startIntervalShootGun
				wave = 1
				nbEnemyMap = 0
				enemyKilled = 0

				posXMap = -( (WINWIDTH // 2) + 132 + 32 )
				posYMap = -( (WINHEIGHT // 2) + 64 )

			changeCursor(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
			pygame.display.flip()
			FPSCLOCK.tick(FPS)
			continue

		# FOND
		screen.fill(bgColor)

		# Enemies Manager
		enemiesRect = pygame.Surface.copy(mapRect)
		playerPos = (posXPlayer - posXMap, posYPlayer - posYMap)
		
		coordsZombie = []

		# spawn enemy, add enemies with timer
		timerEnemy -= (FPSCLOCK.tick_busy_loop(60)/1000)

		# Vague terminer
		if(enemyKilled == waveNbEnemy):
			print('vague suivante')
			wave += 1
			# on augmente le nombre d'ennemies
			waveNbEnemy += 2

			nbEnemyMap = 0
			enemyKilled = 0
			timerEnemy = 0

			# on diminue le temps d'apparition
			if(delaySpawnEnemy > 0.3):
				delaySpawnEnemy -= 0.15
			# on augmente la vitesse de déplacement
			if(speedEnemy < 5):
				speedEnemy += 0.15

		# Ajouter les ennemies avec un delay
		if(timerEnemy <= 0):
			timerEnemy = delaySpawnEnemy

			if(waveNbEnemy > nbEnemyMap):

				posEnemy = spawnPos[randrange(0, len(spawnPos))]
				where = lookTo(playerPos, posEnemy)
				enemiesGroup.add(Enemies(enemiesRect, where, posEnemy))
				nbEnemyMap += 1
	
		# ai for move enemies
		if len(enemiesGroup.sprites()) > 0:
			j = len(enemiesGroup.sprites())
			for enemy in enemiesGroup.sprites():

				dx, dy = enemy.posX - playerPos[0], enemy.posY - playerPos[1]
				dist = math.hypot(dx, dy)
				dx, dy = dx / dist, dy / dist

				dx *= speedEnemy
				dy *= speedEnemy

				enemyCollide = False
				collide = False
				coordsCollide = False
				posCollide = []
				line = False

				# Verifier les collisions avec les zombies
				for i in range(len(enemiesGroup.sprites())):
					if(enemy != enemiesGroup.sprites()[i]):
						if(math.hypot(enemy.posX - enemiesGroup.sprites()[i].posX - dx, enemy.posY - enemiesGroup.sprites()[i].posY - dy) <= 38):
							enemyCollide = True

				# Verifier les collisions avec le joueur + timerAttackEnemy
				if(dist <= 20):
					timerAttack -= (FPSCLOCK.tick_busy_loop(60)/1000)
					if(timerAttack <= 0):
						timerAttack = delayAttackEnemy
						playerHealth -= damageEnemy
					
					enemyCollide = True
				
				# Verifier les collisions avec les obstacles
				if(enemyCollide != True):
					for i in range(len(coordsBlocks)):
						# point x1, y1
						if(checkInsideTile((int(enemy.posX + enemies[enemy.orientation].get_width() - 35 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() - 8 - dy)), coordsBlocks[i][1])):
							coordsCollide = coordsBlocks[i][1]
							posCollide.append("x1")
							if line == False:
								line = detailedCheckCollide((int(enemy.posX + enemies[enemy.orientation].get_width() - 35 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() - 8 - dy)), coordsBlocks[i][1])
							collide = True
						# point x2, y2
						if(checkInsideTile((int(enemy.posX + enemies[enemy.orientation].get_width() - 10 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() - 21 - dy)), coordsBlocks[i][1])):
							coordsCollide = coordsBlocks[i][1]
							posCollide.append("x2")
							if line == False:
								line = detailedCheckCollide((int(enemy.posX + enemies[enemy.orientation].get_width() - 10 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() - 21 - dy)), coordsBlocks[i][1])
							collide = True
						# point x3, y3
						if(checkInsideTile((int(enemy.posX + enemies[enemy.orientation].get_width() + 15 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() - 7 - dy)), coordsBlocks[i][1])):
							coordsCollide = coordsBlocks[i][1]
							posCollide.append("x3")
							if line == False:
								line = detailedCheckCollide((int(enemy.posX + enemies[enemy.orientation].get_width() + 15 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() - 7 - dy)), coordsBlocks[i][1])
							collide = True
						# point x4, y4
						if(checkInsideTile((int(enemy.posX + enemies[enemy.orientation].get_width() - 10 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() + 6 - dy)), coordsBlocks[i][1])):
							coordsCollide = coordsBlocks[i][1]
							posCollide.append("x4")
							if line == False:
								line = detailedCheckCollide((int(enemy.posX + enemies[enemy.orientation].get_width() - 10 - dx), int(enemy.posY + enemies[enemy.orientation].get_height() + 6 - dy)), coordsBlocks[i][1])
							collide = True

					if collide == False:
						enemy.posX -= dx
						enemy.posY -= dy
						enemy.orientation = lookTo(playerPos, (enemy.posX, enemy.posY))
					else:
						# Si collision on essaye de contourner
						print(coordsCollide)
						print(line)
						print(posCollide)
						print(enemy.orientation)

						if line == "TR" or line == "BL" or (line == "R" and ('x4' in posCollide)) or (line == "L" and ('x2' in posCollide)):
							dx, dy = coordsCollide[2][0] - coordsCollide[1][0], coordsCollide[2][1] - coordsCollide[1][1]
						else:
							dx, dy = coordsCollide[1][0] - coordsCollide[0][0], coordsCollide[1][1] - coordsCollide[0][1]
							
						angle = math.degrees(math.atan2(dx, dy))

						# print(angle)

						dist = math.hypot(dx, dy)
						dx, dy = dx / dist, dy / dist

						# verifier la collisions

						# block line x2, x3 and zombie line x1, x4 => fin du block
						if (('x1' in posCollide or 'x2' in posCollide) and 'x3' not in posCollide and 'x4' not in posCollide) and (line != "TR" and line != "BL"):
							dx *= -1
							dy *= -1

						#
						elif ((('x2' in posCollide or 'x3' in posCollide) and 'x1' not in posCollide and 'x4' not in posCollide) and line == "BL"):
							dx *= -1
							dy *= -1
				
						# il ne peut y avoir que 2 points max


						enemy.posX += (dx*speedEnemy)
						enemy.posY += (dy*speedEnemy)

						# Changer la direction selon l'obstacle
						if angle > -22.5 and angle < 22.5:
							enemy.orientation = 'down'
						elif angle < -157.5 or angle > 157.5:
							enemy.orientation = 'up' 
						elif angle < 112.5 and angle > 67.5:
							enemy.orientation = 'right'
						elif angle > -112.5 and angle < -67.5:
							enemy.orientation = 'left'
						elif angle > 112.5 and angle < 157.5:
							enemy.orientation = 'SO'
						elif angle < -112.5 and angle > -157.5:
							enemy.orientation = 'NO'	
						elif angle > 22.5 and angle < 67.5:
							enemy.orientation = 'SE'
						elif angle < -22.5 and angle > -67.5:
							enemy.orientation = 'NE'

				# Afficher le zombie dans la surface
				enemiesRect.blit(enemies[enemy.orientation], (enemy.posX, enemy.posY))

				# ajouter les coordonnées des zombies
				coordsZombie.append(((int(enemy.posX), int(enemy.posY + 31)), (int(enemy.posX + 20), int(enemy.posY)), (int(enemy.posX + 40), int(enemy.posY + 31)), (int(enemy.posX + 20), int(enemy.posY + 62))))
					
		# bullets manager
		if len(bulletsGroup.sprites()) > 0:
			j = len(bulletsGroup.sprites())
			for bullets in bulletsGroup.sprites():
				
				shoot = False
				
				# si en dehors de la map
				if(checkInsideTile((bullets.posX, bullets.posY), dimMap) != True):
					collide = True

				# sur un obstacle
				if(collide != True):
					for i in range(len(coordsBlocks)):
						if(checkInsideTile((bullets.posX, bullets.posY), coordsBlocks[i][1]) == True):
							collide = True
							
				# ennemis
				if(collide != True):
					for i in range(len(coordsZombie)):
						if(checkInsideTile((bullets.posX, bullets.posY), coordsZombie[i]) == True):
							shoot = True

							# SUPPRIMER LE ZOMBIE
							try:
								enemiesGroup.sprites()[i]
							except IndexError:
								shoot = False
								print('aiex')

							if(shoot):

								enemiesGroup.sprites()[i].kill()
								enemyKilled += 1		
							
				# traitement
				if collide != True and shoot == False:
					
					nb = len(bulletsGroup.sprites())
					
					# Lance Flamme
					if(nb > 12):
						nb = 12

					if(j < (nb/3)):
						color = YELLOW
					elif(j >= (nb/3) and j <= (nb/3)*2):
						color = ORANGE
					elif(j > (nb/3)*2):
						color = RED
					
					bullets.newPos(int(j*1.1), color, 35)
					
				elif shoot == True:
					bulletsGroup.remove(bullets)
					# AJOUTER SCORE
					score += 10

					
				else:
					bulletsGroup.remove(bullets)
				
				j -= 1
	
		# Placer les surfaces
		screen.blit(mapRect, (posXMap, posYMap))
		screen.blit(enemiesRect, (posXMap, posYMap))
		screen.blit(playerRect, (posXPlayer,  posYPlayer))
		screen.blit(bulletsRect, (posXMap, posYMap))

		#########################################
		#                  GUI                  #
		#########################################
		# Timer
		timeText = BASICFONT.render("Time "+str(round((time.time() - STARTIME))), True, WHITE)
		screen.blit(timeText, ((WINWIDTH-timeText.get_rect()[2] - 25), 25))

		# Score + vague
		scoreText = BASICFONT.render("Score : "+str(score), True, WHITE)
		screen.blit(scoreText, (25, 25))
		waveText = BASICFONT.render("Wave : "+str(wave), True, WHITE)
		screen.blit(waveText, (25, 50))

		# Weapon
		if(intervalShootGun == 0.5):	
			gunLabel = "Gun"
		elif(intervalShootGun == 0.2):
			gunLabel = "Submachine Gun"
		else:
			gunLabel = "Flame Thrower"

		gunText = BASICFONT.render("Weapon : "+str(gunLabel), True, WHITE)
		screen.blit(gunText, ((WINWIDTH-gunText.get_rect()[2] - 25), (WINHEIGHT-24-25)))

		# PlayerHealth
		pygame.draw.rect(screen, WHITE, (25, (WINHEIGHT-24-25), 110, 24))
		pygame.draw.rect(screen, RED, (30, (WINHEIGHT-24-22), playerHealth, 18))

		# Remplacer le curseur
		changeCursor(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])

		pygame.display.flip()
		FPSCLOCK.tick(FPS)

def quit():
	pygame.quit()
	sys.exit()

def checkEvent(gameStart):
	global screen, mapRect, posXMap, posYMap, speedMapMoving, lastTimeGun, bulletsRect, shotSound, gameBreak, intervalShootGun, wave
	
	for e in pygame.event.get():
		# BTN pressé
		if e.type == KEYDOWN:
			# BTN ESC => QUITTER
			if e.key == K_ESCAPE:
				quit()
			# F/F11 => FULLSCREEN
			elif e.key == K_F11 or e.key == K_f:
				fullscreen()

			# Gestion des touches UP/DOWN/LEFT/RIGHT
			elif e.key == K_DOWN:
				posYMap -= speedMapMoving
				print('down')
			elif e.key == K_UP:
				posYMap += speedMapMoving
				print('up')
			elif e.key == K_LEFT:
				posXMap += speedMapMoving
				print('left')
			elif e.key == K_RIGHT:
				posXMap -= speedMapMoving
				print('right')

		elif e.type == KEYUP:
			if e.key == K_p:
				if gameBreak:
					gameBreak = False
				else:
					gameBreak = True

		# BTN QUIT
		elif e.type == QUIT:
			quit()

	if(gameStart):
		pressedKey = pygame.key.get_pressed()
		forward = False
		
		# Faire avancer le joueur lorsqu'on clique sur la touche "X"
		if pressedKey[K_x]:
			forward = True
			
		animPlayer(pygame.mouse.get_pos(), (posXPlayer, posYPlayer), forward)
		
		# Tirer si on clique sur le bouton gauche de la souris
		pressedMouse = pygame.mouse.get_pressed()
		
		# Limiter le nombre d'action par seconde
		now = time.time()
		# entre 0.01 et 0.06 => 30 FPS
		# 0.5 => pistolet
		# 0.2 => mitrailleuse
		# 0.09 => lance flamme
		if(wave % 4 == 0):
			intervalShootGun = 0.02
		elif(wave % 3 == 0):
			intervalShootGun = 0.2
		elif(wave % 2 == 0):
			intervalShootGun = 0.5

		interval = intervalShootGun
		
		bulletsRect = pygame.Surface((mapRect.get_width(), mapRect.get_height()), pygame.SRCALPHA, 32).convert_alpha()

		if pressedMouse[0] and (now-lastTimeGun)>interval:

			lastTimeGun = now
				
			mousePos = pygame.mouse.get_pos()
			mousePos = (mousePos[0] - posXMap - 20, mousePos[1] - posYMap - 24)

			playerPos = (posXPlayer - posXMap, posYPlayer - posYMap)
			
			bulletsGroup.add(Bullets(bulletsRect, playerPos, mousePos))

			shotSound.play()
			
def fullscreen():
	global flags, FULLWINHEIGHT, FULLWINWIDTH, FULLSCREENSWITCH, WINHEIGHT, WINWIDTH, posXMap, posYMap, posYPlayer, posXPlayer, mapRect

	if flags == 0:
		screen = pygame.display.set_mode((FULLWINWIDTH, FULLWINHEIGHT), pygame.FULLSCREEN)
		WINWIDTH = FULLWINWIDTH
		WINHEIGHT = FULLWINHEIGHT
		
		posXMap = -( (mapRect.get_width() - WINWIDTH) / 2)
		posYMap = -( (mapRect.get_height() - WINHEIGHT) / 2)
		
		posXPlayer = int(round(WINWIDTH/2)) - 40/2
		posYPlayer = int(round(WINHEIGHT/2)) - 62/2
		
		FULLSCREENSWITCH = True
	else:
		screen = pygame.display.set_mode((MINWINWIDTH, MINWINHEIGHT), pygame.DOUBLEBUF)
		WINWIDTH = MINWINWIDTH
		WINHEIGHT = MINWINHEIGHT
		
		posXMap = -( (mapRect.get_width() - WINWIDTH) / 2)
		posYMap = -( (mapRect.get_height() - WINHEIGHT) / 2)
		
		posXPlayer = int(round(WINWIDTH/2)) - 40/2
		posYPlayer = int(round(WINHEIGHT/2)) - 62/2
		
		FULLSCREENSWITCH = False

	flags = screen.get_flags()

def changeCursor(coords, type):
	global cursors

	if type == 0:
		screen.blit(cursors['DEFAULT'], coords)
	else:
		screen.blit(cursors['PRESSED'], coords)

	#Enlever le curseur par défaut
	pygame.mouse.set_visible(False)

def genMap():
	global mapRect, playerRect, coordsBlocks, dimMap

	# Tous les blocks
	ssLanscape = SpriteSheet("res/spritesheets/landscapes/landscape_sheet.png")
	GNNN = ssLanscape.get_image(1193, 0, 132, 99)
	GNFN = ssLanscape.get_image(0, 424, 132, 83)
	GNNM = ssLanscape.get_image(1324, 225, 132, 115)
	GNNL = ssLanscape.get_image(928, 115, 132, 115)
	GRCS = ssLanscape.get_image(1192, 396, 132, 99)
	GLCS = ssLanscape.get_image(1192, 297, 132, 99)
	GTCS = ssLanscape.get_image(1192, 198, 132, 99)
	GRNS = ssLanscape.get_image(797, 0, 132, 115)
	GLNS = ssLanscape.get_image(532, 333, 132, 115)
	GTNS = ssLanscape.get_image(532, 234, 132, 99)
	GBNS = ssLanscape.get_image(664, 317, 132, 99)
	BRLN = ssLanscape.get_image(928, 230, 132, 99)
	BLLN = ssLanscape.get_image(1325, 0, 132, 99)
	BNNN = ssLanscape.get_image(664, 234, 132, 83)
	BBSN = ssLanscape.get_image(1457, 0, 132, 99)
	BTSN = ssLanscape.get_image(1324, 340, 132, 99)
	BLSN = ssLanscape.get_image(1588, 297, 132, 99)
	BRSN = ssLanscape.get_image(1588, 396, 132, 99)
	BBRN = ssLanscape.get_image(928, 329, 132, 99)
	BTRN = ssLanscape.get_image(1720, 99, 132, 99)
	BLRN = ssLanscape.get_image(1060, 396, 132, 99)
	BRRN = ssLanscape.get_image(1060, 297, 132, 99)
	BRLB = ssLanscape.get_image(1060, 198, 132, 99)
	BLLB = ssLanscape.get_image(1720, 409, 132, 99)
	BRLS = ssLanscape.get_image(1852, 235, 132, 115)
	BBLS = ssLanscape.get_image(796, 313, 132, 99)
	BTLS = ssLanscape.get_image(796, 412, 132, 99)
	BLLS = ssLanscape.get_image(665, 0, 132, 115)
	BNNT = ssLanscape.get_image(1456, 99, 132, 99)
	BBNT = ssLanscape.get_image(665, 115, 132, 99)
	BTNT = ssLanscape.get_image(1456, 198, 132, 99)
	BLNT = ssLanscape.get_image(1720, 310, 132, 99)
	BRNT = ssLanscape.get_image(929, 0, 132, 99)
	WRLN = ssLanscape.get_image(0, 198, 132, 99)
	WLLN = ssLanscape.get_image(1588, 99, 132, 99)
	WTRN = ssLanscape.get_image(1589, 0, 132, 99)
	WBRN = ssLanscape.get_image(1060, 99, 132, 99)
	WRRN = ssLanscape.get_image(1061, 0, 132, 99)
	WLRN = ssLanscape.get_image(1192, 99, 132, 99)
	P1 = ssLanscape.get_image(266, 241, 133, 111)
	P2 = ssLanscape.get_image(399, 127, 133, 121)
	P3 = ssLanscape.get_image(266, 352, 133, 113)
	P4 = ssLanscape.get_image(399, 0, 133, 127)
	P5 = ssLanscape.get_image(1324, 99, 132, 126)
	P6 = ssLanscape.get_image(399, 248, 133, 124)
	P7 = ssLanscape.get_image(399, 372, 133, 121)
	P8 = ssLanscape.get_image(532, 0, 133, 118)
	P9 = ssLanscape.get_image(532, 118, 133, 116)
	P10 = ssLanscape.get_image(1456, 297, 132, 130)
	P11 = ssLanscape.get_image(266, 0, 133, 118)
	P12 = ssLanscape.get_image(266, 118, 133, 123)
	R1 = ssLanscape.get_image(0, 0, 133, 99)
	R2 = ssLanscape.get_image(0, 99, 133, 99)
	R3 = ssLanscape.get_image(133, 0, 133, 102)
	R4 = ssLanscape.get_image(133, 102, 133, 102)
	R5 = ssLanscape.get_image(133, 204, 133, 99)
	R6 = ssLanscape.get_image(133, 303, 133, 99)
	R7 = ssLanscape.get_image(1588, 198, 132, 99)
	R8 = ssLanscape.get_image(133, 402, 133, 99)
	C1 = ssLanscape.get_image(1720, 198, 132, 112)
	C2 = ssLanscape.get_image(1852, 114, 132, 121)
	C3 = ssLanscape.get_image(0, 297, 133, 127)
	C4 = ssLanscape.get_image(1852, 0, 132, 114)

	# Disposition des blocks pour la première map
	map1 = [
		[GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN],
		[GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN],
		[GNNN, GNNN, P10, P7, P7, P7, P7, P7, R4, GNNN, GNNN, GNNN, R4, P7, P7, P7, P7, P7, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, P10, P10, P10, GNNN, GNNN, GNNN, GNNN, GNNN, P10, P10, P10, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, P10, P10, P10, GNNN, GNNN, GNNN, GNNN, GNNN, P10, P10, P10, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, P10, P10, P10, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P10, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P10, GNNN, GNNN],
		[GNNN, GNNN, P7, P7, P7, P7, P7, P7, P7, P7, GNNN, GNNN, P7, P7, P7, P7, P7, P7, P7, GNNN, GNNN],
		[GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P7, P7, GNNN, GNNN, GNNN, P7, P7, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN],
		[GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P7, P7, GNNN, GNNN, GNNN, P7, P7, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN],
		[GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, P7, P7, GNNN, GNNN, GNNN, P7, P7, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN],
		[GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, C1, C1, GNNN, GNNN, GNNN, C1, C1, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN, GNNN]
	]

	# Créer une surface pour la map
	mapRect = pygame.Surface(((132 * (len(map1))), (64 * (len(map1[0])) + 35)), pygame.SRCALPHA, 32).convert_alpha()
	mapRect.fill(bgColor)

	# Calculer les coordonnées du premier blocks a placer (selon dim. la map)
	calcFirstX = (mapRect.get_width()//2) - 64
	calcFirstY = 0

	# Initialisation des coordonnées pour la mise en place des blocks
	tmpX, tmpY = (calcFirstX, calcFirstY)
	x, y = (calcFirstX, calcFirstY)

	# Init les coordonnées des blocks, des sommets et des collisions
	coordsBlocks = {}

	# Placement des blocks dans le jeu
	acc = 0
	dimMap = {}

	for i in range(len(map1)):
		if i > 0:
			# Premet d'aligner les colonnes
			tmpX -= 64
			tmpY += 32
			x, y = (tmpX, tmpY)

		for j in range(len(map1[i])):
			if j > 0:
				x += 64
				y += 32

			# Gérer la position si la largeur ou longueur d'un block est différent
			if map1[i][j].get_width() != 132 and map1[i][j].get_height() != 99:
				mapRect.blit(map1[i][j], (x + (132 - map1[i][j].get_width()), y + (99 - map1[i][j].get_height())))
			elif map1[i][j].get_width() != 132:
				mapRect.blit(map1[i][j], (x + (132 - map1[i][j].get_width()), y))
			elif map1[i][j].get_height() != 99:
				mapRect.blit(map1[i][j], (x, y + (99 - map1[i][j].get_height())))
			else:
				mapRect.blit(map1[i][j], (x, y))
			
			# Récupérer les 4 sommets de la map
			if i == 0 and j == 0:
				dimMap[1] = (x+64, y)
			elif i == 0 and j == len(map1[i])-1:
				dimMap[2] = (x+132, y+32)
			elif i == len(map1)-1 and j == 0:
				dimMap[0] = (x, y+32)
			elif i == len(map1)-1 and j == len(map1[i])-1:
				dimMap[3] = (x+64, y+64)
			
			# Vérifier collision
			if id(map1[i][j]) != id(GNNN):
				# if id(map1[i][j]) == id(R4):
				# 	coordsBlocks[acc] = ((x, y), ((x+40, y+21), (x+68, y), (x+95, y+21), (x+68, y+42)))
				coordsBlocks[acc] = ((x, y), ((x, y+32), (x+64, y), (x+132, y+32), (x+64, y+64)))
				acc += 1
		
def detailedCheckCollide(pos, coords):
	if pos[0] > coords[0][0] and pos[0] < coords[2][0] and pos[1] > coords[1][1] and pos[1] < coords[3][1]:
		if pos[0] < coords[0][0] + ((coords[2][0] - coords[0][0]) / 2):
			m = (coords[1][1] - coords[0][1]) / (coords[1][0] - coords[0][0])
			yd = (m * (pos[0] - coords[0][0])) + coords[0][1]
			if pos[1] > yd and pos[1] < (yd + ((coords[0][1] - yd) * 2)):
				# droite en haut à gauche x1, x2
				if pos[1] == yd + (coords[0][1] - yd):
					return "L"
				elif pos[1] < yd + (coords[0][1] - yd):
					return "TL"
				# droite en bas à gauche x1, x4
				else:
					return "BL"
		else:
			m = (coords[2][1] - coords[1][1]) / (coords[2][0] - coords[1][0])
			yd = (m * (pos[0] - coords[1][0])) + coords[1][1]
			if pos[1] > yd and pos[1] < (yd + ((coords[2][1] - yd) * 2)):
				# droite en haut à droite x3, x2
				if pos[1] == yd + (coords[2][1] - yd):
					return "R"
				elif pos[1] < yd + (coords[2][1] - yd):
					return "TR"
				# droite en bas à droite x3, x4
				else:
					return "BR"
	return False

def checkInsideTile(pos, coords):
	if pos[0] > coords[0][0] and pos[0] < coords[2][0] and pos[1] > coords[1][1] and pos[1] < coords[3][1]:
		if pos[0] < coords[0][0] + ((coords[2][0] - coords[0][0]) / 2):
			m = (coords[1][1] - coords[0][1]) / (coords[1][0] - coords[0][0])
			yd = (m * (pos[0] - coords[0][0])) + coords[0][1]
			if pos[1] > yd and pos[1] < (yd + ((coords[0][1] - yd) * 2)):
				return True
		else:
			m = (coords[2][1] - coords[1][1]) / (coords[2][0] - coords[1][0])
			yd = (m * (pos[0] - coords[1][0])) + coords[1][1]
			if pos[1] > yd and pos[1] < (yd + ((coords[2][1] - yd) * 2)):
				return True
	return False

def animPlayer(mousePos, playerPos, forward):
	global playerRect, player, posXMap, posYMap, mapRect, coordsBlocks, lastTimePlayer, dimMap, enemies

	playerRect = pygame.Surface((40, 62), pygame.SRCALPHA, 32).convert_alpha()
	collide = False
	
	# Limiter le nombre d'action par seconde
	now = time.time()
	# entre 0.01 et 0.06 => 30 FPS
	interval = 0.03
	#interval = FPS / 1000

	# Position du joueur sur l'écran
	playerPos = (playerPos[0], playerPos[1])
	angle = math.degrees(math.atan2(mousePos[1]-playerPos[1], mousePos[0]-playerPos[0]))

	# Position du joueur sur la map
	playerPos = (playerPos[0] - posXMap, playerPos[1] - posYMap)

	# RENDER PLAYER

	# RIGHT
	if(angle > -22.5 and angle < 22.5):
		playerRect.blit(player['right'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0] + 40, playerPos[1] + 46.5), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0] + 20, playerPos[1] + 62), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posXMap -= speedMapMoving

	# UP
	elif(angle > -112.5 and angle < -67.5):
		playerRect.blit(player['up'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0] + 20, playerPos[1] + 31), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0] + 20, playerPos[1] + 31), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posYMap += speedMapMoving

	# LEFT
	elif(angle > 157.5 or angle < -157.5):
		playerRect.blit(player['left'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0], playerPos[1] + 46.5), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0] - 20, playerPos[1] + 62), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posXMap += speedMapMoving

	# DOWN
	elif(angle > 67.5 and angle < 112.5):
		playerRect.blit(player['down'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0], playerPos[1] + 62), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0], playerPos[1] + 62), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posYMap -= speedMapMoving	

	# NE
	elif(angle > -67.5 and angle < -22):
		playerRect.blit(player['NE'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0] + 20, playerPos[1] + 31), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0] + 20, playerPos[1] + 62), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posYMap += speedMapMoving/2
				posXMap -= speedMapMoving

	# NO
	elif(angle > -157.5 and angle < -112.5):
		playerRect.blit(player['NO'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0] - 46.5, playerPos[1] + 62), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0] + 20, playerPos[1] + 31), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posYMap += speedMapMoving/2
				posXMap += speedMapMoving

	# SE
	elif(angle > 22.5 and angle < 67.5):
		playerRect.blit(player['SE'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0] + 40, playerPos[1] + 62), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0] + 40, playerPos[1] + 62), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posYMap -= speedMapMoving/2
				posXMap -= speedMapMoving

	# SO
	elif(angle > 112.5 and angle < 157.5):
		playerRect.blit(player['SO'], (0, 0))
		if forward and (now-lastTimePlayer)>interval: 
			lastTimePlayer = now

			if(checkInsideTile((playerPos[0], playerPos[1] + 62), dimMap) != True):
				collide = True

			if(collide != True):
				for i in range(len(coordsBlocks)):
					if(checkInsideTile((playerPos[0], playerPos[1] + 62), coordsBlocks[i][1])):
						collide = True
			
			if(collide == False):
				posYMap -= speedMapMoving/2
				posXMap += speedMapMoving

def lookTo(pos1, pos2):
	angle = math.degrees(math.atan2(pos1[0]-pos2[0], pos1[1]-pos2[1]))
	
	if angle > -22.5 and angle < 22.5:
		return('down')
	elif angle < -157.5 or angle > 157.5:
	 	return('up' )
	elif angle < 112.5 and angle > 67.5:
		return('right')
	elif angle > -112.5 and angle < -67.5:
		return('left')
	elif angle > 112.5 and angle < 157.5:
		return('NE')
	elif angle < -112.5 and angle > -157.5:
		return('NO')
	elif angle > 22.5 and angle < 67.5:
		return('SE')
	elif angle < -22.5 and angle > -67.5:
		return('SO')

def menuWindow():
	global BASICFONT

	# homeBg = pygame.image.load('res/img/home-bg.png')
	# screen.blit(homeBg, ((WINWIDTH - homeBg.get_rect()[2])/2, (WINHEIGHT - homeBg.get_rect()[3])/2))
	screen.fill(RED)

	# TITLE
	
	titleText = TITLEFONT.render("ZOMBIE LAND", True, WHITE)
	screen.blit(titleText, ((WINWIDTH/2 - (titleText.get_rect()[2] / 2)), (WINHEIGHT/2 - 100 )))

	# btn play
	playBtn = pygame.draw.rect(screen, WHITE, ((WINWIDTH/2 - 55), (WINHEIGHT/2 + 50), 110, 44))
	playText = BASICFONT.render("Jouer", True, BLACK)
	screen.blit(playText, ((WINWIDTH/2 - 55 + ((110 - playText.get_rect()[2]) / 2)), (WINHEIGHT/2 + 50 + ((44 - playText.get_rect()[3]) / 2))))# btn play
	
	# quit btn
	quitBtn = pygame.draw.rect(screen, WHITE, ((WINWIDTH/2 - 55), (WINHEIGHT/2 + 125), 110, 44))
	quitText = BASICFONT.render("Quitter", True, BLACK)
	screen.blit(quitText, ((WINWIDTH/2 - 55 + ((110 - quitText.get_rect()[2]) / 2)), (WINHEIGHT/2 + 125 + ((44 - quitText.get_rect()[3]) / 2))))

	if(pygame.mouse.get_pressed()[0]):

		mousePos = pygame.mouse.get_pos()
		# Replay BTN
		if(mousePos[0] >= playBtn[0] and mousePos[0] <= (playBtn[0] + playBtn[2]) and mousePos[1] >= playBtn[1] and mousePos[1] <= (playBtn[1] + playBtn[3])):
			return True

		if(mousePos[0] >= quitBtn[0] and mousePos[0] <= (quitBtn[0] + quitBtn[2]) and mousePos[1] >= quitBtn[1] and mousePos[1] <= (quitBtn[1] + quitBtn[3])):
			quit()

	changeCursor(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
	pygame.display.flip()
	FPSCLOCK.tick(FPS)

	return False

if __name__ == '__main__':
	main()
