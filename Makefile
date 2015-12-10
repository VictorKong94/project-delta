#####################
# GENERAL UTILITIES #
#####################

.PHONY: all clean coverage test

all: clean

clean:
	find . -name "*.pyx.md5" -o -name ".DS_Store" -o -name "__pycache__" \
	-o -name "._hashes.json" -o -name "ds107_sub001_highres.nii" \
	-o -name "*.pyc" -o -name ".ipynb_checkpoints" | xargs rm -rf


#############
# VARIABLES #
#############

raw_data="http://openfmri.s3.amazonaws.com/tarballs/ds005_raw.tgz"
filtered_data="http://nipy.bic.berkeley.edu/rcsds/ds005_mnifunc.tar"
color="http://www.jarrodmillman.com/rcsds/_downloads/actc.txt"

##########
# SET-UP #
##########

dataset:
	wget $(raw_data) --directory-prefix=data
	wget $(filtered_data) --directory-prefix=data
	wget $(colors) --directory-prefix=data/scripts
	tar -xvzf data/ds005_raw.tgz -C data/
	tar -xvzf data/ds005_mnifunc.tar -C data/
	rm data/ds005_raw.tgz data/ds005_mnifunc.tar

test-data:
	python code/utils/make_test_data.py

validate-data:
	python code/data.py

test:
	nosetests code/tests data/test_data.py

rm-test-data:
	find . -name "subtest" | xargs rm -rf

verbose:
	nosetests -v code/tests data/tests


############
# COVERAGE #
############

coverage:
	make test-data
	nosetests code/tests data/test_data.py --with-coverage \
	--cover-package=code/utils,data/data.py


#############################
# RUN DATA ANALYSIS SCRIPTS #
#############################

convolution:
	python code/scripts/convolution.py

linear:
	python code/scripts/linear_analysis.py

logistic:
	python code/scripts/run_logistic_model.py

smoothing:
	python code/scripts/smooth_script.py

analyses:
	make convolution
	make linear
	make logistic
	make smoothing

rm-results:
	rm -rf results
	
