"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-15
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

aggregation of tests

run with:

env python3 setup.py run_unittest

or:

env python3 setup.py run_pytest
"""


import unittest


class test_module_import(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-14
    """

    def test_module_import(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-14
        """
        import py_fuse_git_bare_fs


class test_scripts_executable(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-04-14
    """

    def test_script_fuse_git_bare_fs_executable(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-14
        """
        import subprocess
        for cmd in ["fuse_git_bare_fs.py -h", "fuse_git_bare_fs.py repo -h",
                    "fuse_git_bare_fs.py tree -h"]:
            cp = subprocess.run(
                [cmd],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, timeout=3, check=True)
            # check at least minimal help output
            self.assertTrue(len(cp.stdout) >= 775)
            # check begin of help output
            self.assertTrue(cp.stdout.startswith(
                b'usage: fuse_git_bare_fs.py'))
            # check end of help output
            self.assertTrue(cp.stdout.endswith(
                b'License: ' +
                b'GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.\n'))


def module(suite):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-14
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    add tests for the module
    """
    print('add tests for the module')
    loader = unittest.defaultTestLoader
    suite.addTest(loader.loadTestsFromTestCase(test_module_import))
    # py_fuse_git_bare_fs.repo_class
    suite.addTest(loader.loadTestsFromName(
        'tests.py_fuse_git_bare_fs_repo_class'))


def scripts(suite):
    """
    :Author: Daniel Mohr
    :Email: daniel.mohr@dlr.de
    :Date: 2021-04-15
    :License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

    add tests for the scripts
    """
    print('add tests for the scripts')
    loader = unittest.defaultTestLoader
    suite.addTest(loader.loadTestsFromTestCase(test_scripts_executable))
    # fuse_git_bare_fs.py repo
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_repo'))
    # fuse_git_bare_fs.py tree
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_tree'))
    # fuse_git_bare_fs.py tree -get_user_list_from_gitolite
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_tree_gitolite'))
    # with git-annex: fuse_git_bare_fs.py tree
    suite.addTest(loader.loadTestsFromName(
        'tests.script_fuse_git_bare_fs_tree_annex'))
