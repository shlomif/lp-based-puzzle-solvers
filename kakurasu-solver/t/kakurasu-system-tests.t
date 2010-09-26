#!/usr/bin/perl

use strict;
use warnings;

use Test::More tests => 1;

use Test::Differences;

use IO::All;

{
    my $got = `python kakurasu-solver.py layouts/brainbashers-4x4-medium-2010-09-25.kakurasu.board`;
    my $expected = io->file('t/data/expected/brainbashers-4x4-medium-2010-09-25.kakurasu.expected')->slurp();

    # TEST
    eq_or_diff( $got, $expected, "4x4-medium-2010-09-25");
}
