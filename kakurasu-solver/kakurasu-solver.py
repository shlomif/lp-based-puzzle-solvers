#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Shlomi Fish
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This is Shlomi Fish's open-source solver for Kakurasu distributed under the 
# MIT / X11 License ( http://en.wikipedia.org/wiki/MIT_License ).
# 
# See the README file for more information and you can play Kakurasu online
# here:
#
# http://www.brainbashers.com/kakurasu.asp
#
# (Note: I am not affiliated with brainbashers.com, except for the fact 
# that I enjoy playing games and solving riddles there.)

from lp_solve import *
import re
import sys

def print_sol(sol):
    for row in sol:
        for cell in row:
            sys.stdout.write ('█' if (cell != 0) else '⨯')
        sys.stdout.write("\n")

class Solver:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @classmethod
    def parse_input_file(cls, input_fn):
        fh = open(input_fn, 'r')
        dims = fh.readline().rstrip('\r\n')

        m = re.match('(\\d+)\*(\\d+)', dims)

        if (not m):
            raise ValueError("First line of dimensions is wrong")
        
        width = int(m.group(1))
        height = int(m.group(2))

        ret = cls(width, height)
        ret.parse_constraints_using_fh(fh)

        return ret

    def parse_constraints_using_fh(self, fh):
        found_unknown_horiz_constraints = 0
        self.horiz_constraints = []
        self.num_known_horiz_constraints = 0
        
        for y in range(0,self.height):
            new_cons = fh.readline().rstrip('\r\n')
            if new_cons == '?':
                self.horiz_constraints.append(new_cons)
                found_unknown_horiz_constraints = 1
            else:
                self.horiz_constraints.append(int(new_cons))
                self.num_known_horiz_constraints += 1

        self.vert_constraints = []
        self.num_known_vert_constraints = 0
        line = fh.readline().rstrip('\r\n')
        
        m = re.match('Vert:\s*(.*)', line)
        if (not m):
            raise ValueError("No Very: prefix in last line.")
        
        rest = m.group(1)
        values = re.findall('(\d+|\?)', rest)

        if (len(values) != self.height):
            raise ValueError("Not enough values in Vert line")

        for v in values:
            if v == '?':
                if found_unknown_horiz_constraints:
                    raise ValueError("Cannot have both unknown horizontal and vertical constraints.")
                self.vert_constraints.append('?')
            else:
                self.vert_constraints.append(int(v))
                self.num_known_vert_constraints += 1

def kakurasu_main(args):
    input_fn = args.pop(1)

    solver_obj = Solver.parse_input_file(input_fn)
    sol = solve_file(solver_obj)

    print_sol(sol)

    return 0

def solve_file(solve_obj):

    width = solve_obj.width
    height = solve_obj.height
    num_known_vert_constraints = solve_obj.num_known_vert_constraints
    num_known_horiz_constraints = solve_obj.num_known_horiz_constraints
    horiz_constraints = solve_obj.horiz_constraints
    vert_constraints = solve_obj.vert_constraints

    a_matrix = []
    f_vector = []
    b_vector = []
    e_vector = []
    lower_bounds_vector = []
    upper_bounds_vector = []
    xint_vector = []

    for m in range(0,num_known_vert_constraints+num_known_horiz_constraints):
        a_matrix.append([0] * (width*height))

    y_calc = -1
    for y in range(0,height):
        if (horiz_constraints[y] != '?'):
            y_calc += 1
        x_calc = -1
        for x in range(0,width):
            if (vert_constraints[x] != '?'):
                x_calc += 1

            f_vector.append(1)

            var_num = height * y + x
            
            if (horiz_constraints[y] != '?'):
                a_matrix[y_calc][var_num] = x+1

            if (vert_constraints[x] != '?'):
                a_matrix[num_known_horiz_constraints+x_calc][var_num] = y+1
            
            lower_bounds_vector.append(0)
            upper_bounds_vector.append(1)
            xint_vector.append(len(f_vector))

    eq = 0
    y = 0
    for h_eq in range(0,num_known_horiz_constraints):
        while (horiz_constraints[y] == '?'):
            y += 1
        b_vector.append(horiz_constraints[y])
        y += 1
        e_vector.append(0)
        eq += 1
    x = 0
    for v_eq in range(0,num_known_vert_constraints):
        while (vert_constraints[x] == '?'):
            x += 1
        b_vector.append(vert_constraints[x])
        x += 1
        e_vector.append(0)
        eq += 1
    
    ret = lp_solve(f_vector, a_matrix, b_vector, e_vector, \
            lower_bounds_vector, upper_bounds_vector, xint_vector)
   
    flat_sol = ret[1]

    if (len(flat_sol) == 0):
        raise "Could not find a solution for this puzzle."

    return [[flat_sol[y*width+x] for x in range(width)] for y in range(height)]


if __name__ == "__main__":
    sys.exit(kakurasu_main(sys.argv))

