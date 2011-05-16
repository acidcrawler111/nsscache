#!/usr/bin/python
#
# Copyright 2007 Google Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Unit tests for nss_cache/update/base.py."""

__author__ = ('vasilios@google.com (V Hoffman)',
              'jaq@google.com (Jamie Wilkinson)')


import os
import shutil
import tempfile
import time
import unittest

import mox

from nss_cache import config
from nss_cache.update import base


class TestUpdater(mox.MoxTestBase):
  """Unit tests for the Updater class."""

  def setUp(self):
    super(TestUpdater, self).setUp()
    self.workdir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.workdir)
    super(TestUpdater, self).tearDown()

  def testTimestampDir(self):
    """We read and write timestamps to the specified directory."""
    updater = base.Updater(config.MAP_PASSWORD, self.workdir, {})
    self.updater = updater
    update_time = time.gmtime(1199149400)  # epoch
    modify_time = time.gmtime(1199149200)

    updater.WriteUpdateTimestamp(update_time)
    updater.WriteModifyTimestamp(modify_time)

    update_stamp = updater.GetUpdateTimestamp()
    modify_stamp = updater.GetModifyTimestamp()

    self.assertEqual(update_time, update_stamp,
                     msg=('retrieved a different update time than we stored: '
                          'Expected: %r, observed: %r' %
                          (update_time, update_stamp)))
    self.assertEqual(modify_time, modify_stamp,
                     msg=('retrieved a different modify time than we stored: '
                          'Expected %r, observed: %r' %
                          (modify_time, modify_stamp)))

  def testTimestampDefaultsToNone(self):
    """Missing or unreadable timestamps return None."""
    updater = base.Updater(config.MAP_PASSWORD, self.workdir, {})
    self.updater = updater
    update_stamp = updater.GetUpdateTimestamp()
    modify_stamp = updater.GetModifyTimestamp()

    self.assertEqual(None, update_stamp,
                     msg='update time did not default to None')
    self.assertEqual(None, modify_stamp,
                     msg='modify time did not default to None')

    # touch a file, make it unreadable
    update_file = open(updater.update_file, 'w')
    modify_file = open(updater.modify_file, 'w')
    update_file.close()
    modify_file.close()
    os.chmod(updater.update_file, 0000)
    os.chmod(updater.modify_file, 0000)

    update_stamp = updater.GetUpdateTimestamp()
    modify_stamp = updater.GetModifyTimestamp()

    self.assertEqual(None, update_stamp,
                     msg='unreadable update time did not default to None')
    self.assertEqual(None, modify_stamp,
                     msg='unreadable modify time did not default to None')

  def testTimestampInTheFuture(self):
    """Timestamps in the future are turned into now."""
    updater = base.Updater(config.MAP_PASSWORD, self.workdir, {})
    expected_time = time.gmtime(1)
    update_time = time.gmtime(3600+1)
    update_file = open(updater.update_file, 'w')
    updater.WriteUpdateTimestamp(update_time)
    self.mox.StubOutWithMock(time, 'gmtime')
    time.gmtime().AndReturn(expected_time)
    self.mox.ReplayAll()
    self.assertEqual(expected_time, updater.GetUpdateTimestamp())
