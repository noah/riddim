
import subprocess
flac_cmd = "/usr/bin/flac --silent --decode %s --stdout" % "clementine.flac"
#print flac_cmd
flac = subprocess.Popen(flac_cmd, stdout=subprocess.PIPE, shell=True)

mp3_cmd = "/usr/bin/lame -V0 --silent - -"
#print mp3_cmd
lame = subprocess.Popen(mp3_cmd, stdin=flac.stdout, stdout=subprocess.PIPE, shell=True)

lame.communicate()[0].read()
