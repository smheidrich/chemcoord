import chemcoord as cc
import pytest
import numpy as np
import os
import sys


def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_structure_path(script_path):
    test_path = os.path.join(script_path)
    while True:
        structure_path = os.path.join(test_path, 'structures')
        if os.path.exists(structure_path):
            return structure_path
        else:
            test_path = os.path.join(test_path, '..')


STRUCTURES = get_structure_path(get_script_path())

molecule = cc.Cartesian.read_xyz(os.path.join(STRUCTURES, 'MIL53_small.xyz'))


def test_bond_length():
    calculated = molecule.bond_lengths([0, 1])[0]
    expctd_res = 1.3041493563710411
    assert np.allclose(calculated, expctd_res)

    calculated = molecule.bond_lengths([[0, 1], [1, 2]])
    expct_res = np.array([1.30414936, 3.25813467])
    assert np.allclose(calculated, expct_res)


def test_fragmentate():
    fragments = molecule.fragmentate()
    assert len(fragments) == 1
    assert np.alltrue(fragments[0] == molecule)


def test_shortest_distance():
    i, j, d = molecule.shortest_distance(molecule + [0, 0, 10])
    assert (i, j) == (27, 24)
    assert np.allclose(d, 4.2537465795414988)
