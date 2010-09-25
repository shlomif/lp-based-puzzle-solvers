from lp_solve import *
import re

def kakurasu_main(args):
    input_fn = args.pop(0)

    fh = open(input_fn, 'r')
    dims = fh.readline()

    m = re.match("(\d+)\*(\d+)"), dims)

    if (not m):
        raise ValueError("First line of dimensions is wrong")
    
    width = int(m.group(1))
    height = int(m.group(2))
    
    found_unknown_horiz_constraints = 0
    horiz_constraints = []
    
    for y in range(0,height):
        new_cons = fh.readline()
        if new_cons == '?':
            horiz_constraints.push(new_cons)
            found_unknown_horiz_constraints = 1
        else:
            horiz_constraints.push(int(new_cons))

    vert_constraints = []
    line = fh.readline()
    
    m = re.match("Vert:\s*(.*?)", line)
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
            vert_constraints.push('?')
        else:
            vert_constraints.push(int(v))

    

if __name__ == "__main__":
    sys.exit(kakurasu_main(sys.argv))

