#!/usr/bin/env python
# created by chris@drumminhands.com
# see instructions at http://www.drumminhands.com/2016/09/02/raspberry-pi-photo-booth-projector/
# and the photo booth instruction at http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/
# slide show based on https://github.com/bradmontgomery/pgSlideShow

import argparse
import os
import stat
import sys
import time
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
import config_projector # this is the projector config file config_projector.py

# global variables which will change during the program (do not change here)
transform_x = config_projector.monitor_w # how many pixels to scale the image width
transfrom_y = config_projector.monitor_h # how many pixels to scale the image height
offset_x = 0 # how far right of the top-left pixel to display the image
offset_y = 0 # how far down from the top-left pixel to display the image
current = 0 # which file in the list to show
num_files = 0 # how many total pics to show
file_list = []  # a list of all images being shown

def mount_pics():
    try:
        # mount the drive 
        cmd = "sudo mount -t cifs "+config_projector.server_mount_path+" "+config_projector.client_mount_path+" -o user="+config_projector.user_name+",pass="+config_projector.user_password
        os.system(cmd)
    except Exception, e:
        tb = sys.exc_info()[2]
        traceback.print_exception(e.__class__, e, tb)
        print "Error mounting shared drive"

def walktree(top, callback):
    """recursively descend the directory tree rooted at top, calling the
    callback function for each regular file. Taken from the module-stat
    example at: http://docs.python.org/lib/module-stat.html
    """
    for f in sorted(os.listdir(top)):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[stat.ST_MODE]
        if stat.S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname)
        else:
            # Unknown file type, print a message
            print 'Skipping %s' % pathname


def addtolist(file, extensions=['.jpg','.jpeg']):
    """Add a file to a global list of image files."""
    global file_list

    filename, ext = os.path.splitext(file)
    e = ext.lower()
    # Only add common image types to the list.
    if e in extensions:
        if (filename[-3:]!='-sm'): # don't use the thumbnails
            print 'Adding to list: ', file
            file_list.append(file)

            if config_projector.use_prime:
                if ((len(file_list) % (config_projector.prime_freq +1)) == 0):
                    # show prime slide at regular intervals
                    file_list.append(config_projector.prime_slide) # start with the prime slide
        else:
            print 'Skipping: ', file, ' (thumbnail image)'
    else:
        print 'Skipping: ', file, ' (NOT a supported image)'


def input(events):
    """A function to handle keyboard/mouse/device input events. """
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or
            (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()

def set_demensions(img_w, img_h):
    # set variables to properly display the image on screen

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (config_projector.monitor_w * img_h) / img_w 

    if (ratio_h < config_projector.monitor_h):
        #Use horizontal black bars
        transform_y = ratio_h
        transform_x = config_projector.monitor_w
        offset_y = (config_projector.monitor_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > config_projector.monitor_h):
        #Use vertical black bars
        transform_x = (config_projector.monitor_h * img_w) / img_h
        transform_y = config_projector.monitor_h
        offset_x = (config_projector.monitor_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        transform_x = config_projector.monitor_w
        transform_y = config_projector.monitor_h
        offset_y = offset_x = 0

    # uncomment these lines to troubleshoot screen ratios
    #print str(img_w) + " x " + str(img_h)
    #print "ratio_h: "+ str(ratio_h)
    #print "transform_x: "+ str(transform_x)
    #print "transform_y: "+ str(transform_y)
    #print "offset_y: "+ str(offset_y)
    #print "offset_x: "+ str(offset_x)

def find_pics():
    global current, num_files, file_list

    file_list = [] # clear list

    if config_projector.use_prime:
        file_list.append(config_projector.prime_slide) # start with the prime slide

    walktree(config_projector.pics_folder, addtolist)  # this may take a while...

    if len(file_list) <= 1: # note one is the prime slide, if used
        print "Sorry. No images found. Exiting."
        sys.exit(1)

    current = 0
    num_files = len(file_list)

def main():
    global file_list, current, num_files

    pygame.init()

    find_pics() # check for available images to display

    # Test for image support
    if not pygame.image.get_extended():
        print "Your Pygame isn't built with extended image support."
        print "It's likely this isn't going to work."
        sys.exit(1)

    modes = pygame.display.list_modes()
    pygame.display.set_mode(max(modes))

    screen = pygame.display.get_surface()
    pygame.display.set_caption(config_projector.title)
    pygame.display.toggle_fullscreen()
    pygame.mouse.set_visible(False) #hide the mouse cursor

    while(True):
        try:
            img = pygame.image.load(file_list[current])
            img = img.convert() 

            # clear the screen
            screen.fill( (0,0,0) )

            # set pixel dimensions based on image
            set_demensions(img.get_width(), img.get_height())

            # rescale the image to fit the current display
            img = pygame.transform.scale(img, (transform_x,transfrom_y))
            screen.blit(img,(offset_x,offset_y))
            pygame.display.flip()

            input(pygame.event.get())
            time.sleep(config_projector.waittime)
        except pygame.error as err:
            print "Failed to display %s: %s" % (file_list[current], err)

        # When we get to the end, re-start at the beginning and check for new files
        current = current + 1;
        if (current == num_files):
            print '----------------------- Restart slideshow -----------------------'
            find_pics() # check for available images to display

print 'Projector running'

print 'Waiting a bit to make sure the photo booth has time to boot.'
time.sleep(300) # wait a bit until the other RPi is connected

mount_pics() # mount the drive on startup of program

# run the main program
main()
