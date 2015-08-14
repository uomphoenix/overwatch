#imports required for Lepton
import numpy as np
import cv2
from pylepton import Lepton


#imports required for Firefly
import socket
import time
import math
import sys
from firefly import authentication



#define a capture method/fucntion for the lepton module
def capture(flip_v = False, device = "/dev/spidev0.1"):
    with Lepton(device) as l:
        a,_ = l.capture()
        if flip_v:
            cv2.flip(a,0,a)
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        return np.uint8(a)
  
  








server_address = ('192.168.101.129', 56789)

#perform simple authentication
auth = authentication.SimpleAuthenticationClient(server_address, "TEST_STREAM")

auth.authenticate()


#open UDP socket and connect to the address of "receiver"
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

c.connect(auth.receiver_address)


# This should NEVER be bigger than 8192
MAX_PACKET_SIZE = 4096

"""<challenge>\x00<seq num>\x00<max fragments>\x00<fragment num>\x00<frame>\x00"""

frames_sent = 0

while True:

    thermal_image = capture(flip_v = options.flip_v, device = options.device)
    
    ret, thermal_frame = cv2.imencode('.jpg', thermal_image)
    
    thermal_bytes = thermal_frame.tobytes()
    
    frame_len = len(thermal_bytes)

    if frame_len > MAX_PACKET_SIZE:
        # need to split the frame into fragments
        num_fragments = int(math.ceil(1.0*frame_len/MAX_PACKET_SIZE))
        print "Splitting frame into %d fragments" % num_fragments

        fragment_len_sent = 0
        curr_index = 0
        end_index = MAX_PACKET_SIZE
        for i in range(num_fragments):
            if end_index > frame_len:
                end_index = frame_len

            print "Frame %s indexing range: %s to %s, fragment: %d" % (
                    frames_sent, curr_index, end_index, i
                )

            fragment = frame[curr_index:end_index]
            print "length of fragment: %s" % len(fragment)

            to_send = "%s\x00%s\x00%s\x00%s\x00%s\x00" % (
                auth.token, frames_sent, num_fragments, i, fragment
            )

            #print "Sending %s to %s" % (repr(to_send), auth.receiver_address)
            c.send(to_send)

            fragment_len_sent += len(fragment)

            curr_index = end_index
            end_index += MAX_PACKET_SIZE

        print "length sent: %s, frame len: %s" % (fragment_len_sent, frame_len)

    else:
        to_send = "%s\x00%s\x00%s\x00%s\x00%s\x00" % (auth.token, frames_sent, 1, 1, frame)

        #print "Sending %s to %s" % (repr(to_send), auth.receiver_address)
        c.send(to_send)

    frames_sent += 1


print "Frames sent: " + str(frames_sent)

c.close()


