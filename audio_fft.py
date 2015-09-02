import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.signal as signal
import pyaudio
import wave
import sys
import numpy as np
import math

def TOFLT(value, qnum):
	return float(value)/(float(1<<qnum))
	
def TOFIX(value, qnum):
	fq=float(value)* float(1<<qnum)
	return int(fq)
	
print(TOFIX(0.2, 25))

CHUNK = 64

#speechave=speachave*a+ current*b,   a=0.1, b=0.9, updating fast
#noiseave=speachave*c+ current*d,    c=0.8  d=0.2, updating slow
#ratio=noiseave/speachave
#set gainset according to ratio higher, gain lower. radio lower, gain higher

speechave=np.arange(CHUNK)
noiseave=np.arange(CHUNK)
ratio=np.arange(CHUNK)
SAMPLE_RATE=44100

a=math.exp(-2.2/float(SAMPLE_RATE/64)*0.04)
b=1-a
c=math.exp(-2.2/float(SAMPLE_RATE/64)*3.0)
d=1-c
print(str(a)+":"+str(b)+":"+str(c)+":"+":"+str(d))

lookuptable=[]
for item in range(0, 128):
	lookuptable.append(TOFIX(math.exp(-1*item*0.01), 25) )
	
def sens(fftdata):
	global speechave,noiseave, ratio, a, b, c, d ,lookuptable
	halfdata=fftdata
	
	fftabs = np.abs(halfdata)
	speechave=speechave*a+fftabs*b
	noiseave=noiseave*c+ fftabs*d
	ratio=noiseave/speechave #noise to speech is higher, ratio should be lower
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

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
passthrough=False
if len(sys.argv) ==3:
	passthrough=True

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



while data != '':
    stream.write(data)
    data = wf.readframes(CHUNK)

    data16=np.fromstring(data,dtype=np.int16)
    wbuffer[:CHUNK]=wbuffer[CHUNK:]
    wbuffer[CHUNK:]=data16
    wbuffer=np.reshape(wbuffer, CHUNK*2)
    wbuffer *= signal.hann(CHUNK*2, sym=0) #128
    
    fftdata=np.fft.fft(data16)
    if not passthrough:
	    fftdata=sens(fftdata)
    ifftdata=np.fft.ifft(fftdata).real
    data=ifftdata.astype(np.int16).tostring()


stream.stop_stream()
stream.close()

p.terminate()
