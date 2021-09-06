#!/usr/bin/env python
"""
==========================
FindFiles.py
==========================

The FindFiles.py integrates several interfaces to perform ...
"""

import os, fnmatch
import re
from os.path import join, getsize



def Find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            result = os.path.join(root, name)
            result.sort()
            return result
        # end if
    # end loop
# end def


def FindAll(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    result.sort()
    return result
# end def


def FindPat(pattern, path):
    result = []
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    result.sort()
    return result
# end def

def FindFileDirs(pattern, path):
    result = []
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(root)
    result.sort()
    return result
# end def

def FindDirOfFiles(pattern_arr, path):
    root_vec = []

    for root, dirs, files in os.walk(path, topdown=True):
        found_all = True
        for pattern in pattern_arr:
            found_pat = False
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    found_pat = True
            if found_pat is False:
                found_all = False
        if found_all is True:
            root_vec.append(root)
    root_vec.sort()
    return root_vec
# end def

def FindDirs(pattern, path):
    result = []
    folders = [f.path for f in os.scandir(path) if f.is_dir()]
    for name in folders:
        if pattern in name:
            result.append(name)
        # end if
    # end loop
    result.sort()
    return result
# end def

# find('*.txt', '/path/to/dir')