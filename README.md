PeeweeMySQLObjects
==================

A (soon-to-be) full-featured MySQL database introspection tool to reverse-engineer (convert) MySQL databases into Python objects.
It uses Peewee from Coleifer (get it from https://github.com/coleifer/peewee or http://peewee.readthedocs.org/en/latest/)

Even though Pwiz exists, I coded this converter before knowing about it. I proceeded to add support for ENUM, foreign keys and unique indexes.

COMPATIBILITY
* Not compatible with PostgreSQL or SQLite ! MySQL only.
* Works best with the InnoDB engine. Works with the MyISAM engine.
* Compatible with Windows, Linux and Mac. 

USAGE

peeweemysqlobjects.py [-h] [-v] [-u LOGIN] [-p PASSWD] [-a ADDR]
                             [--port PORT]
                             databasename

Utility tool to convert a MySQL database into peewee orm files.

positional arguments:
  databasename

optional arguments:
  -h, --help            show this help message and exit
  -v                    prints version
  -u LOGIN, --user LOGIN
                        login
  -p PASSWD, --passwd PASSWD
                        password
  -a ADDR, --addr ADDR  ip address of remote server (default localhost)
  --port PORT           port of remote server (default 3306)

RESTRICTION
* Logged user must be able to read from the information_schema database.
* Logged user must have the PROCESS privilege to query the INNODB_SYS_FOREIGN table, if applicable (ie if there are foreign key constraints.)

TODO
* Send your ideas at broutta.mickael(at)gmail.com !

WHAT'S DONE
* The FOREIGN KEY "_id" issue has been fixes. [v 0.1.0.5]
* Support for indexes (non-uniques and uniques, for all columns, even if they are part of multiple indexes) [v. 0.1.1.1]
* better naming system for "related_name"s
    * related_names will now have an underscore followed by a number appended starting with the second occurence of a foreign key on the same foreign table (eg. "fk_reftable_refcol_num").
* clean-up of global variables (dbname, login, passwd). They can't be used when importing parts of the module like "from peeweemysqlobjects import get_tables"
    * Clean-up done, no more glaring global.
* on_update and on_delete actions for foreign keys
* Reorder column definitions in generated files. They are stored and sorted in a dict, so they come out in another order than what's given by the ordinal_position.
* Added support for remote databases.
* Added better argument handling.

KNOWN ISSUES & TROUBLESHOOTING
* None at the moment.