"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-29
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

tests the class RepoClass in the module py_fuse_git_bare_fs

You can run this file directly:

  env python3 py_fuse_git_bare_fs_repo_class.py

Or you can run only one test, e. g.:

  env python3 py_fuse_git_bare_fs_repo_class.py \
    PyFuseGitBareFsRepoClass.test_repo_class
"""


import os
import subprocess
import tempfile
import unittest


class PyFuseGitBareFsRepoClass(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2021-03-29
    """

    def test_repo_class(self):
        """
        :Author: Daniel Mohr
        :Date: 2021-04-29

        This test creates a repo, put some files in and
        check how it is handled by py_fuse_git_bare_fs.repo_class.
        """
        # pylint: disable=too-many-statements
        # pylint: disable = bad-option-value, import-outside-toplevel
        from py_fuse_git_bare_fs.repo_class import RepoClass
        serverdir = 'server'
        clientdir = 'client'
        mountpointdir = 'mountpoint'
        reponame = 'repo1'
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                repo = RepoClass(
                    os.path.join(tmpdir, serverdir, reponame), b'master')
            # prepare test environment
            for dirpath in [serverdir, clientdir, mountpointdir]:
                os.mkdir(os.path.join(tmpdir, dirpath))
            subprocess.run(
                ['git init --bare ' + reponame],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, serverdir),
                timeout=3, check=True)
            subprocess.run(
                ['git clone ../' + os.path.join(serverdir, reponame)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir),
                timeout=3, check=True)
            subprocess.run(
                ['echo "a">a; echo "b">b; ln -s a l; mkdir d; echo "abc">d/c;'
                 'git add a b l d/c; git commit -m init; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # run tests
            repo = RepoClass(
                os.path.join(tmpdir, serverdir, reponame), b'master')
            self.assertEqual(set(repo.readdir('/')),
                             {'.', '..', 'a', 'b', 'd', 'l'})
            file_status = dict()
            for filename in ['/a', '/b', '/l', '/d', '/d/c']:
                file_status[filename] = repo.getattr(filename)
            for filename in ['/d']:
                self.assertEqual(file_status[filename]['st_mode'], 16893)
                self.assertEqual(file_status[filename]['st_size'], 4096)
            for filename in ['/a', '/b']:
                self.assertEqual(file_status[filename]['st_mode'], 33204)
                self.assertEqual(file_status[filename]['st_size'], 2)
            for filename in ['/l']:
                self.assertEqual(file_status[filename]['st_mode'], 41471)
                self.assertEqual(file_status[filename]['st_size'], 1)
            for filename in ['/d/c']:
                self.assertEqual(file_status[filename]['st_mode'], 33204)
                self.assertEqual(file_status[filename]['st_size'], 4)
            for filename in ['/a', '/b', '/l', '/d', '/d/c']:
                self.assertEqual(file_status[filename]['st_uid'], os.geteuid())
                self.assertEqual(file_status[filename]['st_gid'], os.getegid())
            for filename in ['/a', '/b']:
                file_handler = repo.open(filename, 'r')
                data = repo.read(filename, None, 0, file_handler)
                repo.release(filename, file_handler)
                self.assertEqual('/' + data.decode(), filename + '\n')
            for filename in ['/l']:
                file_handler = repo.open(filename, 'r')
                data = repo.read(filename, None, 0, file_handler)
                repo.release(filename, file_handler)
                self.assertEqual(data, b'a')  # link target
                file_handler = repo.open(filename, 'r')
                data = repo.read('/' + data.decode(), None, 0, file_handler)
                repo.release(filename, file_handler)
                self.assertEqual(data, b'a\n')
            for filename in ['/d/c']:
                file_handler = repo.open(filename, 'r')
                data = repo.read(filename, None, 0, file_handler)
                repo.release(filename, file_handler)
                self.assertEqual(data, b'abc\n')
            try:
                # pylint: disable = bad-option-value, import-outside-toplevel
                import fusepy
            except ModuleNotFoundError:
                # pylint: disable = bad-option-value, import-outside-toplevel
                import fuse as fusepy
            with self.assertRaises(fusepy.FuseOSError):
                file_status = repo.getattr('/foo')
            # adapt data
            subprocess.run(
                ['ln -s d/c foo; git add foo; git commit -m foo; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests: readdir
            self.assertEqual(set(repo.readdir('/')),
                             {'.', '..', 'a', 'b', 'd', 'l', 'foo'})
            # adapt data
            subprocess.run(
                ['ln -s d/c bar; git add bar; git commit -m bar; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests: getattr
            file_status = repo.getattr('/bar')
            self.assertEqual(file_status['st_mode'], 41471)
            self.assertEqual(file_status['st_size'], 3)
            self.assertEqual(file_status['st_uid'], os.geteuid())
            self.assertEqual(file_status['st_gid'], os.getegid())
            file_handler = repo.open(filename, 'r')
            data = repo.read('/bar', None, 0, file_handler)
            self.assertEqual(data, b'd/c')  # link target
            data = repo.read('/' + data.decode(), None, 0, file_handler)
            repo.release(filename, file_handler)
            self.assertEqual(data, b'abc\n')
            # adapt data
            subprocess.run(
                ['echo abc..xyz>baz; '
                 'git add baz; git commit -m baz; git push'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=os.path.join(tmpdir, clientdir, reponame),
                timeout=3, check=True)
            # further tests:
            file_handler = repo.open(filename, 'r')
            data = repo.read('/baz', None, 0, file_handler)
            repo.release(filename, file_handler)
            self.assertEqual(data, b'abc..xyz\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
