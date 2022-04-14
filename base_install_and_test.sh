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
        echo "Just completed '$1'"
        echo "Next run '$2'"
        echo ""
        echo "Y or y to perform '$2'"
        echo "K or k to skip '$2' but continue to following step"
        echo "Q or q to quit installation altogether?"
        read -r -p "[y/k/q]: " CONTINUE
    done
    if [[ $CONTINUE == "q" || $CONTINUE == "Q" ]]; then
        echo "Quitting"
        exit 1
    elif [[ $CONTINUE == "k" || $CONTINUE == "K" ]]; then
        echo "Skipping"
        skip_next="yes" 
    else
        echo "Continuing!"
        skip_next="no"
    fi
}

if [[ "$1" == "" ]]; then
    GEOIPS2_ACTIVE_BRANCH=dev
else
    GEOIPS2_ACTIVE_BRANCH=$1
fi
    

    echo ""
    echo "NOTE Approximately 30GB disk space / 10GB memory required for complete installation and test"
    echo ""
    echo "NOTE Expert users can install piece meal to avoid this time consuming installation process (>1h)"
    echo "     This full installation installs ALL dependencies from scratch,"
    echo "     to ensure a consistent environment for successful test returns"
    echo "     This includes"
    echo "          * Full Miniconda installation"
    echo "          * full cartopy coastline and political borders information"
    echo "          * ABI test datasets"
    echo "          * vim8 installation with syntax highlighting to encourage following style guide"
    echo ""
    echo "Confirm environment variables point to desired installation parameters:"
    echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
    echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
    echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
    echo ""

check_continue "verifying GEOIPS2_BASEDIR and GEOIPS2_CONFIG_FILE and GEOIPS2_ACTIVE_BRANCH" "clone geoips2"

    if [[ "$skip_next" == "no" ]]; then
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
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should not exist yet!): "`which conda`
    fi

check_continue "cloning geoip2 repo" "install conda"

    if [[ "$skip_next" == "no" ]]; then
        # Install conda
        # Do not initialize your shell at the end, to allow switching between versions!!!
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_install

        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_link
        # Activate current conda base environment - note geoips2_conda doesn't exist yet, but that is ok.
        # We need to at least point to "new" python and conda
        source $GEOIPS2_CONFIG_FILE

        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (point to geoips2_dependencies/miniconda3): "`which conda`
        echo "    which pip (point to geoips2_dependencies/miniconda3):   "`which conda`
        echo "    which python (point to geoips2_dependencies/miniconda3):     "`which python`
    fi

check_continue "installing conda (should point to $GEOIPS2_BASEDIR/geoips2_dependencies/miniconda3)" "create geoips2_conda_env"

    if [[ "$skip_next" == "no" ]]; then
        # Create geoips2 conda environment
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_update  # only for a fresh Miniconda install
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh create_geoips2_conda_env
        # Now we can use source $GEOIPS2_CONFIG_FILE
        source $GEOIPS2_CONFIG_FILE
        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point to geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "creating geoips2_conda_env (should point to $GEOIPS2_BASEDIR/geoips2_dependencies/miniconda3/envs/geoips2_conda)" "install geoips2 and dependencies"

    if [[ "$skip_next" == "no" ]]; then
        # Actually install geoips2 and all dependencies (cartopy, etc)
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh install_geoips2
        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point to geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "install geoips2 and dependencies" "Download cartopy natural earth data (REQUIRED for successful test returns, but takes ~10min and ~16GB to download)"

    if [[ "$skip_next" == "no" ]]; then

        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh download_cartopy_natural_earth

        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point to geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "Downloading cartopy natural earth data" "Link cartopy natural earth data to ~/.local/share/cartopy (to ensure cartopy uses the correct shapefiles in order for test outputs to match exactly)"

    if [[ "$skip_next" == "no" ]]; then
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh link_cartopy_natural_earth

        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point to geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "installing cartopy data" "install rclone (REQUIRED for test script)"
    if [[ "$skip_next" == "no" ]]; then
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2/setup_geoips2.sh setup_rclone # abi/ahi ingest
        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "installing rclone" "OPTIONAL install seviri libraries (required for seviri HRIT processing)"
    if [[ "$skip_next" == "no" ]]; then
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2/setup_geoips2.sh setup_seviri
        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "installing seviri libraries" "OPTIONAL install vim8"

    if [[ "$skip_next" == "no" ]]; then
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2/setup_geoips2.sh setup_vim8  # vim syntax highlighting

        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "installing vim8" "OPTIONAL install vim8 plugins (updates ~/.vim and ~/.vimrc to set up syntax highlighting based on geoips2 style guide)"

    if [[ "$skip_next" == "no" ]]; then
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2/setup_geoips2.sh setup_vim8_plugins  # vim syntax highlighting

        echo ""
        echo "Confirm environment variables point to desired installation parameters:"
        echo "    GEOIPS2_BASEDIR:       $GEOIPS2_BASEDIR"
        echo "    GEOIPS2_CONFIG_FILE:   $GEOIPS2_CONFIG_FILE"
        echo "    GEOIPS2_ACTIVE_BRANCH: $GEOIPS2_ACTIVE_BRANCH"
        echo "    which conda (should point geoips2_dependencies/bin): "`which conda`
        echo "    which python (should point to miniconda3 envs/geoips2_conda): "`which python`
    fi

check_continue "installing geoips2, cartopy data, dependencies, and external packages" "run basic test script"

    if [[ "$skip_next" == "no" ]]; then
        source $GEOIPS2_CONFIG_FILE
        $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh setup_abi_test_data
        $GEOIPS2/tests/test_base_install.sh
        retval=$?

        echo ""
        echo "full return: $retval"
    fi

check_continue "Installing and testing geoips2" "Done with base installation and test!"
