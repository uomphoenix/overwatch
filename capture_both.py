#!/usr/bin/env python

#imports required for PiCamera
import picamera
import picamera.array


#imports required for Lepton
import sys
import numpy as np
import cv2
from pylepton import Lepton



def capture(flip_v = False, device = "/dev/spidev0.1"):
  with Lepton(device) as l:
    a,_ = l.capture()
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)

if __name__ == '__main__':
  from optparse import OptionParser

  usage = "usage: %prog [options] output_file[.format]"
  parser = OptionParser(usage=usage)

  parser.add_option("-f", "--flip-vertical",
                    action="store_true", dest="flip_v", default=False,
                    help="flip the output image vertically")

  parser.add_option("-d", "--device",
                    dest="device", default="/dev/spidev0.1",
                    help="specify the spi device node (might be /dev/spidev0.1 on a newer device)")

  (options, args) = parser.parse_args()

  if len(args) < 1:
    print "You must specify an output filename"
    sys.exit(1)

  thermal_image = capture(flip_v = options.flip_v, device = options.device)
  thermal_image_name = args[0] + "_thermal.jpg"
  cv2.imwrite(thermal_image_name, thermal_image)



# testing hello hi
# now we have windows lin endings



with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
	camera.capture(output, 'rgb')
	rgb_image = output.array

rgb_image_name = args[0] + "_rgb.jpg"
cv2.imwrite(rgb_image_name, rgb_image)





