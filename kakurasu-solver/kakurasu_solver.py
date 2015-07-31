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

'''
This is Shlomi Fish's open-source solver for Kakurasu distributed under the
MIT / X11 License ( http://en.wikipedia.org/wiki/MIT_License ).

See the README file for more information and you can play Kakurasu online
here:

http://www.brainbashers.com/kakurasu.asp

(Note: I am not affiliated with brainbashers.com, except for the fact
that I enjoy playing games and solving riddles there.)

------

The algorithm is not too complicated on our side of the fence - it just became
a bit hairy because we need to construct input that lp_solve will like.

If you look at a http://brainbashers.com/kakurasu.asp riddle, you'll see that
you need to mark the cells of a two-dimensional grid as true/false so that the
sums will match. So we define Height*Width boolean variables and up to
Height+Width integral linear equations with these boolean variables to
determine the value of the boolean variables. Then we pass them to lp_solve
to do its magic.
'''

from lp_solve import *
import re
import sys

class Params(object):
    '''
    Class for the parameters of the lp_solve module. See the documentation of
    lp_solve for what they represent.
    '''

    def _process_constraints(self, constraints):
        '''
        Populate b_vector and e_vector with the constraints, that could
        be the vertical or the horizontal ones.
        '''
        idx = 0
        while idx < len(constraints):
            while (constraints[idx] == '?'):
                idx += 1
            self.b_vector.append(constraints[idx])
            idx += 1
            self.e_vector.append(0)

    def __init__(self, width, height,
            num_known_vert_constraints, num_known_horiz_constraints,
            horiz_constraints, vert_constraints):

        self.a_matrix = []
        self.f_vector = []
        self.b_vector = []
        self.e_vector = []
        self.lower_bounds_vector = []
        self.upper_bounds_vector = []
        self.xint_vector = []

        for m in range(0,num_known_vert_constraints+num_known_horiz_constraints):
            self.a_matrix.append([0] * (width*height))

        y_calc = -1
        for y in range(0,height):
            if (horiz_constraints[y] != '?'):
                y_calc += 1
            x_calc = -1
            for x in range(0,width):
                if (vert_constraints[x] != '?'):
                    x_calc += 1

                self.f_vector.append(1)

                var_num = height * y + x

                if (horiz_constraints[y] != '?'):
                    self.a_matrix[y_calc][var_num] = x+1

                if (vert_constraints[x] != '?'):
                    self.a_matrix[num_known_horiz_constraints+x_calc][var_num] \
                            = y+1

                self.lower_bounds_vector.append(0)
                self.upper_bounds_vector.append(1)
                self.xint_vector.append(len(self.f_vector))

        for constraints in [horiz_constraints, vert_constraints]:
            self._process_constraints(constraints)

class Solver(object):
    '''This class is used to parse the input files, process the data into
    a format that lp_solve can understand and call lp_solve on it.'''
    def __init__(self, width, height):
        '''Constructor - assign width and height'''
        self.width = width
        self.height = height

    @classmethod
    def parse_input_file(cls, input_fn):
        '''
        Parse the input file and create and return a solver instance.
        '''
        fh = open(input_fn, 'r')
        dims = fh.readline().rstrip('\r\n')

        m = re.match('(\\d+)\*(\\d+)', dims)

        if (not m):
            raise ValueError("First line of dimensions is wrong")

        width = int(m.group(1))
        height = int(m.group(2))

        ret = cls(width, height)
        ret._parse_constraints_using_fh(fh)

        return ret

    def _parse_constraints_using_fh(self, fh):
        '''
        Parse the constraints using the filehandle (after the width and height
        were parsed). This function populates the following fields:

        self.horiz_contraints - the horizontal constraints
        self.num_known_horiz_constraints - the number of known/defined horizontal
            contraints.
        self.vert_constraints - the vertical_constraints.
        self.num_known_vert_constraints - the number of known/defined vertical
            constaints.

        All constraints are either an integer or the string '?' if they are not
        known. The user can fill them himself programatically without calling this
        method.
        '''
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

    def _calc_params_obj(self):
        '''
        Calculate the Params object that should be passed to the lp_solve module.
        This fills in the parameters of the equations needed to solve the puzzle.
        '''

        return Params(
                width=self.width,
                height=self.height,
                num_known_vert_constraints=self.num_known_vert_constraints,
                num_known_horiz_constraints=self.num_known_horiz_constraints,
                horiz_constraints = self.horiz_constraints,
                vert_constraints = self.vert_constraints
        )

    def solve(self):
        '''
        Attempts to solve the game.

        This should be called after self.width , self.height ,
        self.num_known_horiz_constraints , self.num_known_vert_constraints ,
        self.horiz_constraints and self.vert_constraints were filled in.

        Returns a two-dimensional array containing the rows of the boolean
        values with the solution.
        '''

        lp_solve_params = self._calc_params_obj()

        lp_solve_ret = lp_solve(
                lp_solve_params.f_vector,
                lp_solve_params.a_matrix,
                lp_solve_params.b_vector,
                lp_solve_params.e_vector,
                lp_solve_params.lower_bounds_vector,
                lp_solve_params.upper_bounds_vector,
                lp_solve_params.xint_vector
        )

        flat_sol = lp_solve_ret[1]

        if (len(flat_sol) == 0):
            raise "Could not find a solution for this puzzle."

        width  = self.width
        height = self.height

        return \
        [
            [flat_sol[y*width+x] for x in range(width)]
            for y in range(height)
        ]

def _cell_as_text(cell):
    '''Return a textual representation of a cell in pretty Unicode.'''
    if cell != 0:
        return '█'
    else:
        return '⨯'

def print_sol_to_screen_as_unicode(sol):
    '''Prints the solution to the screen using Unicode characters.'''
    for row in sol:
        print "".join(map(_cell_as_text, row))

def kakurasu_main(args):
    '''The main() function of the command-line app'''
    input_fn = args.pop(1)

    solver_obj = Solver.parse_input_file(input_fn)
    sol = solver_obj.solve()

    print_sol_to_screen_as_unicode(sol)

    return 0


if __name__ == "__main__":
    sys.exit(kakurasu_main(sys.argv))

