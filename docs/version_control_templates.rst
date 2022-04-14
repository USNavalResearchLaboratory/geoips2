 | # # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
 | # # # 
 | # # # Author:
 | # # # Naval Research Laboratory, Marine Meteorology Division
 | # # # 
 | # # # This program is free software: you can redistribute it and/or modify it under
 | # # # the terms of the NRLMMD License included with this program.  If you did not
 | # # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
 | # # # information.
 | # # # 
 | # # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
 | # # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 | # # # included license for more details.

Pull Request Template
=====================

.. code-block:: bash
    [ The following information should be included in each Pull Request. ]
    [ Include information specific to the current repo within the pull request. ]
    [ Main testing and installation instructions will be included within the ticket, ]
    [ so the pull request should just include information about what changed within the current repo. ]
    
    # Testing Instructions
    GEOIPS2-XX 
    <Link to ticket with testing instructions, or note that no exhaustive testing is required,>
    <or include testing instructions directly here if appropriate>
    
    # Summary
    <2-3 sentence summary/bullets of the changes that were made to meet the requirements of the ticket>
    <these will likely be copied and pasted into the CHANGELOG during the next version release, so make them concise and informative!>

    # Output
    <Optional output demonstrating functionality - command line or imagery output>
    
    # Individual Commits
    Leave the auto-populated commit messages at the bottom of the pull request text.


Ticket Resolution Template
==========================

.. code-block:: bash
    [ The following information should be included as a comment on the ticket once all repos are ready for approval/merge ]
    [ There may be more than one related repo - they should all be approved / merged as a group ]
    [ Once all ticket requirements are met, update the ticket with the following information ]
    [ Then all associated pull requests can be approved and merged ]
    
    This functionality is ready for review and approval - all tests successfully returned 0.
    
    ### Associated pull requests that should be merged with this approval are linked to ticket
    Navigate to each associated pull request, review changes, and approve individually.
    None will be merged until ALL are approved.
    
    ### Summary
    <2-3 sentence summary of the changes that were made to meet the requirements of the ticket>
    
    ### Instructions to set up required packages from scratch
    * [ https://<url>/repos/<package1>/browse/README.md ]
    * [ https://<url>/repos/<package2>/browse/README.md ]
    * [ https://<url>/repos/<package3>/browse/README.md ]
    
    
    ### Obtain the correct branch and reinstall all associated repos:
    ```
    $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_source_repo <package1> feature/[GEOIPS2-XX-DESCRIPTION]
    $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_source_repo <package2> feature/[GEOIPS2-XX-DESCRIPTION]
    $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_source_repo <package3> feature/[GEOIPS2-XX-DESCRIPTION]
    
    $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_test_repo <testrepo1> feature/[GEOIPS2-XX-DESCRIPTION]
    $GEOIPS2_PACKAGES_DIR/geoips2/setup_geoips2.sh update_test_repo <testrepo2> feature/[GEOIPS2-XX-DESCRIPTION]
        
    $GEOIPS2_BASEDIR/geoips2_packages/<package1>/setup_<package1>.sh install_<package1>
    $GEOIPS2_BASEDIR/geoips2_packages/<package2>/setup_<package2>.sh install_<package2>
    ```
      
    ### Obtain correct versions of all dependencies for consistent test outputs
    ```
    $GEOIPS2/setup_geoips2.sh install_geoips2
    $GEOIPS2/setup_geoips2.sh install_cartopy_offlinedata
    ```
      
    
    ### Test the new functionality
    ```
    $GEOIPS2_BASEDIR/geoips2_packages/<package1>/tests/test_all.sh
    $GEOIPS2_BASEDIR/geoips2_packages/<package2>/tests/scripts/<script>.sh
    [ Include output indicating 0 returns ]
    ```
