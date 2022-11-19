import pygame
import random
import sys
from pygame.locals import *

from sprites import (MasterSprite, 
                     Player, FriendShip, Monster, Beam, Explosion,
                     BombPower, ShieldPower, DoublebeamPower, FriendPower, LifePower, TriplecupcakePower,
                     BroccoliBeamfast,
                     Green, Yellow, Grey, Blue, Pink)
from database import Database
from load import load_image, load_sound, load_music
from menu import *

if not pygame.mixer:
    print('Warning, sound disablead')
if not pygame.font:
    print('Warning, fonts disabled')

BACK = 0
SINGLE = 0

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

direction = {None: (0, 0), pygame.K_UP: (0, -2), pygame.K_DOWN: (0, 2),
             pygame.K_LEFT: (-2, 0), pygame.K_RIGHT: (2, 0)}

class Single():
    def playGame(screen_size):
    # Initialize everything
        pygame.mixer.pre_init(11025, -16, 2, 512)
        pygame.init()
        ratio = (screen_size / 400)
        screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
        pygame.display.set_caption("Let's Player!")
        pygame.mouse.set_visible(0)

    # Prepare background image
        # Game field
        field1, field1Rect = load_image("field.png")
        field2, field2Rect = load_image("field.png")
        field1Rect.midtop = screen.get_rect().midtop
        field2Rect.midbottom = field1Rect.midtop

        # Menu - pause menu Highscore & help
        menu, menuRect = load_image("menu.png")
        menuRect.midtop = screen.get_rect().midtop

        # pause
        pause,pauseRect = load_image('pause.png')
        pause = pygame.transform.scale(pause, (500, 500))
        pauseRect.midtop = screen.get_rect().midtop
        pauseMenu = False 

    # Prepare game contents
        # life
        life1, life1Rect = load_image('heart1.png')
        life2, life2Rect = load_image('heart2.png')
        life3, life3Rect = load_image('heart3.png')

        # Sounds
        missile_sound = load_sound('missile.ogg')
        bomb_sound = load_sound('bomb.ogg')
        alien_explode_sound = load_sound('alien_explode.ogg')
        ship_explode_sound = load_sound('ship_explode.ogg')
        load_music('music_loop.ogg')
        soundFX = Database().getSound()
        music = Database().getSound(music=True)
        if music and pygame.mixer: 
            pygame.mixer.music.play(loops=-1)

        # font
        font = pygame.font.Font(None, round(36*ratio))

        # clock - 60 FPS game
        clockTime = 60  # maximum FPS
        clock = pygame.time.Clock()
        
        # speed
        speed = 1.5
        MasterSprite.speed = speed
        
        # object
        player = Player(screen_size)
        miniplayer = FriendShip(screen_size)
        
        initialMonsterTypes = (Green, Yellow)
        powerTypes = (BombPower, ShieldPower, DoublebeamPower, TriplecupcakePower, BroccoliBeamfast,
                        FriendPower, LifePower)
        bombs = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        
        # Ship Selection
        ship_selection = Ship_selection_check() 
        
        # Score Function
        def kill_bear(monster, monstersLeftThisWave, score) :
            monstersLeftThisWave -= 1
            if monster.pType == 'green':
                score += 1
            elif monster.pType == 'yellow':
                score += 2
            elif monster.pType == 'blue':
                score += 4
            elif monster.pType == 'pink':
                score += 8
            return monstersLeftThisWave, score

    # High Score
        hiScores=Database().getScores()
        highScoreTexts = [font.render("NAME", 1, RED),
                        font.render("SCORE", 1, RED),
                        font.render("ACCURACY", 1, RED)]
        highScorePos = [highScoreTexts[0].get_rect(
                        topleft=screen.get_rect().inflate(-100, -100).topleft),
                        highScoreTexts[1].get_rect(
                        midtop=screen.get_rect().inflate(-100, -100).midtop),
                        highScoreTexts[2].get_rect(
                        topright=screen.get_rect().inflate(-100, -100).topright)]
        for hs in hiScores:
            highScoreTexts.extend([font.render(str(hs[x]), 1, BLACK)
                                for x in range(3)])
            highScorePos.extend([highScoreTexts[x].get_rect(
                topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
    
    # pause menu text  
        blankText=font.render('            ',1,BLACK)
        blankPos=blankText.get_rect(topright=screen.get_rect().center)
        restartText = font.render(' ', 1, BLACK)
        restartPos = restartText.get_rect(topleft=blankPos.bottomleft)   
        hiScoreText = font.render(' ', 1, BLACK)
        hiScorePos = hiScoreText.get_rect(topleft=restartPos.bottomleft)
        fxText = font.render('  ', 1, BLACK)
        fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
        fxOnText = font.render(' ', 1, RED)
        fxOffText = font.render(' ', 1, RED)
        fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
        fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
        musicText = font.render(' ', 1, BLACK)
        musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
        musicOnText = font.render(' ', 1, RED)
        musicOffText = font.render(' ', 1, RED)
        musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
        musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
        helpText=font.render(' ',1,BLACK)
        helpPos=helpText.get_rect(topleft=musicPos.bottomleft)
        quitText = font.render(' ', 1, BLACK)
        quitPos = quitText.get_rect(topleft=helpPos.bottomleft)
        selectText = font.render(' ', 1, BLACK)
        selectPos = selectText.get_rect(topright=restartPos.topleft)
        selection = 1
        showHiScores = False
        showHelp=False 


    #########################
    #    Start Time Mode    #
    #########################

        restart = True
        while restart == True:

        # Prepare game objects : reset
            # Reset Sprite groups
            alldrawings = pygame.sprite.Group()
            allsprites = pygame.sprite.RenderPlain((player,))
            MasterSprite.allsprites = allsprites
            Monster.pool = pygame.sprite.Group(
                [monster(screen_size) for monster in initialMonsterTypes for _ in range(5)])
            Monster.active = pygame.sprite.Group()
            Beam.pool = pygame.sprite.Group([Beam(screen_size) for _ in range(10)]) 
            Beam.active = pygame.sprite.Group()
            Explosion.pool = pygame.sprite.Group([Explosion(screen_size) for _ in range(10)])
            Explosion.active = pygame.sprite.Group()

            # Reset game contents
            monstersThisWave, monstersLeftThisWave, Monster.numOffScreen = 10, 10, 10
            friendship = False
            doublebeam = False
            triplecupcake = False
            broccoli = False
            pepper_chili = False
            bombsHeld = 3
            score = 0
            beamFired = 0
            wave = 1

            # speed
            speed = 1.5 * ratio
            newspeed = 2.5 * ratio
            org_speed = 1.5 * ratio
            player.speed = speed
        
            # Reset all time
            bearPeriod = clockTime // speed
            curTime = 0
            powerTime = 8 * clockTime
            powerTimeLeft = powerTime
            powerdownTime = 8 * clockTime
            powerdownTimeLeft = powerdownTime
            betweenWaveTime = 3 * clockTime
            betweenWaveCount = betweenWaveTime
            
            betweenDoubleTime = 8 * clockTime
            betweenDoubleCount = betweenDoubleTime
            betweenTripleTime = 8 * clockTime
            betweenTripleCount = betweenTripleTime
            friendshipTime = 8 * clockTime
            friendshipCount = friendshipTime
            friendshipBeamTime = 0.2 * clockTime
            friendshipBeamCount = friendshipBeamTime
            broccoliTime  = 8 * clockTime
            broccoliCount = broccoliTime
            pepper_chiliTime  = 8 * clockTime
            pepper_chiliCount = pepper_chiliTime
            
            player.alive = True
            player.life = 3
            player.initializeKeys()
            
            
            player.showChange_ship = False
            
        # Start Game
            while player.alive:
                clock.tick(clockTime)
                
            # Drop Items
                powerTimeLeft -= 1
                powerdownTimeLeft -= 1
                if powerTimeLeft <= 0:
                    powerTimeLeft = powerTime
                    random.choice(powerTypes)(screen_size).add(powers, allsprites)
            # Event Handling
                for event in pygame.event.get():
                    if (event.type == pygame.QUIT
                        or event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    # Resize windowSize
                    elif (event.type == pygame.VIDEORESIZE):
                        screen_size = min(event.w, event.h)
                        if screen_size <= 300:
                            screen_size = 300
                        screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
                        ratio = (screen_size / 400)
                        font = pygame.font.Font(None, round(36*ratio))
                    # Player Moving
                    elif (event.type == pygame.KEYDOWN
                        and event.key in direction.keys()):
                        player.horiz += direction[event.key][0] * player.speed
                        player.vert += direction[event.key][1] * player.speed
                    elif (event.type == pygame.KEYUP
                        and event.key in direction.keys()):
                        player.horiz -= direction[event.key][0] * player.speed
                        player.vert -= direction[event.key][1] * player.speed
                    # Beam
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_SPACE):
                        if doublebeam :
                            Beam.position(player.rect.topleft)
                            Beam.position(player.rect.topright)
                            beamFired += 2
                        elif triplecupcake :
                            Beam.position(player.rect.topleft)
                            Beam.position(player.rect.midtop)
                            Beam.position(player.rect.topright)
                            beamFired += 3
                        elif broccoli :
                            Beam.position(player.rect.midtop)
                            beam.speed = 1.5
                            beamFired += 1
                            
                        # elif pepper_chili:
                        #     Beam.position(player.rect.midtop)
                        #     speed = newspeed
                        #     player.speed = speed
                        #     player.speedUp()
                        #     beamFired += 1
                        else : 
                            Beam.position(player.rect.midtop)
                            beamFired += 1
                        if soundFX:
                            missile_sound.play()
                    # Bomb
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_b):
                        if bombsHeld > 0:
                            bombsHeld -= 1
                            newBomb = player.bomb()
                            newBomb.add(bombs, alldrawings)
                            if soundFX:
                                bomb_sound.play()
                    # Pause Menu
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_p):
                        pauseMenu = True
                        cnt=0
                        
                        while pauseMenu:
                            clock.tick(clockTime)

                            pause_size = (round(pause.get_width() * ratio), round(pause.get_height() * ratio))
                            screen.blit(pygame.transform.scale(pause, pause_size), (0,0))

                            for event in pygame.event.get():
                                if (event.type == pygame.QUIT
                                    or event.type == pygame.KEYDOWN
                                        and event.key == pygame.K_ESCAPE):
                                    pygame.quit()
                                    sys.exit()
                                # Resize windowSize
                                elif (event.type == pygame.VIDEORESIZE):
                                    screen_size = min(event.w, event.h)
                                    if screen_size <= 300:
                                        screen_size = 300
                                    screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
                                    ratio = (screen_size / 500)
                                    font = pygame.font.Font(None, round(36*ratio))
                                elif (event.type == pygame.KEYDOWN  # unpause
                                    and event.key == pygame.K_p):
                                    pauseMenu = False
                                elif (event.type == pygame.KEYDOWN
                                    and event.key == pygame.K_RETURN):
                                    if showHiScores:
                                        showHiScores = False
                                    elif showHelp:
                                        cnt+=1
                                        if cnt%3!=0:
                                            showHelp=True
                                        else:
                                            showHelp=False
                                    elif selection == 1:    
                                        pauseMenu = False
                                        player.alive = False
                                    elif selection == 2:
                                        showHiScores = True
                                    elif selection == 3:
                                        soundFX = not soundFX
                                        if soundFX:
                                            missile_sound.play()
                                        Database.setSound(int(soundFX))
                                    elif selection == 4 and pygame.mixer:
                                        music = not music
                                        if music:
                                            pygame.mixer.music.play(loops=-1)
                                        else:
                                            pygame.mixer.music.stop()
                                        Database.setSound(int(music), music=True)
                                    elif selection == 5:
                                        cnt+=1
                                        showHelp=True
                                    elif selection == 6:
                                        pygame.quit()
                                        sys.exit()
                                elif (event.type == pygame.KEYDOWN
                                    and event.key == pygame.K_UP
                                    and selection > 1
                                    and not showHiScores):
                                    selection -= 1
                                elif (event.type == pygame.KEYDOWN
                                    and event.key == pygame.K_DOWN
                                    and selection < len(pauseMenuDict)
                                    and not showHiScores):
                                    selection += 1
                                
                            blankText=font.render('            ',1,BLACK)
                            blankPos=blankText.get_rect(topright=screen.get_rect().center)
                            restartText = font.render(' ', 1, BLACK)
                            restartPos = restartText.get_rect(topleft=blankPos.bottomleft)   
                            hiScoreText = font.render(' ', 1, BLACK)
                            hiScorePos = hiScoreText.get_rect(topleft=restartPos.bottomleft)
                            fxText = font.render('  ', 1, BLACK)
                            fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
                            fxOnText = font.render(' ', 1, RED)
                            fxOffText = font.render(' ', 1, RED)
                            fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
                            fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
                            musicText = font.render(' ', 1, BLACK)
                            musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
                            musicOnText = font.render(' ', 1, RED)
                            musicOffText = font.render(' ', 1, RED)
                            musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
                            musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
                            helpText=font.render(' ',1,BLACK)
                            helpPos=helpText.get_rect(topleft=musicPos.bottomleft)
                            quitText = font.render(' ', 1, BLACK)
                            quitPos = quitText.get_rect(topleft=helpPos.bottomleft)
                            pauseMenuDict = {1: restartPos, 2: hiScorePos, 3: fxPos, 
                                    4: musicPos, 5: helpPos, 6: quitPos}
                            selectText = font.render(' ', 1, BLACK)
                            selectPos = selectText.get_rect(topright=pauseMenuDict[selection].topleft)

                            highScoreTexts = [font.render("NAME", 1, RED),
                                            font.render("SCORE", 1, RED),
                                            font.render("ACCURACY", 1, RED)]
                            highScorePos = [highScoreTexts[0].get_rect(
                                            topleft=screen.get_rect().inflate(-100, -100).topleft),
                                            highScoreTexts[1].get_rect(
                                            midtop=screen.get_rect().inflate(-100, -100).midtop),
                                            highScoreTexts[2].get_rect(
                                            topright=screen.get_rect().inflate(-100, -100).topright)]
                            for hs in hiScores:
                                highScoreTexts.extend([font.render(str(hs[x]), 1, BLACK)
                                                    for x in range(3)])
                                highScorePos.extend([highScoreTexts[x].get_rect(
                                    topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

                            if showHiScores:
                                menu_size = (round(menu.get_width() * ratio), round(menu.get_height() * ratio))
                                screen.blit(pygame.transform.scale(menu, menu_size), (0,0))                                
                                textOverlays = zip(highScoreTexts, highScorePos)
                            elif showHelp:
                                if cnt%3==1:
                                    menu, menuRect = load_image("help1.png")
                                    menu = pygame.transform.scale(menu, (500, 500))
                                    menuRect.midtop = screen.get_rect().midtop
                                    menu_size = (500,500)
                                    screen.blit(pygame.transform.scale(menu, menu_size), (0,0))
                                    #menu = pygame.transform.scale(menu, (500, 500))
                                elif cnt%3==2:
                                    menu, menuRect = load_image("help2.png") 
                                    menuRect.midtop = screen.get_rect().midtop
                                    menu_size = (500,500)
                                    screen.blit(pygame.transform.scale(menu, menu_size), (0,0))  
                                    #menu = pygame.transform.scale(menu, (500, 500))                                
                            else:
                                textOverlays = zip([blankText,restartText, hiScoreText, helpText, fxText,
                                                    musicText, quitText, selectText,
                                                    fxOnText if soundFX else fxOffText,
                                                    musicOnText if music else musicOffText],
                                                    [blankPos,restartPos, hiScorePos, helpPos, fxPos,
                                                    musicPos, quitPos, selectPos,
                                                    fxOnPos if soundFX else fxOffPos,
                                                    musicOnPos if music else musicOffPos])
                            for txt, pos in textOverlays:
                                screen.blit(txt, pos)

                            alldrawings.update()
                            pygame.display.flip()
                    

            # Collision Detection
                # Monster
                for monster in Monster.active:
                    for bomb in bombs:
                        if pygame.sprite.collide_circle(
                                bomb, monster) and monster in Monster.active:
                            if monster.pType != 'grey' :
                                monster.table()
                                Explosion.position(monster.rect.center)
                                monstersLeftThisWave, score = kill_bear(monster, monstersLeftThisWave, score)
                            beamFired += 1
                            if soundFX:
                                bear_explode_sound.play()
                    for beam in Beam.active:
                        if pygame.sprite.collide_rect(
                                beam, monster) and monster in Monster.active:
                            beam.table()
                            if monster.pType != 'grey' :
                                monster.table()
                                Explosion.position(monster.rect.center)
                                monstersLeftThisWave, score = kill_bear(monster, monstersLeftThisWave, score)
                            if soundFX:
                                bear_explode_sound.play()
                    if pygame.sprite.collide_rect(monster, player):
                        if player.shieldUp:
                            monster.table()
                            Explosion.position(monster.rect.center)
                            monstersLeftThisWave, score = kill_bear(monster, monstersLeftThisWave, score)
                            beamFired += 1
                            player.shieldUp = False
                        elif player.life > 1:   # life
                            monster.table()
                            Explosion.position(monster.rect.center)
                            monstersLeftThisWave -= 1
                            score += 1
                            player.life -= 1
                        else:
                            restart = False
                            player.alive = False
                            player.remove(allsprites)
                            Explosion.position(player.rect.center)
                            if soundFX:
                                kirin_explode_sound.play() ## 변경사항

                # PowerUps
                for power in powers:
                    if pygame.sprite.collide_circle(power, player):
                        if power.pType == 'bomb':
                            bombsHeld += 1
                        elif power.pType == 'shield':
                            player.shieldUp = True
                        elif power.pType == 'doublebeam' :
                            doublebeam = True
                        elif power.pType == 'triplecupcake' :
                            triplecupcake = True
                        elif power.pType == 'broccoli' :
                            broccoli = True
                        elif power.pType == 'life':
                            if player.life < 3:
                                player.life += 1 
                        elif power.pType == 'friendShip' :
                            friendship = True
                            MasterSprite.allsprites.add(miniplayer) 
                            allsprites.update(screen_size)
                            allsprites.draw(screen)
                        power.kill()
                    elif power.rect.top > power.area.bottom:
                        power.kill()

            # Update Monsters
                if curTime <= 0 and monstersLeftThisWave > 0:
                    Monster.position()
                    curTime = bearPeriod
                elif curTime > 0:
                    curTime -= 1

            # Update text overlays
                waveText = font.render("Wave: " + str(wave), 1, BLACK)
                leftText = font.render("Bears Left: " + str(monstersLeftThisWave), 1, BLACK)
                scoreText = font.render("Score: " + str(score), 1, BLACK)
                bombText = font.render("Fart Bombs: " + str(bombsHeld), 1, BLACK)

                wavePos = waveText.get_rect(topleft=screen.get_rect().topleft)
                leftPos = leftText.get_rect(midtop=screen.get_rect().midtop)
                scorePos = scoreText.get_rect(topright=screen.get_rect().topright)
                bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)

                text = [waveText, leftText, scoreText, bombText]
                textposition = [wavePos, leftPos, scorePos, bombPos]

            # Update using items
                # item - doublebeam
                if doublebeam:
                    if betweenDoubleCount > 0:
                        betweenDoubleCount -= 1
                    elif betweenDoubleCount == 0:
                        doublebeam = False
                        betweenDoubleCount = betweenDoubleTime
                if triplecupcake:
                    if betweenTripleCount > 0:
                        betweenTripleCount -= 1
                    elif betweenTripleCount == 0:
                        triplecupcake = False
                        betweenTripleCount = betweenTripleTime
                if broccoli:
                    if broccoliCount > 0:
                        broccoliCount -= 1
                    elif broccoliCount == 0:
                        beam.speed = 1
                        broccoli = False
                        broccoliCount = broccoliTime
                # if pepper_chili:
                #     if pepper_chiliCount > 0:
                #         pepper_chiliCount -= 1
                #     elif pepper_chiliCount == 0:
                #         speed = org_speed
                #         player.speed = speed
                #         player.speedUp()
                #         pepper_chili = False
                #         pepper_chiliCount = pepper_chiliTime
                # item - friendship
                miniplayer.rect.bottomright = player.rect.bottomleft
                if friendship:
                    # friendship
                    if friendshipCount > 0:
                        friendshipCount -= 1
                    elif friendshipCount == 0:
                        friendship = False
                        miniplayer.remove()
                        friendshipCount = friendshipTime
                    # friendship's beam
                    if friendshipBeamCount > 0:
                        friendshipBeamCount -= 1
                    elif friendshipBeamCount == 0:
                        friendshipBeamCount = friendshipBeamTime
                        Beam.position(miniplayer.rect.midtop)

            # betweenWaveCount - Detertmine when to move to next wave
                if monstersLeftThisWave <= 0:
                    if betweenWaveCount > 0:
                        betweenWaveCount -= 1
                        nextWaveText = font.render(
                            'Wave ' + str(wave + 1) + ' in', 1, BLACK)
                        nextWaveNum = font.render(
                            str((betweenWaveCount // clockTime) + 1), 1, BLACK)
                        text.extend([nextWaveText, nextWaveNum])
                        nextWavePos = nextWaveText.get_rect(
                            center=screen.get_rect().center)
                        nextWaveNumPos = nextWaveNum.get_rect(
                            midtop=nextWavePos.midbottom)
                        textposition.extend([nextWavePos, nextWaveNumPos])
                        if wave % 4 == 0:
                            speedUpText = font.render('SPEED UP!', 1, RED)
                            speedUpPos = speedUpText.get_rect(
                                midtop=nextWaveNumPos.midbottom)
                            text.append(speedUpText)
                            textposition.append(speedUpPos)
                    elif betweenWaveCount == 0:
                        if wave % 4 == 0:
                            speed += 0.5
                            MasterSprite.speed = speed
                            player.initializeKeys()
                            monstersThisWave = 10
                            monstersLeftThisWave = Monster.numOffScreen = monstersThisWave
                        else:
                            monstersThisWave *= 2
                            monstersLeftThisWave = Monster.numOffScreen = monstersThisWave
                        if wave == 1:
                            Monster.pool.add([Grey(screen_size) for _ in range(5)])
                        if wave == 2:
                            Monster.pool.add([Blue(screen_size) for _ in range(5)])
                        if wave == 3:
                            Monster.pool.add([Pink(screen_size) for _ in range(5)])
                        wave += 1
                        betweenWaveCount = betweenWaveTime

                textOverlays = zip(text, textposition)

            # moving field - Resize windowSize
                field1Rect.y += int(2 * ratio)
                field2Rect.y += int(2 * ratio)
                if field1Rect.y >= screen_size:
                    field1Rect.midbottom = field2Rect.midtop
                if field2Rect.y >= screen_size:
                    field2Rect.midbottom = field1Rect.midtop
                
                field_size = (round(field1.get_width() * ratio), round(field1.get_height() * ratio))
                screen.blit(pygame.transform.scale(field1, field_size), (0,field1Rect.y))
                screen.blit(pygame.transform.scale(field2, field_size), (0,field2Rect.y))

            # Update and draw all sprites and text                                   
                allsprites.update(screen_size)
                allsprites.draw(screen)
                alldrawings.update()
                for txt, pos in textOverlays:
                    screen.blit(txt, pos)

            # Update life
                life1Rect.topleft = wavePos.bottomleft
                life2Rect.topleft = wavePos.bottomleft
                life3Rect.topleft = wavePos.bottomleft

                life_size = (round(life1.get_width() * ratio), round(life1.get_height() * ratio))
                if player.life == 3:
                    screen.blit(pygame.transform.scale(life3, life_size), life3Rect)
                elif player.life == 2:
                    screen.blit(pygame.transform.scale(life2, life_size), life2Rect)
                elif player.life == 1:
                    screen.blit(pygame.transform.scale(life1, life_size), life1Rect)

                pygame.display.flip()


        # Data for Highscore
            accuracy = round(score / beamFired, 4) if beamFired > 0 else 0.0
            isHiScore = len(hiScores) < Database().numScores or score > hiScores[-1][1]
            name = ''
            nameBuffer = []


    #########################
    #    After Game Loop    #
    #########################

        while True:
            clock.tick(clockTime)

        # Event Handling
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                    or not isHiScore
                    and event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    return False
                # Resize windowSize
                elif (event.type == pygame.VIDEORESIZE):
                    screen_size = min(event.w, event.h)
                    if screen_size <= 300:
                        screen_size = 300
                    screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
                    ratio = (screen_size / 500)
                    font = pygame.font.Font(None, round(36*ratio))
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and not isHiScore):
                    return True
                elif (event.type == pygame.KEYDOWN
                    and event.key in Keyboard.keys.keys()
                    and len(nameBuffer) < 8):
                    nameBuffer.append(Keyboard.keys[event.key])
                    name = ''.join(nameBuffer)
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_BACKSPACE
                    and len(nameBuffer) > 0):
                    nameBuffer.pop()
                    name = ''.join(nameBuffer)
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and len(name) > 0):
                    if Database().name_not_exists(name,mode=SINGLE):
                        Database().setScore(hiScores,name, score, accuracy)
                        return True 
                    else:
                        print("중복된 이름 존재함")
                     
            if isHiScore:
                hiScoreText = font.render('SCORE', 1, RED)
                hiScorePos = hiScoreText.get_rect(
                    midbottom=screen.get_rect().center)
                scoreText = font.render(str(score), 1, BLACK)
                scorePos = scoreText.get_rect(midtop=hiScorePos.midbottom)
                enterNameText = font.render('ENTER YOUR NAME:', 1, RED)
                enterNamePos = enterNameText.get_rect(midtop=scorePos.midbottom)
                nameText = font.render(name, 1, WHITE)
                namePos = nameText.get_rect(midtop=enterNamePos.midbottom)
                textOverlay = zip([hiScoreText, scoreText,
                                enterNameText, nameText],
                                [hiScorePos, scorePos,
                                enterNamePos, namePos])
            else:
                gameOverText = font.render('GAME OVER', 1, BLACK)
                gameOverPos = gameOverText.get_rect(
                    center=screen.get_rect().center)
                scoreText = font.render('SCORE: {}'.format(score), 1, BLACK)
                scorePos = scoreText.get_rect(midtop=gameOverPos.midbottom)
                textOverlay = zip([gameOverText, scoreText],
                                [gameOverPos, scorePos])

        # moving field         
            field1Rect.y += int(2 * ratio)
            field2Rect.y += int(2 * ratio)
            if field1Rect.y >= screen_size:
                field1Rect.midbottom = field2Rect.midtop
            if field2Rect.y >= screen_size:
                field2Rect.midbottom = field1Rect.midtop
            
            field_size = (round(field1.get_width() * ratio), round(field1.get_height() * ratio))
            screen.blit(pygame.transform.scale(field1, field_size), (0,field1Rect.y))
            screen.blit(pygame.transform.scale(field2, field_size), (0,field2Rect.y))

        # Update and draw all sprites
            allsprites.update(screen_size)
            allsprites.draw(screen)
            alldrawings.update()
            for txt, pos in textOverlay:
                screen.blit(txt, pos)

            pygame.display.flip()