#!/usr/bin/env python
#
###############################################################################
# Author: Greg Zynda
# Last Modified: 02/07/2018
###############################################################################
# BSD 3-Clause License
# 
# Copyright (c) 2018, Texas Advanced Computing Center
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

import argparse, sys, os
import multiprocessing as mp
from pysam import FastaFile
from math import ceil
from itertools import chain, imap, ifilter
import numpy as np

def main():
	fCheck = fileCheck() #class for checking parameters
	parser = argparse.ArgumentParser(description="A tool that estimates sequence complexing by counting distinct k-mers in sliding windows")
	parser.add_argument('-F', metavar='FASTA', help='Input genome', required=True, type=fCheck.indexedFasta)
	parser.add_argument('-O', metavar='BEDG', help='Output file (Default: %(default)s)', default='stdout', type=str)
	parser.add_argument('-k', metavar='INT', help='k-mer size (Default: %(default)s)', default=21, type=int)
	parser.add_argument('-w', metavar='INT', help='Window size (Default: %(default)s)', default=10000, type=int) 
	parser.add_argument('-s', metavar='INT', help='Step (slide) size (Default: %(default)s)', default=1000, type=int) 
	parser.add_argument('-P', metavar='INT', help='Number of cores to use (Default: %(default)s)', default=mp.cpu_count(), type=int) 
	parser.add_argument('-A', metavar='STR', help='Aggregation method ([mean], median, sum, min, max)', default="mean", type=str)
	parser.add_argument('-N', help="Allow N's in k-mers", action="store_true")
	#parser.add_argument('-', metavar='INT', help=' (Default: %(default)s)', default=X, type=int) 
	args = parser.parse_args()
	# Verify agg choice
	aggChoices = {"mean":np.mean,"median":np.median,"sum":sum,"min":min,"max":max}
	if args.A not in aggChoices:
		raise argparse.ArgumentValueError("-A must be mean, median, sum, min, or max")
	aggFunc = aggChoices[args.A]
	# Make sure step size is smaller or equal to window size
	if args.s > args.w:
		raise argparse.ArgumentValueError("Step size should be <= window size")
	# Open output file
	if args.O == 'stdout':
		OF = sys.stdout
	else:
		OF = open(args.O, 'w', 100000)
	FA = FastaFile(args.F)
	sortedChroms = sorted(FA.references)
	iterList = [genChromStarts(FA, chrom, args.w, args.s) for chrom in sortedChroms]
	# Spawn workers
	p = mp.Pool(args.P, initializer=initWorker, initargs=(args.w, args.F, args.k, args.N))
	#tmpStr = ''
	#writeAt = 1000
	#at = 0
	intervalList = []
	bI = bedgraphInterval(args.s, aggFunc)
	for ret in p.imap(regionWorker, chain(*iterList), 1000):
		for outStr in bI.add(*ret):
			OF.write(outStr)
			#at += 1
			#tmpStr += outStr
			#if at % writeAt == 0:
			#	OF.write(tmpStr)
			#	tmpStr = ''
	for outStr in bI.end():
		OF.write(outStr)
		#tmpStr += outStr
	#OF.write(tmpStr)
	if args.O != 'stdout':
		OF.close()
	p.close()
	p.join()

class bedgraphInterval:
	def __init__(self, stepSize, aggFunc=np.mean):
		self.stepSize = stepSize
		self.IList = []
		self.lastStart = 0
		self.lastEnd = 0
		self.chrom = ""
		self.aggFunc = aggFunc
	def add(self, chrom, start, end, value):
		# New chrom
		if chrom != self.chrom:
			for i in self.end(): yield i
		# Add new interval
		self.IList.append((start, end, value))
		if not self.lastStart:
			self.lastStart = start
		else:
			self.lastStart = self.lastEnd
		if self.chrom != chrom:
			self.chrom=chrom
		# Print latest interval
		self.lastEnd = min(self.IList[-1][1], self.lastStart + self.stepSize)
		yield self.printInterval(self.lastStart, self.lastEnd)
		# Pop old interval
		self.remove(self.lastStart, self.lastEnd)
	def printInterval(self, start, end):
		outList = []
		for item in self.IList:
			if item[0] < end and start < item[1]:
				outList.append(item[2])
		aggVal = self.aggFunc(outList)
		return "%s\t%i\t%i\t%i\n"%(self.chrom, start, end, aggVal)
	def remove(self, start, end):
		newList = []
		for item in self.IList:
			if item[1] > end:
				newList.append(item)
		self.IList = newList
	def end(self):
		if not self.IList:
			self.chrom = ""
			self.lastStart = 0
			self.lastEnd = 0
			return
		for start in xrange(self.lastEnd, self.IList[-1][1], self.stepSize):
			end = min(self.IList[-1][1], start+self.stepSize)
			yield self.printInterval(start, end)
			self.remove(start, end)
		self.IList = []
		self.chrom = ""
		self.lastStart = 0
		self.lastEnd = 0

def initWorker(localWindowSize, fastaFile, k, N):
	global FA, windowSize, kSize, useN
	windowSize = localWindowSize
	FA = FastaFile(fastaFile)
	kSize = k
	useN = N

def regionWorker(args):
	chrom, start = args
	end = start+windowSize
	region = FA.fetch(chrom, start, end)
	if useN:
		kmerIter = (region[i:i+kSize] for i in xrange(len(region)-kSize+1))
	else:
		kmerIter = ifilter(lambda x: 'N' not in x, (region[i:i+kSize] for i in xrange(len(region)-kSize+1)))
	kmerSet = set(kmerIter)
	return (chrom, start, end, len(kmerSet))
	#return "%s\t%i\t%i\t%i\n"%(chrom, start, end, len(kmerSet))

def genChromStarts(FA, chrom, windowSize, stepSize):	
	length = FA.get_reference_length(chrom)
	nWindows = (length-windowSize)/float(stepSize)
	nFullWindows = int(ceil(nWindows))
	wrap = ((chrom, length-windowSize),)
	fullStarts = imap(lambda x: (chrom, x*stepSize), xrange(nFullWindows))
	return chain(fullStarts, wrap)

class fileCheck:
	def check(self, file, exts):
		ext = os.path.splitext(file)[1][1:]
		fName = os.path.split(file)[1]
		if not ext in exts:
			raise argparse.ArgumentTypeError("%s not a %s"%(fName, exts[0]))
		if not os.path.exists(file):
			raise argparse.ArgumentTypeError("%s does not exist"%(file))
	def fastq(self, file):
		self.check(file, ['fastq','fq'])
		return file
	def fasta(self, file):
		self.check(file, ['fasta','fa'])
		return file
	def indexedFasta(self, file):
		self.check(file, ['fasta','fa'])
		self.check(file+'.fai', ['fai'])
		return file

if __name__ == "__main__":
	main()
