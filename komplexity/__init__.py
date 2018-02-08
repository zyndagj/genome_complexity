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
from itertools import chain, imap

def main():
	fCheck = fileCheck() #class for checking parameters
	parser = argparse.ArgumentParser(description="A tool that estimates sequence complexing by counting distinct k-mers in sliding windows")
	parser.add_argument('-F', metavar='FASTA', help='Input genome', required=True, type=fCheck.indexedFasta)
	parser.add_argument('-O', metavar='BEDG', help='Output file (Default: %(default)s)', default='stdout', type=str)
	parser.add_argument('-k', metavar='INT', help='k-mer size (Default: %(default)s)', default=21, type=int)
	parser.add_argument('-w', metavar='INT', help='Window size (Default: %(default)s)', default=10000, type=int) 
	parser.add_argument('-s', metavar='INT', help='Step (slide) size (Default: %(default)s)', default=1000, type=int) 
	parser.add_argument('-P', metavar='INT', help='Number of cores to use (Default: %(default)s)', default=mp.cpu_count(), type=int) 
	#parser.add_argument('-', metavar='INT', help=' (Default: %(default)s)', default=X, type=int) 
	args = parser.parse_args()
	# Make sure step size is smaller or equal to window size
	if args.s > args.w:
		raise argparse.ArgumentValueError("Step size should be <= window size")
	# Open output file
	if args.O == 'stdout':
		OF = sys.stdout
	else:
		OF = open(args.O, 'w')
	FA = FastaFile(args.F)
	sortedChroms = sorted(FA.references)
	iterList = [genChromStarts(FA, chrom, args.w, args.s) for chrom in sortedChroms]
	# Spawn workers
	p = mp.Pool(args.P, initializer=initWorker, initargs=(args.w, args.F, args.k))
	tmpStr = ''
	writeAt = 1000
	for i, ret in enumerate(p.imap(regionWorker, chain(*iterList), 1000), start=1):
		tmpStr += ret
		if i % writeAt == 0:
			OF.write(tmpStr)
			tmpStr = ''
	OF.write(tmpStr)
	if args.O != 'stdout':
		OF.close()

def initWorker(localWindowSize, fastaFile, k):
	global FA, windowSize, kSize
	windowSize = localWindowSize
	FA = FastaFile(fastaFile)
	kSize = k

def regionWorker(args):
	chrom, start = args
	end = start+windowSize
	region = FA.fetch(chrom, start, end)
	kmerIter = (region[i:i+kSize] for i in xrange(len(region)-kSize+1))
	kmerSet = set(kmerIter)
	return "%s\t%i\t%i\t%i\n"%(chrom, start, end, len(kmerSet))

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
