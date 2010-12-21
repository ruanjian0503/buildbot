# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import os
import sqlalchemy
from sqlalchemy.schema import MetaData
from twisted.python import log

class RealDatabaseMixin(object):
    """
    A class that sets up a real database for testing.  This sets self.db_url to
    the URL for the database.  By default, it specifies an in-memory SQLite
    database, but if the BUILDBOT_TEST_DB_URL environment variable is set, it
    will use the specified database, being careful to clean out *all* tables in
    the database before and after the tests are run - so each test starts with
    a clean database.
    """
    def _clean_database(self):
        log.msg("cleaning database %s" % self.db_url)
        engine = sqlalchemy.create_engine(self.db_url)

        # get a list of all of the tables..
        meta = MetaData()
        meta.reflect(bind=engine)

        # and drop them!
        for table in reversed(meta.sorted_tables):
            log.msg("  dropping table %s" % table)
            table.drop(engine)

        engine.dispose()

    def setUpRealDatabase(self):
        memory = 'sqlite://'
        self.db_url = os.environ.get('BUILDBOT_TEST_DB_URL', 'sqlite:///%s' % (os.path.abspath('test.db'))) ### XXX TEMPORARY until sqlalchemification is complete
        self._using_memory_db = (self.db_url == memory)

        if not self._using_memory_db:
            self._clean_database()

    def tearDownRealDatabase(self):
        if not self._using_memory_db:
            self._clean_database()