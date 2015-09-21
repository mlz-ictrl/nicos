#!/bin/sh
BASEDIR=${BASEDIR:-"$PWD/nicos-stack"}
MAKEOPTS="-j5"

PYVERSIONMAJOR=${PYVERSIONMAJOR:-2}

dofetch=1
dobuild=1
domkvenv=1

buildpython=1
buildqt=1
buildpyqt=1
buildpyqwt=1

function usage() {
  echo "install a nicos stack"
  echo "options:"
  echo
  echo "  -p | --pythonver (2|3)  install a python 2 or 3"
  echo "  -b | --basedir basedir  basedir (default: $BASEDIR)"
  echo "  -v | --verbose          more verbose output"
  echo "  --nofetch               do not fetch files"
  echo "  --nobuild               do not build"
  echo "  --nomkvenv              do not create a venv"
  echo " partial building: assumes that previous part have been built already"
  echo "  --nopython              do not build python"
  echo "  --noqt                  do not build Qt/QScintilla"
  echo "  --nopyqt                do not build PyQt/SIP"
  echo "  --nopyqwt               do not build PyQWT/QWT"
  echo
  echo "  -h | --help             this help"
  echo
  echo "enviroment vars : PYVERSIONMAJOR BASEDIR"
 }

while [ "$1" != "" ]; do
    case $1 in
        -p | --pythonver )        shift
                                PYVERSIONMAJOR=$1
                                ;;
        -v | --verbose )        set -v
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        -b | --basedir )        shift
                                BASEDIR=$1
                                ;;
        --nofetch )             dofetch=0
                                ;;
        --nobuild )             dobuild=0
                                ;;
        --nopython )            buildpython=0
                                ;;
        --noqt )                buildqt=0
                                ;;
        --nopyqt )              buildpyqt=0
                                ;;
        --nopyqwtn )            buildpyqwt=0
                                ;;
        --nomkvenv )            domkvenv=0
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done


if [ $PYVERSIONMAJOR -eq 3 ] ; then
   PYVERSION="3.4.2"
else
   PYVERSION="2.7.6"
fi



PYEXEC=python${PYVERSION:0:1}
PYBASEVER=`echo $PYVERSION|cut -d. -f1-2`


function fetch
{
# fetch sources into a separate directory
mkdir -p $BASEDIR/download
cd $BASEDIR/download
WGET="wget -c --no-check-certificate"
$WGET https://forge.frm2.tum.de/externalpackages/Python-2.7.6.tar.xz
$WGET https://forge.frm2.tum.de/externalpackages/Python-3.4.2.tar.xz
$WGET https://forge.frm2.tum.de/externalpackages/PyQt-x11-gpl-4.10.1.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/PyQwt-5.2.0.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/pyqwt5.2.1-frm2.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/sip-4.14.6.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/QScintilla-gpl-2.7.1.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/qt-everywhere-opensource-src-4.8.5.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/virtualenv-13.1.2.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/pip-7.1.2.tar.gz
$WGET https://forge.frm2.tum.de/externalpackages/setuptools-18.3.2.tar.gz

# check downloaded files
md5sum -c <<EOF
3823d2343d9f3aaab21cf9c917710196  pip-7.1.2.tar.gz
e5973c4ec0b0469f329bc00209d2ad9c  PyQt-x11-gpl-4.10.1.tar.gz
fcd6c6029090d473dcc9df497516eae7  PyQwt-5.2.0.tar.gz
bcf93efa8eaf383c98ed3ce40b763497  Python-2.7.6.tar.xz
36fc7327c02c6f12fa24fc9ba78039e3  Python-3.4.2.tar.xz
da8939b5679a075e30c6632e54dc5abf  QScintilla-gpl-2.7.1.tar.gz
1864987bdbb2f58f8ae8b350dfdbe133  qt-everywhere-opensource-src-4.8.5.tar.gz
d30c969065bd384266e411c446a86623  setuptools-18.3.2.tar.gz
d6493b9f0a7911566545f694327314c4  sip-4.14.6.tar.gz
b989598f068d64b32dead530eb25589a  virtualenv-13.1.2.tar.gz
4856155c5c4fa53401154881da021a62  pyqwt5.2.1-frm2.tar.gz
EOF
if [ $? -ne 0 ]; then
    echo "some files failed md5check, please redownload"
    exit 1;
fi;

}


function build_python
{
#build python and a minimal set of required extra packages
cd $BASEDIR/build
tar xJf $BASEDIR/download/Python-$PYVERSION.tar.xz
cd Python-$PYVERSION/
./configure --prefix=$BASEDIR/python-$PYVERSION
make $MAKEOPTS && make install

cd $BASEDIR/build
tar xzf $BASEDIR/download/setuptools-18.3.2.tar.gz
cd setuptools-18.3.2/
$BASEDIR/python-$PYVERSION/bin/$PYEXEC setup.py install

cd $BASEDIR/build
tar xzf $BASEDIR/download/pip-7.1.2.tar.gz
cd pip-7.1.2/
$BASEDIR/python-$PYVERSION/bin/$PYEXEC setup.py install

cd $BASEDIR/build
tar xzf $BASEDIR/download/virtualenv-1.11.2.tar.gz
cd virtualenv-13.1.2/
$BASEDIR/python-$PYVERSION/bin/$PYEXEC setup.py install

cd $BASEDIR/build
# get numpy as well
$BASEDIR/python-$PYVERSION/bin/pip install numpy
}

function build_qt
{
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
$BASEDIR/qt-4.8.5/bin/qmake
make $MAKEOPTS && make install
}


function build_pyqt
{
# PyQt and needed helpers
cd $BASEDIR/build
tar xzf $BASEDIR/download/sip-4.14.6.tar.gz
cd sip-4.14.6/
$BASEDIR/python-$PYVERSION/bin/$PYEXEC configure.py -b $BASEDIR/python-$PYVERSION/bin/ -d $BASEDIR/python-$PYVERSION/lib/python$PYBASEVER/site-packages/ -e $BASEDIR/python-$PYVERSION/include/ -v $BASEDIR/python-$PYVERSION/share/sip
make $MAKEOPTS && make install


cd $BASEDIR/build
tar xzf $BASEDIR/download/PyQt-x11-gpl-4.10.1.tar.gz
cd PyQt-x11-gpl-4.10.1/
$BASEDIR/python-$PYVERSION/bin/$PYEXEC configure.py -q $BASEDIR/qt-4.8.5/bin/qmake --confirm-license
make $MAKEOPTS && make install
}

function build_pyqwt
{
#PyQwt (supplies Qwt as well)
cd $BASEDIR/build
if [ $PYVERSIONMAJOR -eq 3 ] ;then
    tar xzf $BASEDIR/download/pyqwt5.2.1-frm2.tar.gz
    cd pyqwt5/
    sed -i -e 's/python/python3/' GNUMakefile
    make qwt-5.2.1
    ln -s qwt-5.2.1 qwt-5.2
    make $MAKEOPTS 4 && make install-4
else
    tar xzf $BASEDIR/download/PyQwt-5.2.0.tar.gz
    cd pyqwt5
    make $MAKEOPTS 4 && make install-4
fi
}

function build
{
# create build dir and start building
mkdir -p $BASEDIR/build

if [ $buildpython -eq 1 ]; then
  build_python
fi
export PATH=$BASEDIR/python-$PYVERSION/bin/:$PATH

if [ $buildqt -eq 1 ]; then
  build_qt
fi

export PATH=$BASEDIR/qt-4.8.5/bin/:$PATH

if [ $buildpyqt -eq 1 ]; then
  build_pyqt
fi

if [ $buildpyqwt -eq 1 ]; then
  build_pyqwt
fi
}

function mkvenv
{
#generate a virtualenv for nicos
cd $BASEDIR
virtualenv -p $BASEDIR/python-$PYVERSION/bin/$PYEXEC --system-site-packages --prompt="NICOS\(py-$PYBASEVER\) " nicosvenv-py$PYBASEVER

echo
echo
echo "  To use the virtualenv:"
echo
echo "    sh: . $BASEDIR/nicosvenv-py$PYBASEVER/bin/activate"
echo "    tcsh/csh: source $BASEDIR/nicosvenv-py$PYBASEVER/bin/activate.csh"
echo
}

if [ $dofetch -eq 1 ] ; then
    fetch
fi
if [ $dobuild -eq 1 ] ; then
    build
fi
if [ $domkvenv -eq 1 ] ; then
    mkvenv
fi
