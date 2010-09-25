# -*- coding: utf-8 -*-
from lp_solve import *
import re
import sys

def kakurasu_main(args):
    input_fn = args.pop(1)

    fh = open(input_fn, 'r')
    dims = fh.readline().rstrip('\r\n')

    m = re.match('(\\d+)\*(\\d+)', dims)

    if (not m):
        raise ValueError("First line of dimensions is wrong")
    
    width = int(m.group(1))
    height = int(m.group(2))
    
    found_unknown_horiz_constraints = 0
    horiz_constraints = []
    num_known_horiz_constraints = 0
    
    for y in range(0,height):
        new_cons = fh.readline().rstrip('\r\n')
        if new_cons == '?':
            horiz_constraints.append(new_cons)
            found_unknown_horiz_constraints = 1
        else:
            horiz_constraints.append(int(new_cons))
            num_known_horiz_constraints += 1

    vert_constraints = []
    num_known_vert_constraints = 0
    line = fh.readline().rstrip('\r\n')
    
    m = re.match('Vert:\s*(.*)', line)
    if (not m):
        raise ValueError("No Very: prefix in last line.")
    
    rest = m.group(1)
    values = re.findall('(\d+|\?)', rest)

    if (len(values) != height):
        raise ValueError("Not enough values in Vert line")

    for v in values:
        if v == '?':
            if found_unknown_horiz_constraints:
                raise ValueError("Cannot have both unknown horizontal and vertical constraints.")
            vert_constraints.append('?')
        else:
            vert_constraints.append(int(v))
            num_known_vert_constraints += 1

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

    if (not ret):
        raise "Could not find a solution for this puzzle."

    sol = ret[1]
    for y in range(0,height):
        for x in range(0,width):
            print ('█' if (sol[y*height+x] != 0) else '⨯'),
        print

    return 0

if __name__ == "__main__":
    sys.exit(kakurasu_main(sys.argv))

