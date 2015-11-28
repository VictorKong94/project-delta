"""
Tests creation of test data in make_test_data.py

Run with:
    nosetests test_make_test_data.py
"""
from __future__ import absolute_import, division, print_function
from .. import make_test_data
import nibabel as nib
import numpy as np
import os

def test_make_test_data():
    # Paths to directories that should contain the test subject's data
    path_data = "../../data/ds005/subtest/"
    path_BOLD = path_data + "BOLD/task001_runtest/bold.nii.gz"
    path_behav = path_data + "behav/task001_runtest/behavdata.txt"

    # Test existance of test data files
    assert os.path.isfile(path_BOLD)
    assert os.path.isfile(path_behav)

    # Test BOLD data
    img = nib.load(path_BOLD)
    assert img.affine == np.eyes(4)
    data = img.get_data()
    assert data.shape == (3, 3, 3, 3)
    assert [data.min(), data.max(), data.mean()] == [0, 11, 3.0]
    assert (data[..., 2] - dat[..., 1] ==  data[..., 1] - data[..., 0]).all()

    # Test behavioral data
    behav = open(path_behav).readlines()
    assert len(behav) == 4
    assert [len(row) for row in behav] == [41, 27, 27, 26]
    assert row[0] == "onset\tgain\tloss\tPTval\trespnum\trespcat\tRT\n"
    assert row[1] == "0.00\t10\t20\t-9.80\t4\t0\t1.077\n"
    assert row[2] == "2.00\t20\t20\t0.20\t0\t-1\t0.000\n"
    assert row[3] == "4.00\t30\t20\t10.20\t2\t1\t1.328"