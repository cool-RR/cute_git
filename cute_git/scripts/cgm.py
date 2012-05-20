#!python

import os
import sys

###############################################################################
#                                                                             #
path_to_add = \
         os.path.realpath(os.path.join(os.path.split(__file__)[0], '..', '..'))
if path_to_add not in sys.path:
    sys.path.append(path_to_add)
#                                                                             #
###############################################################################

from cute_git.repo import Repo


source_branch, target_branch = sys.argv[1:]

if __name__ == '__main__':
    repo = Repo(os.getcwd())
    repo.offshored_merge(source_branch, target_branch)