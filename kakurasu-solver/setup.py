from distutils.core import setup

dist_name = 'kakurasu-solver'

setup(
    name=dist_name,
    version='0.2.0',
    description='Solver for the Kakurasu Riddle Game',
    author='Shlomi Fish',
    author_email='shlomif@cpan.org',
    url='http://www.shlomifish.org/open-source/projects/nikoli-solvers/kakurasu/',

    py_modules=[dist_name],
)
