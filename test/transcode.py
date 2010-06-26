import subprocess

fp = subprocess.Popen(["flac","--decode","--stdout","--silent",'./audio/01-outkast-hold_on_be_strong.flac'],stdout=subprocess.PIPE) 
lp = subprocess.Popen(["lame","--silent","-mj", "-q0", "--vbr-new","-V0", "-s44.1","-"],stdin=fp.stdout,stdout=subprocess.PIPE)

output = lp.communicate()[0]

L = len(output)
f = open('file.mp3','w')
f.write(output)
