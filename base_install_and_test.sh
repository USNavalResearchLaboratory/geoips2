# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
# # # 
# # # Author:
# # # Naval Research Laboratory, Marine Meteorology Division
# # # 
# # # This program is free software: you can redistribute it and/or modify it under
# # # the terms of the NRLMMD License included with this program.  If you did not
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
# # # information.
# # # 
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # # included license for more details.

#!/bin/bash

check_continue() {
    unset CONTINUE
    while [ -z "$CONTINUE" ]; do
        echo ""
        echo ""
        read -r -p "Y or y to continue after $1, next $2? [y/N]: " CONTINUE
    done
    if [ $CONTINUE != "y" ] && [ $CONTINUE != "Y" ]; then
        echo "Quitting"
        exit 1
    fi
}

if [[ "$1" == "" ]]; then
    GEOIPS2_ACTIVE_BRANCH=dev
else
    GEOIPS2_ACTIVE_BRANCH=$1
fi
    

    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"

check_continue "verifying GEOIPS2_BASEDIR and GEOIPS2_CONFIG_FILE and GEOIPS2_ACTIVE_BRANCH" "clone geoips2"

    # Initial clone of geoips2 repo, to obtain setup scripts
    mkdir -p $GEOIPS2_BASEDIR/geoips2_packages
    git clone $GEOIPS2_REPO_URL/geoips2.git $GEOIPS2_BASEDIR/geoips2_packages/geoips2
    
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 pull
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 checkout -t origin/$GEOIPS2_ACTIVE_BRANCH
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 checkout $GEOIPS2_ACTIVE_BRANCH
    git -C $GEOIPS2_BASEDIR/geoips2_packages/geoips2 pull

    ls -ld $GEOIPS2_BASEDIR/geoips2_packages/*
    
    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
    echo "which conda (should not exist yet!): "`which conda`

check_continue "cloning geoip2 repo" "install conda"

    # Install conda
    # Do not initialize your shell at the end, to allow switching between versions!!!
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_install

    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_link
    # Activate current conda base environment - note geoips2_conda doesn't exist yet, but that is ok.
    # We need to at least point to "new" python and conda
    source $GEOIPS2_CONFIG_FILE

    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
    echo "which conda (point to geoips2_dependencies/miniconda3): "`which conda`
    echo "which pip (point to geoips2_dependencies/miniconda3):   "`which conda`
    echo "which python (point to geoips2_dependencies/miniconda3):     "`which python`

check_continue "installing conda (should point to $GEOIPS2_BASEDIR/geoips2_dependencies/miniconda3)" "create geoips2_conda_env"

    # Create geoips2 conda environment
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_update  # only for a fresh Miniconda install
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh create_geoips2_conda_env
    source $GEOIPS2_CONFIG_FILE
    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
    echo "which conda (should point to geoips2_dependencies/bin): "`which conda`
    echo "which python (should point to miniconda3 envs/geoips2_conda): "`which python`

check_continue "creating geoips2_conda_env (should point to $GEOIPS2_BASEDIR/geoips2_dependencies/miniconda3/envs/geoips2_conda)" "install geoips2 and dependencies"

    # Actually install geoips2 and all dependencies (cartopy, etc)
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh install_geoips2
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh install_cartopy_offlinedata

    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
    echo "which conda (should point to geoips2_dependencies/bin): "`which conda`
    echo "which python (should point to miniconda3 envs/geoips2_conda): "`which python`

check_continue "installing geoips2 and dependencies" "install external dependencies"

    source $GEOIPS2_CONFIG_FILE
    $GEOIPS2/setup_geoips2.sh setup_seviri
    $GEOIPS2/setup_geoips2.sh setup_rclone # abi/ahi ingest
    $GEOIPS2/setup_geoips2.sh setup_vim8  # vim syntax highlighting
    $GEOIPS2/setup_geoips2.sh setup_vim8_plugins  # vim syntax highlighting

    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
    echo "which conda (should point geoips2_dependencies/bin): "`which conda`
    echo "which python (should point to miniconda3 envs/geoips2_conda): "`which python`

check_continue "installing external dependencies" "run basic test script"

    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh setup_abi_test_data
    $GEOIPS2/tests/test_base_install.sh
    retval=$?

    echo ""
    echo "full return: $retval"

check_continue "running basic test script" "run full test script"

    $GEOIPS2/tests/test_all.sh
    retval=$?

    echo ""
    echo "full return: $retval"

check_continue "running test scripts"
