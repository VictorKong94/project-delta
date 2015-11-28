"""
Tests class `run` functionality in make_class.py

Run with:
    nosetests test_make_class.py
"""
from __future__ import absolute_import, division, print_function
from nose.tools import assert_almost_equal
from numpy.testing import assert_array_equal
from .. import make_class
import numpy as np
import os

def test_make_class():
    # Test argument `rm_nonresp` functionality
    subtest_runtest1 = make_class.run("test1", "001", time_correct=True)
    subtest_runtest2 = make_class.run("test1", "001", rm_nonresp=False)

    # Test attribute .data
    assert_array_equal(subtest_runtest1.data, subtest_runtest2.data)
    data = subtest_runtest1.data
    assert data.shape == (3, 3, 3, 3)
    assert [data.min(), data.max(), data.mean()] == [0, 11, 3.0]
    assert_array_equal(data[..., 2] - data[..., 1], data[..., 1] - data[..., 0])

    # Test attribute .affine
    assert_array_equal(subtest_runtest1.affine, np.eye(4))
    assert_array_equal(subtest_runtest2.affine, np.eye(4))

    # Test attribute .behav
    behav1, behav2 = subtest_runtest1.behav, subtest_runtest2.behav
    assert [behav1.shape, behav2.shape] == [(2, 6), (3, 6)]
    assert [behav1.min(), behav1.max(), behav1[:, :5].sum()] == [0, 30, 89]
    assert [behav2.min(), behav2.max(), behav2[:, :5].sum()] == [-1, 30, 132]

    # Test method .design_matrix()
    design_matrix1 = subtest_runtest1.design_matrix(resp_time=True)
    design_matrix2 = subtest_runtest2.design_matrix(euclidean_dist=False)
    assert [design_matrix1.shape, design_matrix2.shape] == [(2, 5), (3, 3)]
    assert_almost_equal(design_matrix1[0, 4] ** 2, 112.5)
    assert_almost_equal(design_matrix1[1, 4] ** 2, 12.5)
    assert design_matrix2.sum() == 123.0

    # Test method .smooth()
    smooth1, smooth2 = subtest_runtest1.smooth(0), subtest_runtest1.smooth(1, 5)
    smooth3 = subtest_runtest1.smooth(2, 0.25)
    assert [smooth1.max(), smooth1.shape, smooth1.sum()] == [0, (3, 3, 3), 0]
    assert [smooth2.max(), smooth2.shape, smooth2.sum()] == [1, (3, 3, 3), 27]
    assert [smooth3.max(), smooth3.shape, smooth3.sum()] == [8, (3, 3, 3), 108]
    assert [smooth1.std(), smooth2.std()] == [0, 0]
    assert_almost_equal(smooth3.std(), 1.6329931618554521)

    # Test method .time_course()
    time_course1 = subtest_runtest1.time_course("gain", 0.2)
    time_course2 = subtest_runtest1.time_course("loss", 0.25)
    assert [time_course1.shape, time_course1.sum()] == [(1200,), 200]
    assert [time_course2.shape, time_course2.sum()] == [(960,), 160]