PeeweeMySQLObjetcs
==================

A (soon-to-be) full-featured MySQL database introspection tool to reverse-engineer MySQL databases into Python objects. Uses Peewee from Coleifer.

NOT COMPATIBLE WITH PostgreSQL OR SQLite !
Compatible with Windows, Linux and Mac.
It features foreign key detection and adds support for the ENUM field type.

USAGE
$ peeweemysqlobject login passwd database

RESTRICTION
Logged user must be able to read from the information_schema database.

TODO
* on_update and on_delete actions for foreign keys
* better naming system for "related_name"s

KNOWN ISSUES & TROUBLESHOOTING
* Two fields being Foreign keys on the same table will have the same related_name, and WILL create a collision.
    SOLUTION : This can be resolved by hand, and it's on the TODO list.
* More related to peewee. Any Foreign key will have a "_id" appended. It can create situations like this one : your table has a Foreign key column named tablename_Id, 
    and peewee appends "_id". MySQL will report that "tablename_Id_id" doesn't exist, which is true.
    SOLUTION : None at the moment.