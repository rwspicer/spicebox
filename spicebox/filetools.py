"""
FileTools
---------
Tools for general files
"""


import os
import tarfile


def compress_tar_gz(file_or_dir, archive_name):

    path, file = os.path.split(file_or_dir)

    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(file_or_dir, file)


        




