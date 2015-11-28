""" Script to run diagnostic analysis on FMRI run

Parts:
-----
I. Identify outliers
II. General Linear Model
III. Locate activated region
IV. Plots
"""

from __future__ import division, print_function, absolute_import
import matplotlib.pyplot as plt
import nibabel as nib
import numpy.linalg as npl
import sys
sys.path.append(".././utils")
from make_class import *
from utils_functions import *
from hypothesis import *
sys.path.append(".././model")
from diagnostics import *

"""
* Create an object from run class
* Drop the first four volumes, as we know these are outliers
"""
sub = run("001","001")
data = sub.data
data = data[...,4:]

"""
================================== PART I =======================================

Use your vol_std function to get the volume standard deviation values for the
remaining 236 volumes.
"""
vol_std_values = vol_std(data)
np.savetxt('vol_std_values.txt', vol_std_values)

"""
Use the iqr_outlier detection routine to get indices of outlier volumes.
"""
outlier_indices, lo_hi_thresh = iqr_outliers(vol_std_values)
np.savetxt('vol_std_outliers.txt', outlier_indices)

"""
Plot following
* The volume standard deviation values;
* The outlier points from the std values, marked on the plot with an 'o'
  marker;
* A horizontal dashed line at the lower IRQ threshold;
* A horizontal dashed line at the higher IRQ threshold;
"""
plt.plot(vol_std_values, c="b")
outlier = plt.scatter(outlier_indices, vol_std_values[outlier_indices],c="r")
lower_thres = plt.axhline(lo_hi_thresh[0], color="c",ls="--")
higher_thres = plt.axhline(lo_hi_thresh[1], color="g",ls="--")
plt.title("Volume Standard Deviation")
plt.xlabel('Volume Index')
plt.ylabel('Standard Deviation')
plt.xlim(0, 240)
plt.ylim(np.floor(min(vol_std_values)), np.ceil(max(vol_std_values)))
plt.legend((outlier, lower_thres, higher_thres),
			('Outliers', 'Lower IRQ threshold', 'Higher IRQ threshold'),
			loc=0)
plt.savefig('vol_std.png')
plt.close()

"""On the same plot, plot the following:
* The RMS vector;
* The identified outlier points marked with an `o` marker;
* A horizontal dashed line at the lower IRQ threshold;
* A horizontal dashed line at the higher IRQ threshold;"""

rmsd = vol_rms_diff(data)
rmsd_outlier_id, rmsd_thresh = iqr_outliers(rmsd)
plt.plot(rmsd, c="b")
rmsd_outlier = plt.scatter(rmsd_outlier_id, rmsd[rmsd_outlier_id],c="r")
lower_rmsd_thres = plt.axhline(rmsd_thresh[0], color="c",ls="--")
higher_rmsd_thres = plt.axhline(rmsd_thresh[1], color="g",ls="--")
plt.title("RMS Difference")
plt.xlabel('Difference Index')
plt.ylabel('rmsd')
plt.xlim(0, 240)
plt.legend((rmsd_outlier, lower_rmsd_thres, higher_rmsd_thres),
			('Outliers', 'Lower IRQ threshold', 'Higher IRQ threshold'),
			loc=0)
plt.savefig('vol_rms_outliers.png')
plt.close()


"""On the same plot, plot the following:
* The RMS vector with a 0 appended to make it have length the same as the
  number of volumes in the image data array;
* The identified outliers shown with an `o` marker;
* A horizontal dashed line at the lower IRQ threshold;
* A horizontal dashed line at the higher IRQ threshold;
"""
edo_index = extend_diff_outliers(rmsd_outlier_id)
extend_rmsd = np.append(rmsd, 0)

plt.plot(extend_rmsd, c="b")
extend_rmsd_outlier = plt.scatter(edo_index, extend_rmsd[edo_index],c="r")
extend_lower_rmsd_thres = plt.axhline(rmsd_thresh[0], color="c",ls="--")
extend_higher_rmsd_thres = plt.axhline(rmsd_thresh[1], color="g",ls="--")
plt.title("Entended RMS Difference")
plt.xlabel('Difference Index')
plt.ylabel('rmsd')
plt.xlim(0, 240)
plt.legend((extend_rmsd_outlier, extend_lower_rmsd_thres, extend_higher_rmsd_thres),
			('Extended Outliers', 'Lower IRQ threshold', 'Higher IRQ threshold'),
			loc=0)
plt.savefig('extended_vol_rms_outliers.png')
plt.close()

""" Write the extended outlier indices to a text file."""
np.savetxt('extended_vol_rms_outliers.txt', edo_index)

#===========================================================================================

"""
================================== PART II =======================================

Generalized Linear Model

Steps
-----
1) Constructing design matrix
2) Finding beta hats and model accuracy by MRSS
	a) before removing outilers
	b) after removing outliers
3) t-test
4) locate activated region
5) Plots

"""
# Constructing design matrix
convolved_1 = np.loadtxt('conv001.txt') 
convolved_2 = np.loadtxt('conv002.txt')
convolved_3 = np.loadtxt('conv003.txt')
convolved_4 = np.loadtxt('conv004.txt')

convolved1 = convolved_1[4:] 
convolved2 = convolved_2[4:]
convolved3 = convolved_3[4:]
convolved4 = convolved_4[4:]

N = len(convolved1)
X = np.ones((N, 5)) #make a metrix

X[:, 0] = convolved1 # gain
X[:, 1] = convolved2 # loss
X[:, 2] = convolved3 # confidence
X[:, 3] = convolved4 # response time

#==========================================================================================================
# Before removing outliers
# Getting beta hats
data2d = np.reshape(data, (np.prod(data.shape[:-1]), -1))
data2d_trans = data2d.T
Xp = npl.pinv(X)
beta_hat = Xp.dot(data2d_trans)

# calculate MRSS
MRSS_before = np.ones(data2d.shape[0])
res = data2d_trans - X.dot(beta_hat)
RSS = np.sum(res**2, axis=0)
df = X.shape[0] - npl.matrix_rank(X)
MRSS_before = RSS / df
print(np.mean(MRSS_before))

# After removing outliers
X_fixed = np.delete(X, edo_index, 0)
data2d_fixed = np.delete(data2d, edo_index, 1)
data2d_fixed_trans = data2d_fixed.T
Xp_fixed = npl.pinv(X_fixed)
beta_hat_fixed = Xp_fixed.dot(data2d_fixed_trans)

# calculate MRSS
MRSS_after = np.ones(data2d_fixed.shape[0])
res_fixed = data2d_fixed_trans - X_fixed.dot(beta_hat_fixed)
RSS_fixed = np.sum(res_fixed**2, axis=0)
df_fixed = X_fixed.shape[0] - npl.matrix_rank(X_fixed)
MRSS_after = RSS_fixed / df_fixed
print(np.mean(MRSS_after))

mean_mrss = np.array([np.mean(MRSS_before), np.mean(MRSS_after)])
np.savetxt('mean_mrss_vals.txt', mean_mrss)

"""================================== PART III =======================================

Location activated region
-------------------------
1) Find t value and corresonding p-value to determine the significance 
	of beta_hat for each condition 
2) Find voxels with relativly large beta and small p-vaule for each condition
3) Find the activated location on brain
"""
#1) Find t value and corresonding p-value to determine the significance of beta_hat for each condition 
t1, p1 = t_test(X, beta_hat, data2d)
t2, p2 = t_test(X_fixed, beta_hat_fixed, data2d_fixed)

beta_gain1 = beta_hat[0,:]
beta_gain1.shape = data.shape[:-1]
p_gain1 = p1[0,:]
p_gain1.shape = data.shape[:-1]

beta_loss1 = beta_hat[1,:]
beta_loss1.shape = data.shape[:-1]
p_loss1 = p1[1,:]
p_loss1.shape = data.shape[:-1]

beta_conf1 = beta_hat[2,:]
beta_conf1.shape = data.shape[:-1]
p_conf1 = p1[2,:]
p_conf1.shape = data.shape[:-1]

beta_restime1 = beta_hat[3,:]
beta_restime1.shape = data.shape[:-1]
p_restime1 = p1[3,:]
p_restime1.shape = data.shape[:-1]

#after removing outliers
beta_gain2 = beta_hat_fixed[0,:]
beta_gain2.shape = data.shape[:-1]
p_gain2 = p2[0,:]
p_gain2.shape = data.shape[:-1]

beta_loss2 = beta_hat_fixed[1,:]
beta_loss2.shape = data.shape[:-1]
p_loss2 = p2[1,:]
p_loss2.shape = data.shape[:-1]

beta_conf2 = beta_hat_fixed[2,:]
beta_conf2.shape = data.shape[:-1]
p_conf2 = p2[2,:]
p_conf2.shape = data.shape[:-1]

beta_restime2 = beta_hat_fixed[3,:]
beta_restime2.shape = data.shape[:-1]
p_restime2 = p2[3,:]
p_restime2.shape = data.shape[:-1]

#2) Find voxels with relativly large beta and small p-vaule for each condition
thres_gain1 = np.mean(beta_gain1)
thres_gain2 = np.mean(beta_gain2)
thres_loss1 = np.mean(beta_loss1)
thres_loss2 = np.mean(beta_loss2)
thres_conf1 = np.mean(beta_conf1)
thres_conf2 = np.mean(beta_conf2)
thres_restime1 = np.mean(beta_restime1)
thres_restime2 = np.mean(beta_restime2)

active_voxel_gain1 = np.transpose(((beta_gain1 > thres_gain1) & (p_gain1<0.05)).nonzero())
active_voxel_gain2 = np.transpose(((beta_gain2 > thres_gain2) & (p_gain2<0.05)).nonzero())
active_voxel_loss1 = np.transpose(((beta_loss1 > thres_loss1) & (p_loss1<0.05)).nonzero())
active_voxel_loss2 = np.transpose(((beta_loss2 > thres_loss2) & (p_loss2<0.05)).nonzero())
active_voxel_conf1 = np.transpose(((beta_conf1 > thres_conf1) & (p_conf1<0.05)).nonzero())
active_voxel_conf2 = np.transpose(((beta_conf2 > thres_conf2) & (p_conf2<0.05)).nonzero())
active_voxel_restime1 = np.transpose(((beta_restime1 > thres_restime1) & (p_restime1<0.05)).nonzero())
active_voxel_restime2 = np.transpose(((beta_restime2 > thres_restime2) & (p_restime2<0.05)).nonzero())

#3) Find the activated location on brain
vox_to_mm = sub.affine

location_gain1 = nib.affines.apply_affine(vox_to_mm, active_voxel_gain1)
location_gain2 = nib.affines.apply_affine(vox_to_mm, active_voxel_gain2)
location_loss1 = nib.affines.apply_affine(vox_to_mm, active_voxel_loss1)
location_loss2 = nib.affines.apply_affine(vox_to_mm, active_voxel_loss2)
location_conf1 = nib.affines.apply_affine(vox_to_mm, active_voxel_conf1)
location_conf2 = nib.affines.apply_affine(vox_to_mm, active_voxel_conf2)
location_restime1 = nib.affines.apply_affine(vox_to_mm, active_voxel_restime1)
location_restime2 = nib.affines.apply_affine(vox_to_mm, active_voxel_restime2)


"""================================== PART IV =======================================
Plots
"""
# plots for each beta
# before removing outliers
plt.subplot(221)
plot_3D_bold_nii(beta_gain1)
plt.title("Beta estimates for gain")

plt.subplot(222)
plot_3D_bold_nii(beta_loss1)
plt.title("Beta estimates for loss")

plt.subplot(223)
plot_3D_bold_nii(beta_conf1)
plt.title("Beta estimates for confidence level")

plt.subplot(224)
plot_3D_bold_nii(beta_restime1)
plt.title("Beta estimates for response time")

plt.savefig('beta4condition_v1.png')
plt.close()

# After removing outliers
plt.subplot(221)
plot_3D_bold_nii(beta_gain2)
plt.title("Beta estimates for gain")

plt.subplot(222)
plot_3D_bold_nii(beta_loss2)
plt.title("Beta estimates for loss")

plt.subplot(223)
plot_3D_bold_nii(beta_conf2)
plt.title("Beta estimates for confidence level")

plt.subplot(224)
plot_3D_bold_nii(beta_restime2)
plt.title("Beta estimates for response time")

plt.savefig('beta4condition_v2.png')
plt.close()

# Some final checks that you wrote the files with their correct names
from os.path import exists
assert exists('vol_std_values.txt')
assert exists('vol_std_outliers.txt')
assert exists('vol_std.png')
assert exists('vol_rms_outliers.png')
assert exists('extended_vol_rms_outliers.png')
assert exists('extended_vol_rms_outliers.txt')
assert exists('mean_mrss_vals.txt')
