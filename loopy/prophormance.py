from __future__ import division 
from __future__ import absolute_import 
import six 

__copyright__ = "Copyright (C) 2012 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np
from islpy import dim_type
import loopy as lp
import pyopencl as cl
import pyopencl.array
from pymbolic.mapper.flop_counter import FlopCounter

class ExpressionFlopCounter(FlopCounter):

	def map_reduction(self, expr):
		from warnings import warn
		warn("ExpressionFlopCounter counting reduction expression as 0 flops.", stacklevel=2)
		return 0

	def map_subscript(self, expr):
		return self.rec(expr.index)

	def map_tagged_variable(self, expr):
		return 0
'''
	def map_leaf(self, expr):
		return 0

	def map_wildccard(self, expr):
		return 0

	def map_function_symbol(self, expr):
		return 0

	def map_call(self, expr):
		return 0

	def map_call_with_kwargs(self, expr):
		return 0

	def map_lookup(self, expr):
		return 0
'''


class PerformanceForecaster:

	# count the number of flops in the kernel
	# param_vals is a dictionary mapping parameters to values
	def kernel_flop_count(self, knl, param_vals):
		poly = self.kernel_flop_poly(knl)
		return poly.eval_with_dict(param_vals)

	def kernel_flop_poly(self, knl):
		poly = 0
		flopCounter = ExpressionFlopCounter()
		for insn in knl.instructions:
			# how many times is this instruction executed?
			# check domain size:
			insn_inames = knl.insn_inames(insn)
			inames_domain = knl.get_inames_domain(knl.insn_inames(insn))
			domain = (inames_domain.project_out_except(insn_inames, [dim_type.set]))
			flops = flopCounter(insn.expression())
			poly += flops*domain.card()
		return poly

