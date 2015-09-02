usage: fftplot.py -wave car.wav  -noplot 1
this is an algorithm to reduce the noise from speech. 
Basic idea is the have short time average as speech and long time average as noise,
caculating the ratio between noise and speech, and set gain for FFT/iFFT
it includes 1) fft/ifft 2) plot  3) algorithm