# -*- coding: utf-8 -*-

import oerplib
import psycopg2
from psycopg2.extras import DictCursor


source_api = oerplib.OERP('localhost', protocol='xmlrpc', port=4567)
source_user = source_api.login('admin', 'CiscoSystem7970', 'eymimportadores')

destination_api = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)
destination_user = destination_api.login('admin', 'Antonio230', 'eym')

pghost = "127.0.0.1"
user = "odoo"
pwd = "Antonio230"
source_data = psycopg2.connect(dbname='eymimportadores', user='postgres', password='marlboro', host="127.0.0.1", cursor_factory=DictCursor)
destination_data = psycopg2.connect(dbname='eym', user='postgres', password='marlboro', host="127.0.0.1", cursor_factory=DictCursor)
