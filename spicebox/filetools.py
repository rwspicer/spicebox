"""
FileTools
---------
Tools for general files
"""


import os
import tarfile
import glob


def to_tarball(file_or_dir, archive_name, compresson='gz'):
    """add a file to a tarball archive

    Parameters
    ----------
    file_or_dir:
        path to compress
    archive_name: path
        path to output tarball
    copression: string optional, default 'gz'
        compression type to use 
    """

    file = os.path.split(file_or_dir)[1]

    with tarfile.open(archive_name, "w:%s" % compresson) as tar:
        tar.add(file_or_dir, file)


def tarball_all_subdirecttories(
        root, filter='*', outdir = None, outfile_tag = '', copression='gz',
        verbose = False
    ):
    """compress all of the subdirectories in a given directory in to individual
    tarballs.

    Parameters
    ----------
    root: path
        path to subdirectories to compress
    filter: string optional default, '*' 
        filter wild card for glob.glob used to construct list of files to 
        compress
    outdir: path optional, default none
        If none save in current director
    outfile_tag: string optional, default ''
        tag for output files
    copression: string optional, default 'gz'
        compression type to use 
    verbose: bool optional, default False

    """

    if outdir is None:
        outdir = root

    ext = '.tar.%s' % copression

    
    root = os.path.join(root,filter)
    
    files = glob.glob(root)
    
    outfile_tag = ('%s-' % outfile_tag) if outfile_tag != '' else '' 
    for pth in files:
        # print(pth)
        if not os.path.isdir(pth):
            continue

        name = os.path.split(pth)[1]
        tar = os.path.join(outdir, '%s%s%s' % (outfile_tag, name, ext))
        if verbose:
            print('Compressing %s -> %s' % (pth, tar))
 
        to_tarball(pth, tar)

def _tarball_helper_(filter_func, root, 
        filter='*', outdir = None, outfile_tag = '', copression='gz',
        verbose = False ):
    """abstraction of common code for fillter_all_subdirectories, 
    and fileter_all_files. 

    Parameters
    ----------
    filter_func: function
        takes a path, and returns a bool
    root: path
        path to subdirectories to compress
    filter: string optional default, '*' 
        filter wild card for glob.glob used to construct list of files to 
        compress
    outdir: path optional, default none
        If none save in current director
    outfile_tag: string optional, default ''
        tag for output files
    copression: string optional, default 'gz'
        compression type to use 
    verbose: bool optional, default False

    """
    if outdir is None:
        outdir = root

    ext = '.tar.%s' % copression

    root = os.path.join(root,filter)
    
    files = glob.glob(root)
    
    outfile_tag = ('%s-' % outfile_tag) if outfile_tag != '' else '' 
    for pth in files:
        if not filter_func(pth):
            continue

        name = os.path.split(pth)[1]
        tar = os.path.join(outdir, '%s%s%s' % (outfile_tag, name, ext))
        if verbose:
            print('Compressing %s -> %s' % (pth, tar))
 
        to_tarball(pth, tar)
    

def tarball_all_subfiles(
        root, filter='*', outdir = None, outfile_tag = '', copression='gz',
        verbose = False
    ):
    """compress all of the sub-files in a given directory in to individual
    tarballs.

    Parameters
    ----------
    root: path
        path to subdirectories to compress
    filter: string optional default, '*' 
        filter wild card for glob.glob used to construct list of files to 
        compress
    outdir: path optional, default none
        If none save in current director
    outfile_tag: string optional, default ''
        tag for output files
    copression: string optional, default 'gz'
        compression type to use 
    verbose: bool optional, default False

    """
    _tarball_helper_(
        os.path.isfile, root, filter, outdir , outfile_tag, copression, verbose 
    )


def tarball_all_subdirecttories(
        root, filter='*', outdir = None, outfile_tag = '', copression='gz',
        verbose = False
    ):
    """compress all of the subdirectories in a given directory in to individual
    tarballs.

    Parameters
    ----------
    root: path
        path to subdirectories to compress
    filter: string optional default, '*' 
        filter wild card for glob.glob used to construct list of files to 
        compress
    outdir: path optional, default none
        If none save in current director
    outfile_tag: string optional, default ''
        tag for output files
    copression: string optional, default 'gz'
        compression type to use 
    verbose: bool optional, default False

    """
    _tarball_helper_(
        os.path.isdir, root, filter, outdir , outfile_tag, copression, verbose 
    )


def tarball_all(
        root, filter='*', outdir = None, outfile_tag = '', copression='gz',
        verbose = False
    ):
    """compress all of the sub-files in a given directory in to individual
    tarballs.

    Parameters
    ----------
    root: path
        path to subdirectories to compress
    filter: string optional default, '*' 
        filter wild card for glob.glob used to construct list of files to 
        compress
    outdir: path optional, default none
        If none save in current director
    outfile_tag: string optional, default ''
        tag for output files
    copression: string optional, default 'gz'
        compression type to use 
    verbose: bool optional, default False

    """
    if verbose:
        print("Adding directories to tarball...")
    tarball_all_subdirecttories(
        root, filter, outdir, outfile_tag, copression, verbose
    )
    if verbose:
        print("Adding files to tarball...")
    tarball_all_subfiles(root, filter, outdir, outfile_tag, copression, verbose)
