#!python

import os
import sys

from .repo import Repo

source_branch, target_branch = sys.argv[1:]

if __name__ == '__main__':
    repo = Repo(os.getcwd())
    repo.offshored_merge(source_branch, target_branch)