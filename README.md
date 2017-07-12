## Project: Search and Sample Return
## by Richard Schure

**The goals / steps of this project are the following:**

**Training / Calibration**

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points

---
### Overview

This write up addresses the subjects in the rubric, how each was addressed, and the process in which I arrived at the final production. This is the first project in the Robotics Nano Degree program and the project was based on the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html).

In this project I gained direct experience in the three essential elements of Robotics: perception, decision making and actuation.  I learned about the elements of the coding involved by utilizing both a Jupyter Notebook and a simulator environment built with the Unity game engine.

The notebook was crucial in developing an understanding of how images are processed for the robot to perceive navigable terrain, obstacles, and samples of interest. This was the first time that I have used a Jupyter Notebook and I found it to be an extremely powerful tool for testing the layout of code, ideas on how to improve code effectively, error discovery and correction, and so much more. I spent a good deal of time working through many elements of OpenCV to see which method would work best for perception in this project. I spent a good deal of time exploring not just color thresholding but also methods like Otsu's Method of Binarization - which I found intriguing, fascinating, powerful, challenging, and ultimately unsuitable for this application. There were several times that I felt quite stuck, but through perseverance, the slack channel, stack overflow, asking friends, and the like, I was able to complete and exceed the requirements of the project by having the rover successfully navigate, map the area with a fidelity > 70%, pick up all six samples, and return to the starting point.


### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

As I mention above, the notebook was instrumental in working through this project. I needed to transform the robot's forward camera view into an overhead view, determine: navigable terrain, obstacles, and rock samples, as well as create a map of the area in which the rover was exploring. In the notebook I performed geometric transforms, thresholding, and image processing with OpenCV. Using OpenCV the robot could analyze its surroundings and achieve the desired results - mapping with a high level of fidelity and locating rock samples. With good processed image information at hand, the robot was able to decide how to proceed through the environment, locate all of the rock samples, retrieve the rock samples and return to the starting position.

I first worked with a function called 'Perspective Transform'. This function performs a geometric transformation of front facing camera information. I observed that front facing camera information is trapezoidal in nature. For mapping, an overhead view is required which meant that I needed to convert this front facing trapezoidal image into a square. The squares in the grid displayed on the ground are one square meter - i.e. they are one meter by one meter - and the 'source' and 'destination' points originate from the corner points of the grid. This conversion to a square was achieved by using an OpenCV function called cv2.warpPerspective and was very effective.

![Example Grid](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/example_grid.jpg)

![Warped Example Grid](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/warped_example_grid.jpg)

The next set of code that I worked with regarded color thresholding and took the image generated by the 'Perspective Transform' and modified the color information in the image. In looking at the environment, it was possible to identify four different types of terrain with color information. These were navigable areas, obstacles, rocks, and the sky. Fortunately, obstacles and sky had similar enough RGB color values that it was possible to threshold against these values in order to accurately detect navigable terrain. Once the navigable terrain was threshed, I went back and created a mask based upon the original warped image in the 'Perspective Transform' function. This allowed me to create an overhead view of the obstacles that was the exact opposite of the overhead view of navigable terrain. As for the rocks, luckily, these were all yellow/gold in color. I used color thresholding in OpenCV to create an image of these in HSV and turned the resultant values into a warped overhead view of the rocks. All of the final overhead views are binary images, which was later useful in creating a colored map of navigable areas, obstacles, and rocks.

![Example Rock](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/example_rock.jpg)

![Warped Example Rock](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/warped_example_rock.jpg)

![Navigable World](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/navi_world.jpg)

![Masked World](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/warped_masked.jpg)

![Obstacle World](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/obst_world.jpg)

![Rock World](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/rock_world.jpg)

With the color thresholding in place for navigable terrain, obstacles, and rocks, I then set to the task of modifying the coordinate system. This was necessary in order to navigate effectively, create a map that could be tested against the 'ground truth' map, and effectively locate rock samples to be collected. The functions that achieved this result are 'rover_coords', 'to_polar_coords', 'rotate_pix', 'translate_pix', and 'pix_to_world'. The 'rover_coords' function takes the output of the previous two functions and finds the x pixel and y pixel location of the rover's navigable terrain - and later rock samples. These values are then input to the 'to_polar_coords' function which transforms the x pixel and y pixel locations into rover centric polar coordinates, which allowed me to identify the distance and bearing of navigable terrain and rock samples. The next step is to convert from rover centric values into world centric values. This was accomplished with the 'rotate_pix' function which takes the rover centric values and performs a coordinate rotation by taking the result of the 'rover_coords' function with rover yaw values and then passing them through the appropriate sin and cos relationships for a 90 degree ccw rotation. The 'translate_pix' and 'pix_to_world' functions were essential in creating a well oriented world centric map that could be tested against the provided 'ground truth' map. I have provided images below that demonstrate the output of these functions. I have also included an image with a navigation vector that was calculated using mean of the binary navigable pixels.

![Coord Transform Random Example Image](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/coord_random_image.jpg)

![Coord Transform Random Warped Image](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/coord_warped_image.jpg)

![Coord Transform Random Navigable Image](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/coord_navi_world.jpg)

![Coord Transform Random Navigable Vector](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/coord_navi_vector.jpg)


#### 2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.

The 'process_image()' function takes all of the previous functions and compiles test images into a video using moviepy. An additional step required was to create a class to be the data container for test images and telemetry. The test data was a recording of a short manual run in the simulated environment. I also recorded my own manual run and tested this data as well. The recorded data was in the form of a csv file and jpg images. The contents of the csv file were image names, x position, y position, and yaw values. The csv values were passed through: the perspective transform functions - 'warped', 'masked', the color threshold functions - 'navi_world', 'obst_world', 'rock_world', pixel values to rover-centric coord functions - 'navi_x_pix', 'navi_y_pix', the convert rover-centric pixel values to world coords - including the data bucket class - 'navi_x_world', 'navi_y_world', 'obst_x_pix', 'obst_y_pix', 'obst_x_world', 'obst_y_world'. I also updated the data class worldmap with the blue navigable pixels and red obstacle pixels. To map rocks, I added an if warped_rock(): statement and marked the rocks as white when found. The process is repeated for each entry in the csv file and the image information is stitched together with moviepy into the video shown below.

![Test Mapping Video](https://github.com/RaisinO/RoboND-Rover-Project/output/test_mapping.mp4)

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

The 'perception_step()' function is very similar to the 'process_image()' function. The first difference of note is that images arrive as Rover.img. For OpenCV to function correctly with HSV thresholding, I added color conversion for rover images to supporting_functions.py and named the color converted image Rover.hsv. Prior to understanding this, I had been attempting to use the same methods as in the notebook - i.e. reading in the image and then converting the color information - which generated errors. Another section that is different than 'process_image()' is the updating function for the worldmap. In this section I added a section that takes the pitch and roll of the rover into account. When the pitch and roll are close to one degree out of level, the map accuracy drops dramatically. Limiting the worldmap updates to a range of < 0.75 degrees from level greatly improves the fidelity of the worldmap vs ground truth. With this improvement, I was able to reliably achieve a fidelity of > 70%. Also, in this section updates to the worldmap for navigable terrain are favored over obstacles at a 25:1 ratio, so when navigable terrain is found it is assumed that it is definitely navigable. Another section that was added has to do with locating rocks, mapping them to the worldmap, and finding a vector path to the rocks for the rover to pick them up.

In the 'decision_step()' I started out by saving the Rover.start_pos so that when it had collected all of the samples it would know when it had arrived home. After some trial and error, I then added a function to help the rover break out of stuck senarios by detecting when the throttle was set to a value other than zero and the velocity remained zero for one second. This triggered the rover to follow a simple routine to get unsuck by rotating to the left for 0.1 seconds at a time. Usually this worked but sometimes it would fail and manual control was needed to help the rover get unstuck - especially on certain rocks where the rover would become 'high centered'. I then set to add a series of statements for navigating towards and picking up the samples. The 'rover to sample navigation' decision tree is similar to the 'driving and exploration' decision tree and this section gets the rover close enough to the sample to trigger the 'sample pickup' decision tree. Once the rover had driven towards the sample, it stopped, picked up the sample, and turned around so that it could continue on in the 'driving and exploration' decision tree. For fun, I also added a mission complete section where text is printed out and the rover does a little victory spin dance.

I added some image color conversions to 'supporting_functions.py' section so that I would be able to process HSV images with OpenCV. Other than that, 'supporting_functions.py' is the same as provided.

In 'drive_rover.py', I added 'self.start_pos', 'self.rock_angles', 'self.rock_dists', and 'self.rock_idx_dist' to assist in saving the start position and navigation towards rock samples. I also raised the throttle setting to 0.25 so that the rover had enough torque and forward momentum to get away from the walls after picking up a sample.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.

In autonomous mode, the rover can definitely navigate the terrain, map autonomously, and detect rocks quite well! The rover will also fully navigate the map with a little assistance around the rock obstacles at a fidelity > 70%. The rocks are all detected and usually all are picked up as well, though this takes some time for it to complete on it's own. Once the rover picks up all of the rock samples, it returns to the starting location and does a victory dance. It's quite satisfying to see it complete the mission.

One area of concern is that I have had quite a bit of trouble getting the rover to sometimes recognize when it is stuck. The problem is sporadic and I believe that it has something to do with the rover thinking that it can navigate still because there is good terrain in front of it. Another challenging area is that the stones are often very close to the walls, they can be somewhat difficult for the rover to approach in a straight line. It also sometimes will speed on by. I would have liked to have spent more time refining the approach to the rock samples. I have some ideas on how to get the rover to approach in an arc instead of a straight line, but I couldn't get any of them to work very well. I also had been working on getting the rover to stop when it got near a sample, but couldn't get this to work well either. There were times that I created a bad set of decisions when doing this that dropped my frame rate below ten and to date I have not figured out a correct and efficient decision tree to accomplish this task. I'm sure that if I spent more time on this, it could be achieved.

I also would like to improve the rover's collision detection for the rocks in the environment. Perhaps combining some other thresholding techniques with the ones that I have used would be effective in accomplishing this. As I mentioned in the beginning, I experimented with Otsu's Method of Binarization but couldn't get it to work effectively by combining the two sets of data. I'm sure that I just need more practice and experience. Overall this was a challenging project that really taught me a lot about robotics. I'm looking forward to more! Thanks for the fun project.

![Success](https://github.com/RaisinO/RoboND-Rover-Project/writeup_images/successful_run.jpg)

**Simulator Settings: 1600x900, windowed, graphics quality: Fantastic, Reported FPS: 28-40**
