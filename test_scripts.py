# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited. # # #
# # #  # # #
# # # Author: # # #
# # # Naval Research Laboratory, Marine Meteorology Division # # #
# # #  # # #
# # # This program is free software: you can redistribute it and/or modify it under # # #
# # # the terms of the NRLMMD License included with this program.  If you did not # # #
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more # # #
# # # information. # # #
# # #  # # #
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied # # #
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the # # #
# # # included license for more details. # # #

''' Test script for running representative products using data and comparison outputs from geoips_test_data_* '''

import subprocess
import logging
from os.path import basename, join, splitext, dirname, isdir, isfile
LOG = logging.getLogger(__name__)


def is_image(fname):
    ''' Determine if fname is an image file

    Args:
        fname (str) : Name of file to check.

    Returns:
        bool: True if it is an image file, False otherwise.
    '''
    if splitext(fname)[-1] in ['.png', '.jpg', '.jpeg', '.jif']:
        return True
    return False


def is_mtif(fname):
    ''' Check if fname is a metoctiff file

    Args:
        fname (str) : Name of file to check.

    Returns:
        bool: True if it is a metoctiff file, False otherwise.
    '''

    if splitext(fname)[-1] in ['.jif']:
        return True
    return False


def is_text(fname):
    ''' Check if fname is a text file

    Args:
        fname (str) : Name of file to check.

    Returns:
        bool: True if it is a text file, False otherwise.
    '''

    if splitext(fname)[-1] in ['', '.txt', '.text', '.yaml']:
        with open(fname) as f:
            line = f.readline()
        if isinstance(line, str):
            return True
    return False


def is_gz(fname):
    ''' Check if fname is a gzip file

    Args:
        fname (str) : Name of file to check.

    Returns:
        bool: True if it is an image file, False otherwise.
    '''
    if splitext(fname)[-1] in ['.gz']:
        return True
    return False


def gunzip_product(fname):
    ''' gunzip file fname

    Args:
        fname (str) : File to gunzip

    Returns:
        str: Filename of file after gunzipping
    '''
    subprocess.call(['gunzip', fname])
    return splitext(fname)[0]


def get_out_diff_fname(compare_product, output_product):
    from os import makedirs, getenv
    from os.path import exists
    diffdir = join(dirname(compare_product), 'diffs_{0}'.format(getenv('USER')))
    out_diff_fname = join(diffdir, 'diff_'+basename(output_product))
    if not exists(diffdir):
        makedirs(diffdir)
    return out_diff_fname


def images_match(output_product, compare_product, threshold=0.0000001):
    ''' Use imagemagick compare system command to compare currently produced image to correct image

    Args:
        output_product (str) : Current output product
        compare_product (str) : Path to comparison product
        threshold (float) : DEFAULT 0.0000001, valid range 0-1, maximum allowable RMSE for successful comparison
                                NOTE threshold of 0 will often return False for identicaly tiff files (perhaps due to
                                mismatched headers)

    Returns:
        bool: Return True if images match, False if they differ
    '''
    out_diffimg = get_out_diff_fname(compare_product, output_product)

    call_list = ['compare', '-verbose', '-quiet',
                 '-metric', 'rmse',
                 '-dissimilarity-threshold', '{0:0.15f}'.format(threshold),
                 output_product,
                 compare_product,
                 out_diffimg]
    fullimg_retval = subprocess.call(call_list)

    call_list = ['compare', '-verbose', '-quiet',
                 '-metric', 'rmse',
                 '-dissimilarity-threshold', '{0:0.15f}'.format(threshold),
                 '-subimage-search',
                 output_product,
                 compare_product,
                 out_diffimg]

    LOG.info('Running %s', ' '.join(call_list))

    subimg_retval = subprocess.call(call_list)
    if subimg_retval != 0 and fullimg_retval != 0:
        call_list = ['compare', '-verbose', '-quiet',
                     '-metric', 'rmse',
                     '-subimage-search',
                     output_product,
                     compare_product,
                     out_diffimg]
        subprocess.call(call_list)
        LOG.info('    ***************************************')
        LOG.info('    *** BAD Images do NOT match exactly ***')
        LOG.info('    ***************************************')
        return False

    LOG.info('    *************************')
    LOG.info('    *** GOOD Images match ***')
    LOG.info('    *************************')
    # Remove the image if they matched so we don't have extra stuff to sort through.
    from os import unlink as osunlink
    osunlink(out_diffimg)
    return True


def text_match(output_product, compare_product):
    ''' Check if two text files match

    Args:
        output_product (str) : Current output product
        compare_product (str) : Path to comparison product

    Returns:
        bool: Return True if products match, False if they differ
    '''
    retval = subprocess.call(['diff', output_product, compare_product])
    if retval == 0:
        LOG.info('    *****************************')
        LOG.info('    *** GOOD Text files match ***')
        LOG.info('    *****************************')
        return True
    LOG.info('    *******************************************')
    LOG.info('    *** BAD Text files do NOT match exactly ***')
    LOG.info('    *******************************************')
    out_difftxt = get_out_diff_fname(compare_product, output_product)
    with open(out_difftxt, 'w') as fobj:
        subprocess.call(['diff', output_product, compare_product], stdout=fobj)
    return False


def mtif_headers_match(output_product, compare_product):
    ''' Check if mtif headers match on the 2 metoctiff files

    Args:
        output_product (str) : Current output product
        compare_product (str) : Path to comparison product

    Returns:
        (Bool) : Return True if products match, False if they differ
    '''
    head1 = subprocess.check_output([dirname(compare_product)+'/../mtif', '--inFile',  # nosec
                                     compare_product,
                                     '--decode', 'header'])
    head2 = subprocess.check_output([dirname(compare_product)+'/../mtif', '--inFile',  # nosec
                                     output_product,
                                     '--decode', 'header'])
    head1list = str(head1).split('\\n')
    head2list = str(head2).split('\\n')
    if len(head1list) == 1:
        head1list = str(head1).split('\n')
        head2list = str(head2).split('\n')

    import difflib
    diffout = []
    for line in difflib.unified_diff(head1list, head2list):
        if (line[0] in ['+', '-']) and (line[1] not in ['+', '-']):
            if 'szDTG' in line:
                LOG.info('NOTE szDTG is the current date time - NOT including in header diff')
            else:
                diffout += [line]
    # print('\n'.join(diffout))
    if len(diffout) == 0:
        LOG.info('    *******************************')
        LOG.info('    *** GOOD MTIF headers match ***')
        LOG.info('    *******************************')
        return True
    LOG.info('    *********************************************')
    LOG.info('    *** BAD MTIF headers DO NOT match exactly ***')
    LOG.info('    *********************************************')
    out_difftxt = get_out_diff_fname(compare_product, output_product)
    with open(out_difftxt, 'w') as fobj:
        fobj.writelines(diffout)
    return False


def test_product(output_product, compare_product, goodcomps, badcomps, missingtests):
    ''' Test output_product against "good" product stored in "compare_path".

    Args:
        output_product
    '''
    matched_one = False
    if is_image(output_product):
        matched_one = True
        if images_match(output_product, compare_product):
            goodcomps += ['IMAGE {0}'.format(output_product)]
        else:
            badcomps += ['IMAGE {0}'.format(output_product)]

    if is_mtif(output_product):
        matched_one = True
        if mtif_headers_match(output_product, compare_product):
            goodcomps += ['MTIF HEADERS {0}'.format(output_product)]
        else:
            badcomps += ['MTIF HEADERS {0}'.format(output_product)]

    if is_text(output_product):
        matched_one = True
        if text_match(output_product, compare_product):
            goodcomps += ['TEXT {0}'.format(output_product)]
        else:
            badcomps += ['TEXT {0}'.format(output_product)]

    if not matched_one:
        missingtests += [output_product]

    return goodcomps, badcomps, missingtests


def compare_outputs(compare_path, output_products):
    ''' Compare the "correct" imagery found in comparepath with the list of current output_products

    Args:
        comparepath (str) : Path to directory of "correct" products - filenames must match output_products
        output_products (list) : List of strings of current output products, to compare with products in compare_path

    Returns:
        int: Binary code: Good products, bad products, missing products
    '''
    try:
        from shutil import which
        if not which('compare'):
            raise OSError('Imagemagick compare does not exist, install if you want to check outputs')
    except ImportError:
        pass
    badcomps = []
    goodcomps = []
    missingcomps = []
    missingtests = []
    missingproducts = []
    LOG.info('********************************************************************************************')
    LOG.info('********************************************************************************************')
    LOG.info('*** RUNNING COMPARISONS OF KNOWN OUTPUTS IN %s ***', compare_path)
    LOG.info('********************************************************************************************')
    LOG.info('********************************************************************************************')
    LOG.info('')
    from glob import glob

    compare_basenames = [basename(yy) for yy in glob(compare_path+'/*')]
    final_output_products = []

    for output_product in output_products:
        if isdir(output_product):
            # Skip 'diff' output directory
            continue

        LOG.info('********************************************************************************************')
        LOG.info('*** COMPARE  %s ***', basename(output_product))
        LOG.info('********************************************************************************************')

        if is_gz(output_product):
            output_product = gunzip_product(output_product)

        if basename(output_product) in compare_basenames:
            goodcomps, badcomps, missingtests = test_product(output_product,
                                                             join(compare_path, basename(output_product)),
                                                             goodcomps, badcomps, missingtests)
        else:
            missingcomps += [output_product]
        final_output_products += [output_product]
        LOG.info('')
    LOG.info('********************************************************************************************')
    LOG.info('********************************************************************************************')
    LOG.info('*** DONE RUNNING COMPARISONS OF KNOWN OUTPUTS IN %s ***', compare_path)
    LOG.info('********************************************************************************************')
    LOG.info('********************************************************************************************')

    product_basenames = [basename(yy) for yy in final_output_products]
    for compare_product in glob(compare_path+'/*'):
        if isfile(compare_product) and basename(compare_product) not in product_basenames:
            missingproducts += [compare_product]

    from os import makedirs, getenv
    from os.path import exists
    diffdir = join(compare_path, 'diffs_{0}'.format(getenv('USER')))
    if not exists(diffdir):
        makedirs(diffdir)

    for goodcompare in goodcomps:
        LOG.warning('GOODCOMPARE %s', goodcompare)

    for missingproduct in missingproducts:
        LOG.warning('MISSINGPRODUCT no %s in output path from current run', missingproduct)

    for missingcompare in missingcomps:
        LOG.warning('MISSINGCOMPARE no %s in comparepath', missingcompare)

    for missingtest in missingtests:
        LOG.warning('MISSINGTEST no test for file of type  %s', missingtest)

    for badcompare in badcomps:
        LOG.warning('BADCOMPARE %s', badcompare)

    if len(goodcomps) > 0:
        fname_goodcptest = join(diffdir, 'cptest_GOODCOMPARE.txt')
        # print('source {0}'.format(fname_goodcptest))
        with open(fname_goodcptest, 'w') as fobj:
            fobj.write('mkdir {0}/GOODCOMPARE\n'.format(diffdir))
            for goodcomp in goodcomps:
                fobj.write('cp {0} {1}/GOODCOMPARE\n'.format(goodcomp, diffdir))

    if len(missingcomps) > 0:
        fname_cp = join(diffdir, 'cp_MISSINGCOMPARE.txt')
        fname_missingcompcptest = join(diffdir, 'cptest_MISSINGCOMPARE.txt')
        # print('source {0}'.format(fname_missingcompcptest))
        # print('# source {0}'.format(fname_cp))
        with open(fname_cp, 'w') as fobj:
            for missingcomp in missingcomps:
                fobj.write('cp {0} {1}/../\n'.format(missingcomp, diffdir))
        with open(fname_missingcompcptest, 'w') as fobj:
            fobj.write('mkdir {0}/MISSINGCOMPARE\n'.format(diffdir))
            for missingcomp in missingcomps:
                fobj.write('cp {0} {1}/MISSINGCOMPARE\n'.format(missingcomp, diffdir))

    if len(missingproducts) > 0:
        fname_rm = join(diffdir, 'rm_MISSINGPRODUCTS.txt')
        fname_missingprodcptest = join(diffdir, 'cptest_MISSINGPRODUCTS.txt')
        # print('source {0}'.format(fname_missingprodcptest))
        # print('# source {0}'.format(fname_rm))
        with open(fname_rm, 'w') as fobj:
            for missingproduct in missingproducts:
                fobj.write('rm {0}\n'.format(missingproduct))
        with open(fname_missingprodcptest, 'w') as fobj:
            fobj.write('mkdir {0}/MISSINGPRODUCTS\n'.format(diffdir))
            for missingproduct in missingproducts:
                fobj.write('cp {0} {1}/MISSINGPRODUCTS\n'.format(missingproduct, diffdir))

    if len(badcomps) > 0:
        fname_cp = join(diffdir, 'cp_BADCOMPARES.txt')
        fname_badcptest = join(diffdir, 'cptest_BADCOMPARES.txt')
        # print('source {0}'.format(fname_badcptest))
        # print('# source {0}'.format(fname_cp))
        with open(fname_cp, 'w') as fobj:
            for badcomp in badcomps:
                fobj.write('cp {0} {1}/../\n'.format(badcomp, diffdir))
        with open(fname_badcptest, 'w') as fobj:
            fobj.write('mkdir {0}/BADCOMPARES\n'.format(diffdir))
            for badcomp in badcomps:
                fobj.write('cp {0} {1}/BADCOMPARES\n'.format(badcomp, diffdir))

    retval = 0
    if len(badcomps) != 0:
        retval += 1 << 0
        LOG.info('BADCOMPS %s', len(badcomps))
    if len(missingcomps) != 0:
        retval += 1 << 1
        LOG.info('MISSINGCOMPS %s', len(missingcomps))
    if len(missingtests) != 0:
        retval += 1 << 2
        LOG.info('MISSINGTEST %s', len(missingtests))
    if len(missingproducts) != 0:
        LOG.info('MISSINGPRODUCTS %s', len(missingproducts))
        retval += 1 << 3

    LOG.info('retval: %s', retval)
    if retval != 0:
        LOG.info('Nonzero return value indicates error, 4 bit binary code: WXYZ where:')
        LOG.info('    Z (1): BADCOMP: One or more bad comparisons found between comparepath and current run output path')
        LOG.info('    Y (2): MISSINGCOMP: One or more products missing in compare path but existing in current output path')
        LOG.info('    X (4): MISSINGTEST: One or more product type is missing a valid test script')
        LOG.info('    W (8): MISSINGPROD: One or more products exist in comparepath, but missing in current output path')
    
    return retval
