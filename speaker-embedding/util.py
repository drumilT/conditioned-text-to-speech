import numpy as np
import torch
from visdom import Visdom
import os
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as pyplot

class Hyperparameters():
	"""
	Empty class that can hold the hyperparameters
	"""
	def __init__(self):
		pass

class VisdomLinePlotter(object):
	"""Plots to Visdom"""

	def __init__(self, env_name='main'):
		self.viz = Visdom()
		self.env = env_name
		self.plots = {}
		
	def plot(self, var_name, split_name, title_name, x, y):
		if var_name not in self.plots:
			self.plots[var_name] = self.viz.line(X=np.array([x,x]), Y=np.array([y,y]), env=self.env, opts=dict(
				legend=[split_name],
				title=title_name,
				xlabel='Epochs',
				ylabel=var_name
			))
		else:
			self.viz.line(X=np.array([x]), Y=np.array([y]), env=self.env, win=self.plots[var_name], name=split_name, update = 'append')

def get_device(cuda=True):
	"""
	returns the device used in the system (cpu/cuda)
	"""
	device = torch.device("cuda" if torch.cuda.is_available() and cuda == 1 else "cpu")
	print("Using Device : " + str(device))
	return device

def quantize_waveform(waveform, quantiles=256, non_linear=True):
	"""
	Used to quantize the waveform to 256 (default) values.
	Returns the quantized values as well as indices.

	Data Type hardcoded to int16 for now.

	Input waveform : [-2^x,2^x-1]
	Output waveform : [-1,1)
	Indices : [0,quantiles-1]
	"""

	bits = 16 # hardcoded number of bits

	# normalize for [-1 to 1)
	waveform = waveform/2**(bits-1)

	# use the non-linear mapping from the paper
	if non_linear is True:
		waveform = np.sign(waveform)*(np.log(1+(quantiles-1)*abs(waveform))/np.log(quantiles)) # range: [-1 to 1)
	else:
		waveform = np.array(waveform)

	# get the indices
	indices = (1+waveform)/2 # range: [0 to 1)
	indices = (indices*quantiles).astype('int') # range: [0 to 255]

	# get the waveform from the indices
	waveform = 2*(indices.astype('float')/quantiles) - 1

	return waveform, indices

def normalize2denormalize(waveform):
	"""
	Used to denormalize a waveform from [-1 to 1) to int16 values.
	The data can be saved without denormalizing as well, though.
	So it is not required so far.
	"""

	bits = 16 # hardcoded number of bits
	waveform = (waveform*(2**(bits-1))).astype('int')

	return waveform

def index2normalize(indices, quantiles=256):
	"""
	converts a sequence of indices to corresponding values in [-1 to 1)
	"""
	waveform = indices/float(quantiles) # [0 to 1)
	waveform = (waveform*2)-1 # [-1 to 1)

	return waveform

def index2oneHot(indices, quantiles):
	"""
	Used to convert an array of indices to one-hot form.
	indices: array of length n
	output: np array of shape quantiles x n
	"""
	onehot = np.zeros((indices.size, quantiles))
	onehot[np.arange(indices.size), indices] = 1
	return onehot.transpose()

def save_model(model, filename=None):
	"""
	Used to save the model into a file.
	"""
	folder = "saved_models"
	if folder not in os.listdir():
		os.mkdir(folder)
	folder = folder+"/"

	if filename is None:
		while True:
			files = os.listdir(folder)
			filename = input("Enter filename [model]: ")
			if filename in files:
				response = input("Warning! File already exists. Override? [y/n] : ")
				if response.strip() in ("Y", "y"):
					break
				continue
			break

	torch.save(model, folder+filename)

def save_audio(data, rate, filename=None):
	"""
	Used to save the audio into a file.
	"""
	folder = "audio_samples"
	if folder not in os.listdir():
		os.mkdir(folder)
	folder = folder+"/"

	if filename is None:
		while True:
			files = os.listdir(folder)
			filename = input("Enter filename [audio]: ")
			if filename in files:
				response = input("Warning! File already exists. Override? [y/n] : ")
				if response.strip() in ("Y", "y"):
					break
				continue
			break

	wavfile.write(folder+filename, rate, data)

def visualize_waveform(waveform=None, wavefile=None):
	"""
	Used to display waveform from a file or from an array.
	Exactly one of the two args should be not None.
	"""

	# read waveform from file if needed
	if wavefile is not None:
		_, waveform = wavfile.read(wavefile)

	# plot the waveform using pyplot
	pyplot.plot(range(len(waveform)), waveform)
	pyplot.show()	


