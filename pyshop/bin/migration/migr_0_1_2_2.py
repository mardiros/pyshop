#-*- coding: utf-8 -*-
"""
migrate from 0.7.5 version.

Alter the table release_file, to handle the format "bdist_wheel"

see: http://wheel.readthedocs.org/en/latest/

"""

import os
import sys


from pyshop.models import DBSession

def main(argv=sys.argv):

    session = DBSession()

    # Create temp table
    session.execute("""
    CREATE TABLE classifier__release_new (
            classifier_id integer REFERENCES classifier ON DELETE CASCADE,
            release_id integer REFERENCES release
    );
    """)

    # Copy data to new table
    session.execute("""
    INSERT INTO classifier__release_new (
            classifier_id, release_id)
    SELECT  classifier_id, release_id
    FROM classifier__release;
    """)

    # Swap the tables
    session.execute("""
    DROP TABLE classifier__release;
    """)
    session.execute("""
    ALTER TABLE classifier__release_new RENAME TO classifier__release;
    """)
    session.commit()
