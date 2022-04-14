#### # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
#### # # 
#### # # Author:
#### # # Naval Research Laboratory, Marine Meteorology Division
#### # # 
#### # # This program is free software: you can redistribute it and/or modify it under
#### # # the terms of the NRLMMD License included with this program.  If you did not
#### # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
#### # # information.
#### # # 
#### # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
#### # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#### # # included license for more details.

Installation Guide
==================

Using a fresh Mini/Anaconda Python 3.8 or 3.9 Environment is the easiest way to get geoips2 up and running.

geoips2 does not support Python 2 development.


Setup System Environment Variables
----------------------------------

```bash

    # Set up appropriate environment variables for conda-based geoips2 setup steps within this README below.
    # The steps within this section will need to be copied and pasted into your shell any time you want to
    # run the setup commands within this README. Typical users do not have to make any modifications to the
    # commands within this README and can copy and paste directly.

    # Once geoips2 has been installed, the "GEOIPS2_CONFIG_FILE" specified below will be sourced when running geoips2,
    # and the direct environment variable assignments within this section are no longer required.

    # If you would like to have the GEOIPS2_CONFIG_FILE automatically sourced so you do not have to manually run the 
    # appropriate source command for every new shell, you can add 
    # source </full/path/to/GEOIPS2_CONFIG_FILE>
    # to your ~/.bashrc file

    # If you have sudo/apt access to your system, ensure all required libraries are available
    # sudo apt-get update               # Make sure apt packages are up to date
    # sudo apt install wget             # Required for Miniconda and rclone setup
    # sudo apt install git              # Required for all git clones, >=2.19.1
    # sudo apt install imagemagick      # Required for test output comparisons
    # sudo apt install gfortran         # OPTIONAL - Required if you have plugins with fortran builds
    # sudo apt install build-essential  # OPTIONAL - Required if you have plugins with fortran/C builds
    # sudo apt install screen           # OPTIONAL - convenience package
    # sudo apt install ncurses          # OPTIONAL - Required for vim build
    # sudo apt install libncurses5-dev  # OPTIONAL - Required for vim build


    # GEOIPS2_BASEDIR will contain all source, output, and external dependencies
    # Ensure this is consistently set for all installation / setup steps below
    export GEOIPS2_BASEDIR=$HOME/geoproc

    # GEOIPS2_REPO_URL should point to the base URL for git clone commands
    export GEOIPS2_REPO_URL=https://github.com/USNavalResearchLaboratory/

    # This config file must be sourced ANY TIME you want to run geoips2
    export GEOIPS2_CONFIG_FILE=$GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup/config_geoips2

    GEOIPS2_ACTIVE_BRANCH=dev
```


Base geoips2 installation and test
----------------------------------
```
    # Initial clone of geoips2 repo, to obtain setup scripts
    mkdir -p $GEOIPS2_BASEDIR/geoips2_packages
    git clone $GEOIPS2_REPO_URL/geoips2.git $GEOIPS2_BASEDIR/geoips2_packages/geoips2
    
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 pull
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 checkout -t origin/$GEOIPS2_ACTIVE_BRANCH
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 checkout $GEOIPS2_ACTIVE_BRANCH
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 pull

    # This prompts you through all the steps of installing geoips2 from scratch, using the parameters specified above
    # Installs and tests everything!
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/base_install_and_test.sh $GEOIPS2_ACTIVE_BRANCH
```
