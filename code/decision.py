import numpy as np
from math import *
import time

rover_time_count = time.time()

def right_adjustment(Rover):
    global rover_time_count
    Rover.throttle = 0
    Rover.brake = 0
    Rover.steer = -15
    time.sleep(0.5)
    return Rover

def left_adjustment(Rover):
    global rover_time_count
    Rover.throttle = 0
    Rover.brake = 0
    Rover.steer = 15
    time.sleep(0.5)
    return Rover

def forward_adjustment(Rover):
    global rover_time_count
    Rover.throttle = 0.5
    Rover.brake = 0
    Rover.steer = 0
    time.sleep(2)
    return Rover

def backward_adjustment(Rover):
    global rover_time_count
    Rover.throttle = -0.5
    Rover.brake = 0
    Rover.steer = 0
    time.sleep(2)
    return Rover

def victory_dance(Rover):
    left_adjustment(Rover)
    left_adjustment(Rover)
    right_adjustment(Rover)
    right_adjustment(Rover)
    forward_adjustment(Rover)
    backward_adjustment(Rover)
    return Rover

def get_unstuck(Rover):
    backward_adjustment(Rover)
    left_adjustment(Rover)
    return(Rover)

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(Rover):

    global rover_time_count

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

#SAVE THE STARTING POSITION
    if Rover.start_pos==None:
        Rover.start_pos = ( Rover.pos[0],Rover.pos[1])
        print("Saving start position as:", Rover.start_pos)

#DISTANCE TO HOME AND QUIT WHEN ALL SAMPLES COLLECTED
    Rover.distance_home = sqrt((Rover.pos[1] - Rover.start_pos[1])**2 +(Rover.pos[0] - Rover.start_pos[0])**2)
    if Rover.samples_collected == 6:
        if Rover.distance_home < 5:
            print("MISSION COMPLETE: ALL 6 SAMPLES COLLECTED AND RETURNED TO STARTING POSITION!")
            Rover.mode = "MISSION COMPLETE"
            Rover.throttle = 0
            Rover.steering = 0
            Rover.brake = Rover.brake_set
            return Rover

#IS THE MISSION COMPLETE?
    if Rover.mode == "MISSION COMPLETE":
        Rover = victory_dance(Rover)
        quit()

#SEND PICKUP COMMAND?
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
        return Rover

#STOP IF ROVER IS NEAR SAMPLE
    if Rover.near_sample:
        Rover.mode = 'stop'
        Rover.throttle = 0
        Rover.brake = Rover.brake_set
        return Rover

#STUCK CHECK
    if Rover.vel < 0.1 and Rover.throttle!=0:
        if time.time() - rover_time_count > 1.5:
            Rover = get_unstuck(Rover)
            return Rover
    #RESET STUCK TIME
    else:
        rover_time_count = time.time()

#ROVER TO SAMPLE NAVIGATION TREE
    #IS THERE A SAMPLE NEARBY TO DRIVE TO?
    if Rover.rock_angles is not None:
        #CHECK ROVER.MODE STATUS. FORWARD?
        if Rover.mode == 'forward':
            #SEE IF THERE IS NAVIGABLE TERRAIN IN FRONT OF US TO DRIVE
            if len(Rover.nav_angles) >= Rover.stop_forward:
                #IF MODE IS FORWARD, NAVIGABLE TERRAIN LOOKS GOOD
                #AND VELOCITY BELOW MAX, THEN THROTTLE
                if Rover.vel < Rover.max_vel:
                    Rover.throttle = Rover.throttle_set
                #OTHERWISE COAST
                else:
                    Rover.throttle = 0
                Rover.brake = 0
                #SET STEERING TO AVERAGE ANGLE CLIPPED TO THE RANGE OF +/- 15 DEGREES
                Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)

        #IF THERE'S A LACK OF NAVIGABLE TERRAIN PIXELS THEN GO TO 'STOP' MODE
        elif len(Rover.nav_angles) < Rover.stop_forward:
                #SET MODE TO 'STOP' AND HIT THE BRAKES
                Rover.throttle = 0
                #SET BRAKE TO STORED BRAKE VALUE
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

        #CHECK ROVER.MODE STATUS. STOPPED?
        elif Rover.mode == 'stop':
            #IF IN 'STOP' MODE BUT MOVING KEEP BRAKING
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            #IF MOVING < 0.2 THEN DO SOMETHING ELSE
            elif Rover.vel <= 0.2:
                #STOPPED. NOW CHECK VISION DATA FOR PATH FORWARD
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    #RELEASE BRAKE TO ALLOW TURNING
                    Rover.brake = 0
                    #4-WHEEL TURN TO THE RIGHT
                    Rover.steer = -15 #CAN DEFINITELY BE MORE CLEVER HERE
                    time.sleep(0.5) #CAN DEFINITELY BE MORE CLEVER HERE
                #IF STOPPED BUT THERE IS SUFFICIENT NAVIGABLE TERRAIN SET TO GO
                if len(Rover.nav_angles) >= Rover.go_forward:
                    #SET THROTTLE TO STORED VALUE
                    Rover.throttle = Rover.throttle_set
                    Rover.brake = 0
                    #SET STEER TO THE MEAN ANGLE OF THE ROCK
                    Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
        return Rover

#EXPLORATION & DRIVING TREE
    #IS THERE NAVIGATION DATA TO DRIVE WITH?
    if Rover.nav_angles is not None:
        #CHECK ROVER.MODE STATUS. FORWARD?
        if Rover.mode == 'forward':
            #SEE IF THERE IS NAVIGABLE TERRAIN IN FRONT OF US TO DRIVE
            if len(Rover.nav_angles) >= Rover.stop_forward:
                #IF MODE IS FORWARD, NAVIGABLE TERRAIN LOOKS GOOD
                #AND VELOCITY BELOW MAX, THEN THROTTLE
                if Rover.vel < Rover.max_vel:
                    Rover.throttle = Rover.throttle_set
                #OTHERWISE COAST
                else:
                    Rover.throttle = 0
                Rover.brake = 0
                #SET STEERING TO AVERAGE ANGLE CLIPPED TO THE RANGE OF +/- 15 DEGREES
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)

            #IF THERE'S A LACK OF NAVIGABLE TERRAIN PIXELS THEN GO TO 'STOP' MODE
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    #SET MODE TO 'STOP' AND HIT THE BRAKES
                    Rover.throttle = 0
                    #SET BRAKE TO STORED BRAKE VALUE
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        #CHECK ROVER.MODE STATUS. STOPPED?
        elif Rover.mode == 'stop':
            #IF IN 'STOP' MODE BUT MOVING KEEP BRAKING
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            #IF MOVING < 0.2 THEN DO SOMETHING ELSE
            elif Rover.vel <= 0.2:
                #STOPPED. NOW CHECK VISION DATA FOR PATH FORWARD
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    #RELEASE BRAKE TO ALLOW TURNING
                    Rover.brake = 0
                    #4-WHEEL TURN TO THE RIGHT
                    Rover.steer = -15 #CAN DEFINITELY BE MORE CLEVER HERE
                    time.sleep(0.5) #CAN DEFINITELY BE MORE CLEVER HERE
                #IF STOPPED BUT THERE IS SUFFICIENT NAVIGABLE TERRAIN SET TO GO
                if len(Rover.nav_angles) >= Rover.go_forward:
                    #SET THROTTLE TO STORED VALUE
                    Rover.throttle = Rover.throttle_set
                    #RELEASE THE BRAKE
                    Rover.brake = 0
                    #SET STEER TO MEAN ANGLE
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover
