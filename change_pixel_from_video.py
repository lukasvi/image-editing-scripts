"""
Author: Lukas Vilsmeier
This script evens out dead pixels in a given video.
The area of dead pixels needs to be specified.
How it works:
The malfunctioning area gets filled with valid pixels from outside.
Only works for small malfunctioning areas.
"""

import cv2
import math
import os
import sys
from ffpyplayer.player import MediaPlayer
from time import process_time

##########
## CHANGE THIS
##########

# Top left corner of the area
pixel_from = (948, 230)
# Bottom right corner of the area
pixel_to = (954, 235)

# Set this to true if you want every 100 frames to be saved as comparison
reference_every_100_frames = False

# If w want a video with audio
with_audio = False

# Input video
input_path = "Mama_50_Jahre_220221_Test_01_Trim.mp4"

# Properties of our video
fps = 30
dimensions = (1920, 1080)

##########
## CHANGE THIS
##########


def main():

    t_start = process_time()

    # Middle pixel is used as reference point
    pixel_middle_x = math.ceil((pixel_from[0] + pixel_to[0]) / 2)
    pixel_middle_y= math.ceil((pixel_from[1] + pixel_to[1]) / 2)
    pixel_middle = (pixel_middle_x, pixel_middle_y)

    # Getting the video
    cap = cv2.VideoCapture(input_path)

    # Creating output folder
    if(not os.path.isdir("output")):
        os.mkdir("output")

    # Counting frames
    counter = 1

    # First option: we want to save the images every 100 frames
    if reference_every_100_frames:
        while True:
            ret, frame = cap.read()

            if ret == True:
                if counter%100 == 0:
                    cv2.imwrite("output/frame%d.jpg" % counter, frame)
                    frame = change_frame(frame, pixel_from, pixel_to, pixel_middle)
                    cv2.imwrite("output/frame%dnew.jpg" % counter, frame)
                counter += 1
            else:
                break

    # Second option: we want only the video output
    else:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        out = cv2.VideoWriter('output/video_output.avi',fourcc, fps, dimensions)
        if with_audio:
            player = MediaPlayer(input_path)

        while True:

            # Grabbing the image
            ret, frame = cap.read()

            # Grabbing the sound
            if with_audio:
                audio_frame, val = player.get_frame()

            if ret == True:
                    frame = change_frame(frame, pixel_from, pixel_to, pixel_middle)

                    if with_audio:
                        if val != 'eof' and audio_frame is not None:
                            #audio
                            img, t = audio_frame

                    out.write(frame)

            else:
                out.release()
                break

    # Statistics
    t_end = process_time()
    time_in_s = t_end-t_start
    print("Processed in " + str(time_in_s / 60) + " min.")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


def change_frame(frame, pixel_from, pixel_to, pixel_middle):

    # we start at top left and do line by line
    for x in range(pixel_from[0], pixel_to[0]):
        for y in range(pixel_from[1], pixel_to[1]):

            # if we are higher than middle, we take the one that is one higher
            if (is_higher_than((x, y), pixel_middle)):
                frame[y][x] = frame[y-1][x]

            # if we are lefter than middle, we take one from the left
            elif (is_lefter_than((x, y), pixel_middle)):
                frame[y][x] = frame[y][x-1]

            # if we are righter than middle, we take one from the right 
            elif (is_righter_than((x, y), pixel_middle)):
                frame[y][x] = frame[y][pixel_to[0]]

            # if we are lower than middle, we take on from the bottom
            elif (is_lefter_than((x, y), pixel_middle)):
                frame[y][x] = frame[pixel_to[1]][x]

            # if we are same, we take the bottom right
            elif (is_same((x, y), pixel_middle)):
                frame[y][x] = frame[pixel_to[1]][pixel_to[0]]
    return frame


def is_same(pixel, pixel_compare):
    if (pixel[0] == pixel_compare[0] and pixel[1] == pixel_compare[1]):
        return True
    else:
        return False

def is_righter_than(pixel, pixel_compare):
    if pixel[0] > pixel_compare[0]:
        return True
    else:
        return False

def is_lefter_than(pixel, pixel_compare):
    if pixel[0] < pixel_compare[0]:
        return True
    else:
        return False

def is_lower_than(pixel, pixel_compare):
    if pixel[1] > pixel_compare[1]:
        return True
    else:
        return False

def is_higher_than(pixel, pixel_compare):
    if pixel[1] < pixel_compare[1]:
        return True
    else:
        return False
                
if __name__ == "__main__":
   main()