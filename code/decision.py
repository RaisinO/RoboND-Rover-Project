import numpy as np
from math import *
import time

stuck_start_time = time.time()

def get_unstuck(Rover):
    global stuck_start_time
    Rover.throttle = 0
    Rover.brake = 0
    Rover.steer = -15
    return Rover

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(Rover):

    global stuck_start_time

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

#STEER ROVER TO SAMPLE DIRECTION
    if Rover.rock_idx_mean_ang is not None:
        if Rover.mode == 'forward':

            #STUCK CHECK
            if Rover.vel < 0.1 and Rover.throttle!=0:
                if time.time() - stuck_start_time > 2:
                    Rover = get_unstuck(Rover)
                    return Rover
            #RESET STUCK TIME
            else:
                stuck_start_time = time.time()

            if len(Rover.nav_angles) >= Rover.stop_forward:
                if Rover.vel < Rover.max_vel:
                    Rover.throttle = Rover.throttle_set
                else:
                    Rover.throttle = 0
                Rover.brake = 0
                Rover.steer = degrees(Rover.rock_idx_mean_ang)
            #IF THERE IS NO CLEAR PATH TO THE SAMPLE
            elif len(Rover.nav_angles) < Rover.stop_forward:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

        elif Rover.mode == 'stop':
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            elif Rover.vel <= 0.2:
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    Rover.brake = 0
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    Rover.throttle = Rover.throttle_set
                    Rover.brake = 0
                    #SET STEER TO THE MEAN ANGLE OF THE ROCK
                    Rover.steer = degrees(Rover.rock_idx_mean_ang)
                    Rover.mode = 'forward'
        return Rover

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward':

            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover
