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

# These commands loop through all required plugins and test data repos for a given package.

# internal_plugins, internal_algs, external_repos, and test_repos set within <package> setup_<package>.sh

if [[ "$1" == "setup" ]]; then
    if [[ -z "$GEOIPS2_BASEDIR" ]]; then
        echo "Must define GEOIPS2_BASEDIR environment variable prior to setting up geoips2"
        exit 1
    fi
    if [[ -z "$GEOIPS2_REPO_URL" ]]; then
        echo "Must defined GEOIPS2_REPO_URL environment variable prior to setting up geoips2"
        exit 1
    fi
    
    mkdir -p $GEOIPS2_BASEDIR/geoips2_dependencies/bin
    mkdir -p $GEOIPS2_BASEDIR/geoips2_packages
    mkdir -p $GEOIPS2_BASEDIR/test_data
    export GEOIPS2_DEPENDENCIES_DIR=$GEOIPS2_BASEDIR/geoips2_dependencies
    export GEOIPS2_PACKAGES_DIR=$GEOIPS2_BASEDIR/geoips2_packages
    export GEOIPS2_TESTDATA_DIR=$GEOIPS2_BASEDIR/test_data
    export BASECONDAPATH=$GEOIPS2_DEPENDENCIES_DIR/miniconda3/bin
elif [[ "$1" == "repo_clone" ]]; then
    for internal_repo in $internal_plugins $internal_algs; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh clone_source_repo $internal_repo
        retval=$?
        if [[ $retval != 0 ]]; then
            echo "******FAILED repo_clone internal repos - please resolve and rerun repo_clone command"
            exit 1
        fi
    done
    for external_repo in $external_repos; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh clone_external_repo $external_repo
        retval=$?
        if [[ $retval != 0 ]]; then
            echo "******FAILED repo_clone external repos - please resolve and rerun repo_clone command"
            exit 1
        fi
    done
    for test_repo in $test_repos; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh clone_test_repo $test_repo
        retval=$?
        if [[ $retval != 0 ]]; then
            echo "******FAILED repo_clone test repo - please resolve and rerun repo_clone command"
            exit 1
        fi
    done

elif [[ "$1" == "repo_update" ]]; then
    if [[ "$2" == "" ]]; then
        branch=dev
    else
        branch=$2
    fi
    if [[ "$3" == "" ]]; then
        do_not_fail=""
    else
        do_not_fail="do_not_fail"
    fi
    for internal_plugin in $internal_plugins; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_source_repo $internal_plugin $branch $do_not_fail
        retval=$?
        if [[ $retval != 0 && "$do_not_fail" != "do_not_fail" ]]; then
            echo "******FAILED repo_update internal plugin - please resolve and rerun repo_update command"
            exit 1
        fi
    done
    for internal_alg in $internal_algs; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_source_repo $internal_alg $branch $do_not_fail
        retval=$?
        if [[ $retval != 0 && "$do_not_fail" != "do_not_fail" ]]; then
            echo "******FAILED repo_update internal alg - please resolve and rerun repo_update command"
            exit 1
        fi
    done
    for external_repo in $external_repos; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_external_repo $external_repo $do_not_fail
        retval=$?
        if [[ $retval != 0 && "$do_not_fail" != "do_not_fail" ]]; then
            echo "******FAILED repo_update external repo - please resolve and rerun repo_update command"
            exit 1
        fi
    done
    for test_repo in $test_repos; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_test_repo $test_repo $branch $do_not_fail
        retval=$?
        if [[ $retval != 0 && "$do_not_fail" != "do_not_fail" ]]; then
            echo "******FAILED repo_update test repo - please resolve and rerun repo_update command"
            exit 1
        fi
    done

elif [[ "$1" == "install_plugins" ]]; then

    installed_plugins_path=$GEOIPS2_BASEDIR/installed_geoips2_plugins.txt

    for plugin in $internal_plugins $internal_algs $external_repos; do
        echo ""
        echo "Trying plugin '$plugin', checking $installed_plugins_path"
        found="false"
        if [[ -f $installed_plugins_path ]]; then
            while read installed_plugin; do
                if [[ "$installed_plugin" == "$plugin" ]]; then
                    found="true"    
                fi
            done < $installed_plugins_path
            if [[ "$found" == "true" ]]; then
                echo "Plugin $plugin already installed, skipping"
                continue
            fi
        fi
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh install_plugin $plugin
        retval=$?
        if [[ $retval != 0 ]]; then
            echo "******FAILED install_plugins - please resolve and rerun install_plugins command"
            exit 1
        fi
    done

elif [[ "$1" == "uncompress_test_data" ]]; then
    for test_repo in $test_repos; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh uncompress_test_data $test_repo
    done
    for internal_plugin in $internal_plugins; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh uncompress_test_data $internal_plugin
    done

elif [[ "$1" == "recompress_test_data" ]]; then
    for test_repo in $test_repos; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh recompress_test_data $test_repo
    done
    for internal_plugin in $internal_plugins; do
        $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh recompress_test_data $internal_plugin
    done

fi
