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
    session.execute("""
    CREATE TABLE release_file_new (
            id INTEGER NOT NULL,
            created_at DATETIME,
            release_id INTEGER NOT NULL,
            filename VARCHAR(200) NOT NULL,
            md5_digest VARCHAR(50),
            size INTEGER,
            package_type VARCHAR(13) NOT NULL,
            python_version VARCHAR(25),
            url VARCHAR(1024),
            downloads INTEGER,
            has_sig BOOLEAN,
            comment_text TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY(release_id) REFERENCES release (id),
            UNIQUE (filename),
            CHECK (package_type IN ('sdist', 'bdist_egg', 'bdist_msi',
                                    'bdist_dmg', 'bdist_rpm', 'bdist_dumb',
                                    'bdist_wininst', 'bdist_wheel'))
            CHECK (has_sig IN (0, 1))
    );
    """)
    session.execute("""
    INSERT INTO release_file_new (
            id, created_at, release_id, filename,
            md5_digest, size, package_type, python_version,
            url, downloads, has_sig, comment_text)
    SELECT  id, created_at, release_id, filename,
            md5_digest, size, package_type, python_version,
            url, downloads, has_sig, comment_text
    FROM release_file;
    """)
    session.execute("""
    DROP TABLE release_file;
    """)
    session.execute("""
    ALTER TABLE release_file_new RENAME TO release_file;
    """)
    session.commit()
