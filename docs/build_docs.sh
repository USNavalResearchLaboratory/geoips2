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

#!/bin/sh
if [ -z "$GEOIPS_OUTDIRS" ]; then
    echo "Must source config_geoips2 - need GEOIPS_OUTDIRS and GEOIPS_VERS defined"
    exit
fi
docpath=`dirname $0`
modulepath=$docpath/../
echo "$docpath"
echo "$modulepath"
rel=$GEOIPS_VERS
vers=`echo $rel | cut -d . -f 1`.`echo $rel | cut -d . -f 2`
echo "$rel $vers"
sphinx-quickstart -p geoips2 -a nrlmry -v $vers -r $rel -l en --master=index \
                --ext-autodoc --ext-doctest --ext-intersphinx --ext-todo --ext-coverage --ext-imgmath --ext-ifconfig \
                --ext-viewcode --ext-githubpages --extensions=sphinx.ext.napoleon \
                --makefile --no-batchfile -m --sep --dot=_ --suffix='.rst' --epub --ext-mathjax $docpath
sphinx-apidoc -o $docpath/source $modulepath
find $modulepath -name '*.rst' -exec echo cp {} $docpath/source \;
find $modulepath -name '*.rst' -exec cp {} $docpath/source \;
cp -rp $docpath/images $docpath/source
cp $docpath/style.css $docpath/source/_static
cp $docpath/layout.html $docpath/source/_templates
# echo "" >> $docpath/source/conf.py
# echo "" >> $docpath/source/conf.py
# echo "def setup(app):" >> $docpath/source/conf.py
# echo "    app.add_css_file('style.css')" >> $docpath/source/conf.py
mv $docpath/source/geoips2_index.rst $docpath/source/index.rst
make -C $docpath html
# make pdf
find $docpath -type d -exec chmod 755 {} \;
find $docpath -type f -exec chmod 644 {} \;
chmod 755 $docpath/build_docs.sh
if [[ "$GEOIPS2_DOCSDIR" != "" ]]; then
    mkdir -p $GEOIPS2_DOCSDIR
    cp -rp $docpath/build/html/ $GEOIPS2_DOCSDIR
fi
