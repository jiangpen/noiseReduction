import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.signal as signal
import pyaudio
import wave
import sys
import numpy as np
import math
import time
import argparse

CHUNK = 64
speechave=np.arange(CHUNK)
noiseave=np.arange(CHUNK)
ratio=np.arange(CHUNK)


def reduce_noise(fftdata):
	global speechave,noiseave, ratio, a, b, c, d 
	halfdata=fftdata
	
	fftabs = np.abs(halfdata)
	speechave=speechave*a+fftabs*b #short time ave
	noiseave=noiseave*c+ fftabs*d  #long time ave
	ratio=noiseave/speechave #noise to speech is higher, ratio should be lower
	
	#import pdb ; pdb.set_trace()
	gain=[]
	
	for item in ratio:
		newratio=1.2-item
		if(newratio>1.0):
			newratio=1.0
		if(newratio<0.23):
			newratio=0.23
		"""	
		fixratio=TOFIX(float(item), 25)
		fixratio=fixratio>>18;
		fixratio=fixratio-25
		if(fixratio<0):
			fixratio=0
		if(fixratio>=len(lookuptable)):
			fixratio=len(lookuptable)-1
		gaint=lookuptable[fixratio]
		gain.append(TOFLT(gaint, 25))
		"""
		gain.append(newratio)
		
	#print(ratio[0:3])
	#print(gain[0:3])
	fftdata=fftdata*gain
	return fftdata
	
def updatePic(i):
    global data, wbuffer , line
    stream.write(data)
    data = wf.readframes(CHUNK)

    data16=np.fromstring(data,dtype=np.int16)
    wbuffer[:CHUNK]=wbuffer[CHUNK:]
    wbuffer[CHUNK:]=data16
    wbuffer=np.reshape(wbuffer, CHUNK*2)
    wbuffer *= signal.hann(CHUNK*2, sym=0) #128
    n=len(data16)
    k=np.arange(n)
    T=n/SAMPLE_RATE
    frq=k/T
    frq=frq[range(int(n/2))]
    #import pdb ; pdb.set_trace()
    fftdata=np.fft.fft(data16)
    reduced=reduce_noise(fftdata)
    dispfft=(fftdata/n)[range(int(n/2))]
    dispfft_reduced=(reduced/n)[range(int(n/2))]
    #ifftdata=np.fft.ifft(fftdata).real
    ifftdata=np.fft.ifft(reduced).real
    data=ifftdata.astype(np.int16).tostring()
    

    line.set_data(frq,abs(dispfft)) # plotting the spectrum
    line1.set_data(frq, abs(dispfft_reduced))
    return line
	
	
	
parser = argparse.ArgumentParser()	
parser.add_argument("-noplot", help="don't show plot")
parser.add_argument("-wave", help="input wave file", required=True)
args = parser.parse_args()

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)
	


wf = wave.open(str(args.wave), 'rb')
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)
print(wf.getnchannels())
SAMPLE_RATE=wf.getframerate()
windata=np.arange(CHUNK*2)#create an array
wbuffer=np.arange(CHUNK*2)

a=math.exp(-2.2/(float(SAMPLE_RATE/CHUNK)*0.04))
b=1.0-a
c=math.exp(-2.2/(float(SAMPLE_RATE/CHUNK)*3.0))
d=1.0-c
print(str(a)+":"+str(b)+":"+str(c)+":"+":"+str(d))
Ts = 1.0/SAMPLE_RATE; # sampling interval
t = np.arange(0,1,Ts) # time vector
data16=np.fromstring(data,dtype=np.int16)


		
fig = plt.figure()
ax = plt.axes(xlim=(0, SAMPLE_RATE/2), ylim=(0, 5000))
ax.grid()
line,line1 =ax.plot([],[], [],[])
line.set_label('orignal')
line1.set_label('noise reduced')
line.set_c('r')
line1.set_c('b')
if args.noplot:
	while(True):
		updatePic(0)
		
		
ani = animation.FuncAnimation(fig, updatePic, interval=1)
plt.show()


stream.stop_stream()
stream.close()

p.terminate()



