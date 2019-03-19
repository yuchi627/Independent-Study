import sys
import subprocess
import os

flir_file_name = sys.argv[1]
move = os.chdir("pylepton")
delay_time = "1"
take_flir_photo = subprocess.call("./pylepton_capture " + flir_file_name, shell = True)
