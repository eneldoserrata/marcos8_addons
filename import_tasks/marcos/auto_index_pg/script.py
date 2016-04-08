# -*- coding: utf-8 -*-
from __future__ import absolute_import
import contextlib
import psycopg2




__all__ = ['savepoint', 'create_missing_indexes']


@contextlib.contextmanager
def savepoint(cr, name, quiet=False):
    # http://www.postgresql.org/docs/current/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    if '"' in name:
        name = name.replace('"', '""')
    cr.execute('SAVEPOINT "%s";' % name)
    try:
        yield
    except Exception:
        cr.execute('ROLLBACK TO "%s";' % name)
        if not quiet:
            raise
    finally:
        cr.execute('RELEASE "%s";' % name)


def create_missing_indexes(cr):
    """Create indexes for all the foreign keys (m2o, o2m, ...)."""
    # List the missing indexes:
    #  * ignore the FK on "res_users" (create_uid, write_uid, ...)
    #  * skip the relations having less than 2 entries in the source or
    #    destination table
    cr.execute("""
    SELECT conrelid::regclass, attname
      FROM pg_constraint
      JOIN pg_class c ON (c.oid = conrelid)
      JOIN pg_class fc ON (fc.oid = confrelid)
      JOIN pg_attribute ON (attrelid = conrelid AND attnum = ANY(conkey))
     WHERE contype = 'f'
       AND confrelid != 'res_users'::regclass
       AND c.reltuples > 1 AND fc.reltuples > 1
       AND NOT EXISTS (
      SELECT 1 FROM pg_index
       WHERE indrelid = conrelid AND indkey[0] = conkey[1]);
    """)
    statistics = {'done': [], 'errors': []}
    count = 0
    for tbl, col in cr.fetchall():
        try:
            with savepoint(cr, 'create_index'):
                cr.execute('CREATE INDEX "%(tbl)s_%(col)s_fki" '
                           'ON "%(tbl)s" ("%(col)s")' % {'tbl': tbl, 'col': col})
            statistics['done'].append((tbl, col))
        except Exception:
            statistics['errors'].append((tbl, col))
        count  += 1
        print count

    print statistics



username = 'odoo' #the user
pwd = 'Antonio230'      #the password of the user
dbname = 'rim'    #the database

conn = psycopg2.connect(dbname=dbname, user=username, password=pwd, host="127.0.0.1")
cur = conn.cursor()
create_missing_indexes(cur)