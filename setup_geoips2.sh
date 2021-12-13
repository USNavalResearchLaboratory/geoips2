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

if [[ -z "$GEOIPS2_BASEDIR" ]]; then
    echo "Must define GEOIPS2_BASEDIR environment variable prior to setting up geoips2"
    exit 1
fi

# This sets required environment variables for setup - without requiring sourcing a geoips config in advance
. $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup/repo_clone_update_install.sh setup

umask 0002

if [[ "$1" == "conda_install" ]]; then
    echo ""
    # echo "**wgetting Anaconda3*.sh"
    # wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh -P $GEOIPS2_DEPENDENCIES_DIR
    # chmod 755 $GEOIPS2_DEPENDENCIES_DIR/Anaconda3-*.sh
    echo "**wgetting Miniconda3*.sh"
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -P $GEOIPS2_DEPENDENCIES_DIR
    chmod 755 $GEOIPS2_DEPENDENCIES_DIR/Miniconda3-*.sh
    echo ""
    echo "**Running Anaconda3*.sh"
    # $GEOIPS2_DEPENDENCIES_DIR/Anaconda3-*.sh -p $GEOIPS2_DEPENDENCIES_DIR/anaconda3
    $GEOIPS2_DEPENDENCIES_DIR/Miniconda3-*.sh -p $GEOIPS2_DEPENDENCIES_DIR/miniconda3
    echo ""
    echo "**If shell initialized, MUST source ~/.bashrc or restart shell"
    source ~/.bashrc
    echo "source ~/.bashrc"
elif [[ "$1" == "conda_link" ]]; then
    echo ""
    echo "**Linking conda to bin"
    ln -sfv $BASECONDAPATH/conda $GEOIPS2_DEPENDENCIES_DIR/bin
elif [[ "$1" == "conda_init" ]]; then
    echo ""
    echo "**Initializing conda"
    $BASECONDAPATH/conda init
    # Link conda to geoips2_dependencies/bin so it is in path
    $GEOIPS2_BASEDIR/geoips2_packages/geoips2/setup_geoips2.sh conda_link
    echo ""
    echo "**IF SCRIPT WAS NOT SOURCED MUST source ~/.bashrc or restart shell"
    source ~/.bashrc
    echo "source ~/.bashrc"
elif [[ "$1" == "conda_update" ]]; then
    echo ""
    echo "**updating base conda env"
    which conda
    which python
    conda update -n base -c defaults conda --yes
elif [[ "$1" == "remove_geoips2_conda_env" ]]; then
    echo ""
    echo "**removing geoips2_conda env"
    which conda
    which python
    echo "**IF SCRIPT WAS NOT SOURCED MUST first deactivate geoips2_conda env from parent shell"
    conda deactivate
    echo "conda deactivate"
    conda env remove --name geoips2_conda
elif [[ "$1" == "create_geoips2_conda_env" ]]; then
    echo ""
    echo "**creating geoips2_conda env"
    which conda
    which python
    conda create --yes --name geoips2_conda python=3.9 --yes
    echo "**IF SCRIPT WAS NOT SOURCED MUST activate geoips2_conda env from parent shell"
    conda activate geoips2_conda
    echo "conda activate geoips2_conda"
elif [[ "$1" == "install_geoips2" ]]; then
    echo ""
    echo "**Installing cartopy"
    # cartopy 0.19.0 and matplotlib 3.4.0 both cause slightly shifted figures compared to old versions
    # Updating test outputs to latest versions
    # $BASECONDAPATH/conda install -c conda-forge cartopy matplotlib
    # This was getting 0.18.0 sometimes without specifying version ???  Force to 0.20.0
    $BASECONDAPATH/conda install -c conda-forge cartopy=0.20.0 matplotlib=3.4.3 --yes

    pip install -e $GEOIPS2_PACKAGES_DIR/geoips2

elif [[ "$1" == "setup_abi_test_data" ]]; then
    # rclone lsf publicAWS:noaa-goes16/ABI-L1b-RadF/2020/184/16/
    abidir=$GEOIPS2_PACKAGES_DIR/geoips2/tests/data/goes16_20200918_1950/
    mkdir -p $abidir
    echo "** Setting up abi test data, from publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/ to $abidir"
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C01_G16_s20202621950205_e20202621959513_c20202621959567.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C02_G16_s20202621950205_e20202621959513_c20202621959546.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C03_G16_s20202621950205_e20202621959513_c20202621959570.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C04_G16_s20202621950205_e20202621959513_c20202621959534.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C05_G16_s20202621950205_e20202621959513_c20202621959562.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C06_G16_s20202621950205_e20202621959518_c20202621959556.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C07_G16_s20202621950205_e20202621959524_c20202621959577.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C08_G16_s20202621950205_e20202621959513_c20202621959574.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C09_G16_s20202621950205_e20202621959518_c20202621959588.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C10_G16_s20202621950205_e20202621959524_c20202621959578.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C11_G16_s20202621950205_e20202621959513_c20202621959583.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C12_G16_s20202621950205_e20202621959518_c20202621959574.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C13_G16_s20202621950205_e20202621959525_c20202622000005.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C14_G16_s20202621950205_e20202621959513_c20202622000009.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C15_G16_s20202621950205_e20202621959518_c20202621959594.nc $abidir
    rclone copy -P publicAWS:noaa-goes16/ABI-L1b-RadF/2020/262/19/OR_ABI-L1b-RadF-M6C16_G16_s20202621950205_e20202621959524_c20202622000001.nc $abidir

elif [[ "$1" == "setup_seviri" ]]; then
    mkdir -p $GEOIPS2_DEPENDENCIES_DIR/seviri_wavelet
    cd $GEOIPS2_DEPENDENCIES_DIR/seviri_wavelet
    git clone https://gitlab.eumetsat.int/open-source/PublicDecompWT.git
    make all -C $GEOIPS2_DEPENDENCIES_DIR/seviri_wavelet/PublicDecompWT/xRITDecompress
    ln -sfv $GEOIPS2_DEPENDENCIES_DIR/seviri_wavelet/PublicDecompWT/xRITDecompress/xRITDecompress $GEOIPS2_DEPENDENCIES_DIR/bin/xRITDecompress
elif [[ "$1" == "setup_rclone" ]]; then
    mkdir -p $GEOIPS2_DEPENDENCIES_DIR/rclone
    cd $GEOIPS2_DEPENDENCIES_DIR/rclone
    curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
    unzip rclone*.zip
    ln -sfv ${GEOIPS2_DEPENDENCIES_DIR}/rclone*/rclone*/rclone ${GEOIPS2_DEPENDENCIES_DIR}/bin/rclone
elif [[ "$1" == "setup_vim8" ]]; then
    mkdir -p $GEOIPS2_DEPENDENCIES_DIR/vim8_build
    cd $GEOIPS2_DEPENDENCIES_DIR/vim8_build
    git clone https://github.com/vim/vim.git
    cd vim
    ./configure --prefix=${GEOIPS2_DEPENDENCIES_DIR}/vim8_build/vim --disable-nls --enable-cscope --enable-gui=no --enable-multibyte --enable-pythoninterp --with-features=huge --with-tlib=ncurses --without-x;
    make
    make install
    ln -s $GEOIPS2_DEPENDENCIES_DIR/vim8_build/vim/bin/vim $GEOIPS2_DEPENDENCIES_DIR/bin/vi
    ln -s $GEOIPS2_DEPENDENCIES_DIR/vim8_build/vim/bin/vim $GEOIPS2_DEPENDENCIES_DIR/bin/vim
elif [[ "$1" == "setup_vim8_plugins" ]]; then
    mkdir -p $GEOIPS2_DEPENDENCIES_DIR/vimdotdir/pack/plugins/start
    cd $GEOIPS2_DEPENDENCIES_DIR/vimdotdir/pack/plugins/start
    git clone https://github.com/w0rp/ale.git
    pip install flake8
    pip install pylint
    pip install bandit
    mkdir -p ~/.vim/pack
    ## If ~/.vim/pack does not exist, link it, otherwise link the contents appropriately.
    echo ""
    ln -sv $GEOIPS2_DEPENDENCIES_DIR/vimdotdir/pack/* ~/.vim/pack
    if [[ $? != 0 ]]; then
        echo "If you want to replace ~/.vim/pack with geoips2 version, run the following:"
        echo "ln -sfv $GEOIPS2_DEPENDENCIES_DIR/vimdotdir/pack/* ~/.vim/pack"
    fi
    echo ""
    ## Either add the contents of vimrc_ale to your ~/.vimrc, or replace it
    ln -sv $GEOIPS2_PACKAGES_DIR/geoips2/setup/bash_setup/vimrc_ale ~/.vimrc
    if [[ $? != 0 ]]; then
        echo "If you want to replace ~/.vimrc with geoips2 ALE version, run the following:"
        echo "ln -sfv $GEOIPS2_PACKAGES_DIR/geoips2/setup/bash_setup/vimrc_ale ~/.vimrc"
    fi
elif [[ "$1" == "install_cartopy_offlinedata" ]]; then
    echo ""
    echo "**Installing conda cartopy offlinedata"
    # 0.2.4 no longer sets $CARTOPY_OFFLINE_SHARED
    $BASECONDAPATH/conda install -c conda-forge cartopy_offlinedata==0.2.3
    echo ""
    echo "CARTOPY_OFFLINE_SHARED: $CARTOPY_OFFLINE_SHARED"
    echo ""
    echo "**Installing github.com/nvkelso/natural-earth-vector map data, this will take a while"
    cartopy_data=$GEOIPS2_DEPENDENCIES_DIR/cartopy_map_data
    echo "    destination: $cartopy_data"
    mkdir -p $cartopy_data
    git -C $cartopy_data clone https://github.com/nvkelso/natural-earth-vector
    echo ""
    echo "**Linking natural-earth-data to CARTOPY_OFFLINE_SHARED: $CARTOPY_OFFLINE_SHARED"
    ln -sf $cartopy_data/natural-earth-vector/*_cultural/* $CARTOPY_OFFLINE_SHARED/shapefiles/natural_earth/cultural
    ln -sf $cartopy_data/natural-earth-vector/*_physical/* $CARTOPY_OFFLINE_SHARED/shapefiles/natural_earth/physical
elif [[ "$1" =~ "clone_test_repo" ]]; then
    echo ""
    echo "**Cloning $2.git"
    git clone $GEOIPS2_REPO_URL/$2.git $GEOIPS2_TESTDATA_DIR/$2
    retval=$?
    echo "git clone return: $retval"
    if [[ $retval != 0 ]]; then
        echo "**You can ignore 'fatal: destination path already exists' - just means you already have the repo"
    fi
elif [[ "$1" =~ "update_test_repo" ]]; then
    if [[ "$3" == "" ]]; then
        branch=dev
    else
        branch=$3
    fi
    currdir=$GEOIPS2_TESTDATA_DIR/$2
    echo ""
    echo "**Updating test repo $2 branch $branch"
    git -C $GEOIPS2_TESTDATA_DIR/$2 pull
    git -C $GEOIPS2_TESTDATA_DIR/$2 checkout -t origin/$branch
    retval_t=$?
    git -C $GEOIPS2_TESTDATA_DIR/$2 checkout $branch
    retval=$?
    git -C $GEOIPS2_TESTDATA_DIR/$2 pull
    git -C $GEOIPS2_TESTDATA_DIR/$2 pull
    retval_pull=$?
    echo "git checkout -t return: $retval_t"
    echo "git checkout return: $retval"
    echo "git pull return: $retval_pull"
    if [[ $retval != 0 || $retval_t != 0 ]]; then
        echo "**You can ignore 'fatal: A branch named <branch> already exists' - just means you already have the branch"
    fi
    if [[ $retval != 0 && $retval_t != 0 ]]; then
        echo "*****GIT CHECKOUT FAILED ON $currdir $branch PLEASE APPROPRIATELY commit (if you want to save your changes), checkout (if you do not want to save changes of a git-tracked file), or delete (if you do not want to save changes of an untracked file) ANY LOCALLY MODIFIED FILES AND RERUN repo_update COMMAND. This will ensure you have the latest version of all repos!!!!!!!!"
        exit 1
    fi
    if [[ $retval_pull != 0 ]]; then
        echo "*****GIT PULL FAILED ON $currdir $branch PLEASE APPROPRIATELY commit (if you want to save your changes), checkout (if you do not want to save changes of a git-tracked file), or delete (if you do not want to save changes of an untracked file) ANY LOCALLY MODIFIED FILES AND RERUN repo_update COMMAND. This will ensure you have the latest version of all repos!!!!!!!!"
        exit 1
    fi
elif [[ "$1" == "uncompress_test_data" ]]; then
    echo ""
    echo "Attempting uncompress $2..."
    testdata_path=$GEOIPS2_TESTDATA_DIR/$2/uncompress_test_data.sh
    packages_path=$GEOIPS2_PACKAGES_DIR/$2/tests/uncompress_test_data.sh

    uncompress_script=""
    if [[ -e $testdata_path ]]; then
        uncompress_script=$testdata_path
    elif [[ -e $packages_path ]]; then
        uncompress_script=$packages_path
    fi

    if [[ $uncompress_script != "" ]]; then
        echo "     $uncompress_script..."
        $uncompress_script
        retval=$?
        if [[ $retval != 0 ]]; then
            echo "******FAILED uncompress_test_data - please resolve and rerun uncompress_test_data command"
            exit 1
        fi
    fi

elif [[ "$1" == "recompress_test_data" ]]; then
    echo ""
    echo "Attempting recompress $2..."

    testdata_path=$GEOIPS2_TESTDATA_DIR/$2/recompress_test_data.sh
    packages_path=$GEOIPS2_PACKAGES_DIR/$2/tests/recompress_test_data.sh

    recompress_script=""
    if [[ -e $testdata_path ]]; then
        recompress_script=$testdata_path
    elif [[ -e $packages_path ]]; then
        recompress_script=$packages_path
    fi
    if [[ -e $recompress_script ]]; then
        echo "     $recompress_script..."
        $recompress_script
        retval=$?
        if [[ $retval != 0 ]]; then
            echo "******FAILED uncompress_test_data - please resolve and rerun uncompress_test_data command"
            exit 1
        fi
    fi
elif [[ "$1" =~ "clone_source_repo" ]]; then
    echo ""
    echo "**Cloning $2.git"
    git clone $GEOIPS2_REPO_URL/$2.git $GEOIPS2_PACKAGES_DIR/$2
    retval=$?
    echo "git clone return: $retval"
    if [[ $retval != 0 ]]; then
        echo "**You can ignore 'fatal: destination path already exists' - just means you already have the repo"
    fi
elif [[ "$1" =~ "update_source_repo" ]]; then
    if [[ "$3" == "" ]]; then
        branch=dev
    else
        branch=$3
    fi
    currdir=$GEOIPS2_PACKAGES_DIR/$2
    echo ""
    echo "**Updating $2 branch $branch"
    git -C $GEOIPS2_PACKAGES_DIR/$2 pull
    git -C $GEOIPS2_PACKAGES_DIR/$2 checkout -t origin/$branch
    retval_t=$?
    git -C $GEOIPS2_PACKAGES_DIR/$2 checkout $branch
    retval=$?
    git -C $GEOIPS2_PACKAGES_DIR/$2 pull
    git -C $GEOIPS2_PACKAGES_DIR/$2 pull
    retval_pull=$?
    echo "git checkout -t return: $retval_t"
    echo "git checkout return: $retval"
    echo "git pull return: $retval_pull"
    if [[ $retval != 0 || $retval_t != 0 ]]; then
        echo "**You can ignore 'fatal: A branch named <branch> already exists' - just means you already have the branch"
    fi
    if [[ $retval != 0 && $retval_t != 0 ]]; then
        echo "*****GIT CHECKOUT FAILED ON $currdir $branch PLEASE APPROPRIATELY commit (if you want to save your changes), checkout (if you do not want to save changes of a git-tracked file), or delete (if you do not want to save changes of an untracked file) ANY LOCALLY MODIFIED FILES AND RERUN repo_update COMMAND. This will ensure you have the latest version of all repos!!!!!!!!"
        exit 1
    fi
    if [[ $retval_pull != 0 ]]; then
        echo "*****GIT PULL FAILED ON $currdir $branch PLEASE APPROPRIATELY commit (if you want to save your changes), checkout (if you do not want to save changes of a git-tracked file), or delete (if you do not want to save changes of an untracked file) ANY LOCALLY MODIFIED FILES AND RERUN repo_update COMMAND. This will ensure you have the latest version of all repos!!!!!!!!"
        exit 1
    fi
elif [[ "$1" =~ "clone_external_repo" ]]; then
    echo ""
    echo "**Cloning external repo $2"
    if [[ "$2" == "archer" ]]; then
        git clone https://github.com/ajwimmers/archer $GEOIPS2_PACKAGES_DIR/archer
        retval=$?
        echo "git clone return: $retval"
    else
        echo "Unknown external repo"
    fi
    if [[ $retval != 0 ]]; then
        echo "**You can ignore 'fatal: destination path already exists' - just means you already have the repo"
    fi
elif [[ "$1" =~ "run_git_cmd" ]]; then
    gitbasedir=$GEOIPS2_PACKAGES_DIR
    if [[ "$4" != "" ]]; then
        gitbasedir=$4
    fi
    echo ""
    echo "**Running git -C $gitbasedir/$2 $3"
    git -C $gitbasedir/$2 $3
    retval=$?
    echo "git $3 return: $retval"
elif [[ "$1" =~ "update_external_repo" ]]; then
    currdir=$GEOIPS2_PACKAGES_DIR/$2
    echo ""
    echo "**Updating external repo $2"
    git -C $GEOIPS2_PACKAGES_DIR/$2 pull
    retval=$?
    echo "git pull return: $retval"
    if [[ $retval != 0 ]]; then
        echo "*****GIT PULL FAILED ON $currdir PLEASE APPROPRIATELY commit (if you want to save your changes), checkout (if you do not want to save changes of a git-controlled file), or delete (if you do not want to save changes of a non-git-controlled file) ANY LOCALLY MODIFIED FILES AND RERUN repo_update COMMAND. This will ensure you have the latest version of all repos!!!!!!!!"
        exit 1
    fi
elif [[ "$1" =~ "install_plugin" ]]; then
    echo ""
    echo "**Installing plugin $2"
    $GEOIPS2_PACKAGES_DIR/$2/setup_$2.sh install_$2
    if [[ $? != 0 ]]; then
        echo "**Trying pip installing plugin $2"
        pip install -e $GEOIPS2_PACKAGES_DIR/$2
    fi
    echo ""
else
    echo "UNRECOGNIZED COMMAND $1"
    exit 1
fi
exit 0
