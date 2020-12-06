 | # # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited. # # #
 | # # #  # # #
 | # # # Author: # # #
 | # # # Naval Research Laboratory, Marine Meteorology Division # # #
 | # # #  # # #
 | # # # This program is free software: you can redistribute it and/or modify it under # # #
 | # # # the terms of the NRLMMD License included with this program.  If you did not # # #
 | # # # receive the license, see http://www.nrlmry.navy.mil/geoips for more # # #
 | # # # information. # # #
 | # # #  # # #
 | # # # This program is distributed WITHOUT ANY WARRANTY; without even the implied # # #
 | # # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the # # #
 | # # # included license for more details. # # #

Installation Guide
==================================

Using a fresh Anaconda Python 3.8 Environment is the easiest way to get geoips2 up and running.

geoips2 does not support Python 2 development.


Setup System Environment Variables
----------------------------------

.. code-block:: bash
    :linenos:

    # Set up appropriate environment variables for conda-based geoips2 setup

    # GEOIPS2_BASEDIR will contain all source, output, and external dependencies
    export GEOIPS2_BASEDIR=$HOME/satproc


Clone geoips2 git repository
----------------------------------


.. code-block:: bash
    :linenos:

    # Clone the geoips repository into GEOIPS2_MODULES_DIR and cd to the set up directory
    mkdir -p $GEOIPS2_BASEDIR/geoips2_modules
    git clone -b dev https://github.com/USNavalResearchLaboratory/geoips2.git $GEOIPS2_BASEDIR/geoips2_modules/geoips2


Setup Anaconda Environment
----------------------------

.. code-block:: bash
    :linenos:

    # geoips2/setup/geoips2_conda_setup:
    wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh -P $HOME
    chmod 755 $HOME/Anaconda3*.sh
    $HOME/Anaconda3*.sh
    $HOME/anaconda3/bin/conda init
    # Manually restart your shell to activate conda
    export GEOIPS2_BASEDIR=$HOME/satproc
    conda update -n base -c defaults conda
    conda env create -f $GEOIPS2_BASEDIR/geoips2_modules/geoips2/setup/geoips2_conda_environment.yml
    conda activate geoips2_conda


Test geoips2 Installation
----------------------------

This test script processes AMSR2 data over a tropical cyclone and produces a large number of output files.  
It should take approximately 6-7 minutes to run. This test repo contains a representative sample of products
available through geoips2.


.. code-block:: bash
    :linenos:

    # Obtain test data repo for functionality test
    cd $GEOIPS2_BASEDIR
    ### Request complete geoips_test_data_amsr2 test data repo from geoips@nrlmry.navy.mil

    # Run functionality test
    source $GEOIPS2_BASEDIR/geoips2_modules/geoips2/setup/config_geoips2
    $GEOIPS2_BASEDIR/geoips_test_data_amsr2/test_amsr2_python3.sh runall
