import numpy as np
import cv2
from math import *
import time

'''
PERSPECTIVE TRANSFORM
'''
#WARPED PERSPECTIVE TRANSFORM
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    masked = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    return warped, masked

'''
COLOR THRESHOLDING OF GROUND, OBSTACLES, AND ROCKS
'''
#GROUND
def navigable_thresh(img, rgb_thresh=(160,160,160)):
    threshed_ground = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    threshed_ground[above_thresh] = 1
    return threshed_ground
'''navi_world = navigable_thresh(warped)'''

#OBSTACLES
'''obst_world = np.absolute(np.float32(threshed) - 1) * masked'''

#GOLD ROCKS
def rock_thresh(img):
    #hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([4,100,100])
    upper_yellow = np.array([33,255,255])
    threshed_sample = cv2.inRange(img, lower_yellow, upper_yellow)
    return threshed_sample
'''rock_world = rock_thresh(warped_rock)'''

'''
COORDINATE TRANSFORMATIONS
'''
#CONVERT FROM IMAGE COORDS TO ROVER COORDS
def rover_coords(binary_img):
    ypos, xpos = binary_img.nonzero()
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel

#CONVERT TO RADIAL COORDS IN ROVER SPACE
def to_polar_coords(x_pixel, y_pixel):
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

#MAP ROVER SPACE PIXELS TO WORLD SPACE
def rotate_pix(xpix, ypix, yaw):
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    return xpix_translated, ypix_translated

#APPLY ROTATION, TRANSLATION AND CLIPPING
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    return x_pix_world, y_pix_world

'''
PERCEPTION FUNCTION
'''
def perception_step(Rover):
    # Perform perception steps to update Rover()

    # TODO:
    # NOTE: camera image is coming to you in Rover.img
    image = Rover.img
    image_hsv = Rover.hsv

    # 1) Define source and destination points for perspective transform
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                      [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                      ])
    # 2) Apply perspective transform
    warped, masked = perspect_transform(image, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navi_world = navigable_thresh(warped)
    obst_world = np.absolute(np.float32(navi_world) - 1) * masked

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,2] = navi_world * 255
    Rover.vision_image[:,:,0] = obst_world * 255

    # 5) Convert map image pixel values to rover-centric coords
    navi_xpix, navi_ypix = rover_coords(navi_world)

    # 6) Convert rover-centric pixel values to world coordinates
    world_size = Rover.worldmap.shape[0]
    scale = 2 * dst_size
    navi_x_world, navi_y_world = pix_to_world(navi_xpix, navi_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
    obst_xpix, obst_ypix = rover_coords(obst_world)
    obst_x_world, obst_y_world = pix_to_world(obst_xpix, obst_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    if ((Rover.pitch > 359.25 or Rover.pitch < 0.75) and (Rover.roll > 359.25 or Rover.roll < 0.75)):
        Rover.worldmap[navi_y_world, navi_x_world, 2] += 25
        Rover.worldmap[obst_y_world, obst_x_world, 0] += 1
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1


    # 8) Convert rover-centric pixel positions to polar coordinates
    dist, angles = to_polar_coords(navi_xpix, navi_ypix)
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    Rover.nav_dists, Rover.nav_angles = dist, angles

    #SEE IF WE CAN FIND SOME ROCKS
    warped_rock,_ = perspect_transform(image_hsv, source, destination)
    rock_world = rock_thresh(warped_rock)
    if rock_world.any():
        #CONVERT FROM IMAGE COORDS TO ROVER COORDS - ROCKS
        rock_xpix, rock_ypix = rover_coords(rock_world)
        #PIX_TO_WORLD(XPIX, YPIX, XPOS, YPOS, YAW, WORLD_SIZE, SCALE)
        #ROVER-CENTRIC COORD PIXEL VALUES - ROCKS
        rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
        #POLAR COORDS
        rock_dist, rock_ang = to_polar_coords(rock_xpix, rock_ypix)
        #CENTER OF ROCKS
        rock_idx_dist = np.argmin(rock_dist)
        rock_idx_ang = np.argmin(rock_ang)
        rock_xcen = rock_x_world[rock_idx_dist]
        rock_ycen = rock_y_world[rock_idx_dist]
        #UPDATE WORLDMAP
        Rover.worldmap[rock_ycen, rock_xcen, 1] += 255
        Rover.vision_image[:, :, 1] = rock_world * 255
        Rover.rock_dists, Rover.rock_angles = rock_dist, rock_ang
        Rover.rock_idx_dist = rock_idx_dist
        Rover.rock_idx_ang = rock_idx_ang
    else:
        Rover.vision_image[:, :, 1] = 0
        Rover.rock_angles = None
        Rover.rock_idx_dist = None
        Rover.rock_idx_ang = None


    #rock_world_pos = Rover.worldmap[:,:,1].nonzero()
    #if rock_idx_dist.any =! None:
    #    if np.min(rock_idx_dist) < 5:
    #        rock_xpix, rock_ypix = rover_coords(rock_world)
    #        rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
    #        rock_dist, rock_ang = to_polar_coords(rock_xpix, rock_ypix)
    #        Rover.rock_dists, Rover.rock_angles = rock_dist, rock_ang
    #        rock_idx_dist = np.argmin(rock_dist)
    #        Rover.rock_idx_dist = rock_idx_dist
    #else:
    #    Rover.rock_idx_dist = None
    #    Rover.rock_angles = None


        #Rover.rock_angles = None
        #Rover.rock_idx_dist = None

    #SEE IF WE CAN PLOT A PATH TO SOME ROCKS
    #rock_world_pos = Rover.worldmap[:,:,1].nonzero()

    #if rock_world_pos[0].any():
        #CONVERT FROM IMAGE COORDS TO ROVER COORDS - ROCKS
    #    rock_xpix, rock_ypix = rover_coords(rock_world)
        #PIX_TO_WORLD(XPIX, YPIX, XPOS, YPOS, YAW, WORLD_SIZE, SCALE)
        #ROVER-CENTRIC COORD PIXEL VALUES - ROCKS
    #    rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size, scale)
        #POLAR COORDS
    #    rock_dist, rock_ang = to_polar_coords(rock_xpix, rock_ypix)



    return Rover
