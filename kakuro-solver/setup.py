from distutils.core import setup

dist_name = 'kakuro_solver'

setup(
    name=dist_name,
    version='0.0.1',
    description='Solver for the Kakuro (Cross Sums) Riddle Game',
    author='Shlomi Fish',
    author_email='shlomif@cpan.org',
    url='http://www.shlomifish.org/open-source/projects/nikoli-solvers/kakuro/',

    py_modules=[dist_name],
    requires = ['lp_solve'],
)
