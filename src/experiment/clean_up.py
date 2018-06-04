from torchbearer import extinguish_path as ep
from torchbearer import light_path as lp

my_path = [("192.168.57.201", "gig 0/25"),("192.168.57.200", "gig 0/25"),
          ("192.168.57.201", "gig 0/26"),("192.168.57.200", "gig 0/26"),
          ("192.168.57.201", "gig 0/27"),("192.168.57.200", "gig 0/27")]

ep(my_path)
