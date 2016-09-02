#!/usr/bin/env python

# configure these settings to change projector behavior
server_mount_path = '//192.168.42.11/PiShare' # shared folder on other pi
user_name = 'pi' # shared drive login user name
user_password = 'raspberry' # shared drive login password
client_mount_path = '/mnt/pishare' # where to find the shared folder on this pi
pics_folder = '/mnt/pishare/pics' # where to find the pics to display
waittime = 2   # default time to wait between images (in seconds)
use_prime = True # Set to true to show the prime slide, false if otherwise
prime_slide = '/home/pi/photobooth/projector.png' # image to show regularly in slideshow
prime_freq = 16 # how many pics to show before showing the prime slide again
monitor_w = 800 # width in pixels of display (monitor or projector)
monitor_h = 600 # height in pixels of display (monitor or projector)
title = "SlideShow"  # caption of the window...
