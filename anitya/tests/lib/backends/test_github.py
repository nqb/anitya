# -*- coding: utf-8 -*-
#
# Copyright © 2014  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

'''
anitya tests for the custom backend.
'''

import unittest

import anitya.lib.backends.github as backend
from anitya.db import models
from anitya.lib.exceptions import AnityaPluginException
from anitya.tests.base import DatabaseTestCase, create_distro


BACKEND = 'GitHub'


class GithubBackendtests(DatabaseTestCase):
    """ Github backend tests. """

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(GithubBackendtests, self).setUp()

        create_distro(self.session)
        self.create_project()

    def create_project(self):
        """ Create some basic projects to work with. """
        project = models.Project(
            name='fedocal',
            homepage='https://github.com/fedora-infra/fedocal',
            version_url='fedora-infra/fedocal',
            backend=BACKEND,
        )
        self.session.add(project)
        self.session.commit()

        project = models.Project(
            name='foobar',
            homepage='https://github.com/foo/bar',
            version_url='foobar/bar',
            backend=BACKEND,
        )
        self.session.add(project)
        self.session.commit()

        project = models.Project(
            name='pkgdb2',
            homepage='https://github.com/fedora-infra/pkgdb2',
            backend=BACKEND,
        )
        self.session.add(project)
        self.session.commit()

    def test_get_version(self):
        """ Test the get_version function of the github backend. """
        pid = 1
        project = models.Project.get(self.session, pid)
        exp = '0.14'
        obs = backend.GithubBackend.get_version(project)
        self.assertEqual(obs, exp)

        pid = 2
        project = models.Project.get(self.session, pid)
        self.assertRaises(
            AnityaPluginException,
            backend.GithubBackend.get_version,
            project
        )

        pid = 3
        project = models.Project.get(self.session, pid)
        exp = '2.3'
        obs = backend.GithubBackend.get_version(project)
        self.assertEqual(obs, exp)

    def test_get_versions(self):
        """ Test the get_versions function of the github backend. """
        pid = 1
        project = models.Project.get(self.session, pid)
        exp = [
            u'v0.9.3',
            u'0.10', u'0.11', u'0.11.1', u'0.12',
            u'0.13', u'0.13.1', u'0.13.2', u'0.13.3',
            u'0.14',
        ]
        obs = backend.GithubBackend.get_ordered_versions(project)
        self.assertEqual(obs, exp)

        pid = 2
        project = models.Project.get(self.session, pid)
        self.assertRaises(
            AnityaPluginException,
            backend.GithubBackend.get_versions,
            project
        )

        pid = 3
        project = models.Project.get(self.session, pid)
        exp = [
            u'1.33.0', u'1.33.2', u'1.33.3',
            u'2.0', u'2.0.1', u'2.0.2', u'2.0.3', u'2.1', u'2.2', u'2.3'
        ]
        obs = backend.GithubBackend.get_ordered_versions(project)
        self.assertEqual(obs, exp)

    def test_plexus_utils(self):
        """ Regression test for issue #286 """
        project = models.Project(
            version_url='codehaus-plexus/plexus-archiver',
            version_prefix='plexus-archiver-',
        )
        version = backend.GithubBackend().get_version(project)
        self.assertEqual(u'3.3', version)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(GithubBackendtests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
