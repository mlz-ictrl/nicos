#!/bin/sh
BASEDIR=${BASEDIR:-"$PWD/nicos-stack"}
MAKEOPTS="-j5"

# fetch sources into a separate directory
mkdir -p $BASEDIR/download
cd $BASEDIR/download
WGET="wget -c --no-check-certificate"
$WGET http://www.python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
$WGET https://trac.frm2.tum.de/externalpackages/Python-2.7.6.tar.xz
$WGET https://trac.frm2.tum.de/externalpackages/PyQt-x11-gpl-4.10.1.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/PyQwt-5.2.0.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/sip-4.14.6.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/QScintilla-gpl-2.7.1.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/qt-everywhere-opensource-src-4.8.5.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/virtualenv-1.11.1.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/pip-1.5.1.tar.gz
$WGET https://trac.frm2.tum.de/externalpackages/setuptools-2.1.tar.gz

# check downloaded files
md5sum -c <<EOF
4678c2ae5cce4e9234c3923d7dcb32f0  pip-1.5.1.tar.gz
e5973c4ec0b0469f329bc00209d2ad9c  PyQt-x11-gpl-4.10.1.tar.gz
fcd6c6029090d473dcc9df497516eae7  PyQwt-5.2.0.tar.gz
bcf93efa8eaf383c98ed3ce40b763497  Python-2.7.6.tar.xz
da8939b5679a075e30c6632e54dc5abf  QScintilla-gpl-2.7.1.tar.gz
1864987bdbb2f58f8ae8b350dfdbe133  qt-everywhere-opensource-src-4.8.5.tar.gz
2044725530450d0517393882dc4b7508  setuptools-2.1.tar.gz
d6493b9f0a7911566545f694327314c4  sip-4.14.6.tar.gz
7875c2d8c2075571abe5e727449af4d8  virtualenv-1.11.1.tar.gz
EOF
if [ $? -ne 0 ]; then
    echo "some files failed md5check, please redownload"
    exit 1;
fi;

# create build dir and start building
mkdir -p $BASEDIR/build

#build python and a minimal set of required extra packages
cd $BASEDIR/build
tar xJf $BASEDIR/download/Python-2.7.6.tar.xz
cd Python-2.7.6/
./configure --prefix=$BASEDIR/python-2.7.6
make $MAKEOPTS && make install
cd $BASEDIR/build
tar xzf $BASEDIR/download/setuptools-2.1.tar.gz
cd setuptools-2.1/
../../python-2.7.6/bin/python setup.py install
cd $BASEDIR/build
tar xzf $BASEDIR/download/pip-1.5.1.tar.gz
cd pip-1.5.1/
../../python-2.7.6/bin/python setup.py install
cd $BASEDIR/build
tar xzf $BASEDIR/download/virtualenv-1.11.1.tar.gz
cd virtualenv-1.11.1/
../../python-2.7.6/bin/python setup.py install

cd $BASEDIR/build
# get numpy as well
$BASEDIR/python-2.7.6/bin/pip install numpy


#build Qt and Qt-related packages
cd $BASEDIR/build
tar xzf $BASEDIR/download/qt-everywhere-opensource-src-4.8.5.tar.gz
cd qt-everywhere-opensource-src-4.8.5/
# silence licence agreement
yes|./configure -prefix $BASEDIR/qt-4.8.5 -prefix-install -nomake examples -nomake demos -silent -opensource
(make $MAKEOPTS && make install) || (gmake $MAKEOPTS && gmake install)


cd $BASEDIR/build
tar xzf $BASEDIR/download/QScintilla-gpl-2.7.1.tar.gz
cd QScintilla-gpl-2.7.1/
cd Qt4Qt5/
../../../qt-4.8.5/bin/qmake
make $MAKEOPTS && make install
cd ../../
export PATH=$BASEDIR/python-2.7.6/bin/:$BASEDIR/qt-4.8.5/bin/:$PATH


# PyQt and needed helpers
cd $BASEDIR/build
tar xzf $BASEDIR/download/sip-4.14.6.tar.gz
cd sip-4.14.6/
../../python-2.7.6/bin/python configure.py -b ../../python-2.7.6/bin/ -d ../../python-2.7.6/lib/python2.7/site-packages/ -e ../../python-2.7.6/include/ -v ../../python-2.7.6/share/sip
make $MAKEOPTS && make install
cd $BASEDIR/build
tar xzf $BASEDIR/download/PyQt-x11-gpl-4.10.1.tar.gz
cd PyQt-x11-gpl-4.10.1/
../../python-2.7.6/bin/python configure.py -q ../../qt-4.8.5/bin/qmake --confirm-license
make $MAKEOPTS && make install


#PyQwt (supplies Qwt as well)
cd $BASEDIR/build
tar xzf $BASEDIR/download/PyQwt-5.2.0.tar.gz
cd PyQwt-5.2.0/
make $MAKEOPTS 4 && make install-4
cd ../


#generate a virtualenv for nicos
cd $BASEDIR
virtualenv -p $BASEDIR/python-2.7.6/bin/python --system-site-packages --prompt=NICOS nicosvenv


#to use the virtualenv:
# sh: . $BASEDIR/nicosvenv/bin/activate
# (t)csh): source $BASEDIR/nicosvenv/bin/activate.csh
