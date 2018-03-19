#!/usr/bin/env python
#
###############################################################################
# Author: Greg Zynda
# Last Modified: 03/19/2018
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

import unittest, sys, komplexity
try:
	from unittest.mock import patch
except:
	from mock import patch
from os import path
from StringIO import StringIO

class TestKomplexity(unittest.TestCase):
	def setUp(self):
		self.fasta = path.join(path.dirname(__file__),'test.fasta')
	def test_1(self):
		testArgs = ['None','-F',self.fasta,'-k','3','-w','5','-s','5']
		answer1 = \
'''test1	0	5	3
test1	5	10	3
test1	10	15	3
test1	15	18	1
test2	0	5	3
test2	5	10	3
test2	10	13	1
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())
	def test_2(self):
		testArgs = ['None','-F',self.fasta,'-k','3','-w','6','-s','5']
		answer1 = \
'''test1	0	5	4
test1	5	10	4
test1	10	15	4
test1	15	18	2.50
test2	0	5	4
test2	5	10	4
test2	10	13	2.50
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())
	def test_3(self):
		testArgs = ['None','-F',self.fasta,'-k','3','-w','6','-s','5','-A','sum']
		answer1 = \
'''test1	0	5	4
test1	5	10	8
test1	10	15	8
test1	15	18	5
test2	0	5	4
test2	5	10	8
test2	10	13	5
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())
	def test_4(self):
		testArgs = ['None','-F',self.fasta,'-k','3','-w','5','-s','5','-M','duplicate']
		answer1 = \
'''test1	0	5	0
test1	5	10	0
test1	10	15	0
test1	15	18	0
test2	0	5	0
test2	5	10	0
test2	10	13	0
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())
	def test_5(self):
		testArgs = ['None','-F',self.fasta,'-k','3','-w','6','-s','5','-M','duplicate']
		answer1 = \
'''test1	0	5	0
test1	5	10	0
test1	10	15	0
test1	15	18	0
test2	0	5	0
test2	5	10	0
test2	10	13	0
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())
	def test_6(self):
		testArgs = ['None','-F',self.fasta,'-k','3','-w','6','-s','5','-A','sum','-M','duplicate']
		answer1 = \
'''test1	0	5	0
test1	5	10	0
test1	10	15	0
test1	15	18	0
test2	0	5	0
test2	5	10	0
test2	10	13	0
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())
	def test_7(self):
		testArgs = ['None','-F',self.fasta,'-k','2','-w','10','-s','10','-M','duplicate']
		answer1 = \
'''test1	0	10	1
test1	10	18	1
test2	0	10	1
test2	10	13	0
'''
		with patch('sys.argv', testArgs):
			with patch('sys.stdout', StringIO()):
				komplexity.main()
				self.assertMultiLineEqual(answer1, sys.stdout.getvalue())

if __name__ == "__main__":
	unittest.main()

#>test1
#AAGGCCTTAGCTAGGCCT
#>test2
#TTCCGGAATCGAT
#test1	18	7	18	19
#test2	13	33	13	14
