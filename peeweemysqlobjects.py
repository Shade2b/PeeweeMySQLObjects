#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-
"""
peeweemysqlobjects.py

Author : BROUTTA MICKAEL
Year : 2013/2014
Contact : broutta.mickael@gmail.com

LICENCE
The MIT License (MIT)

Copyright (c) 2014 BROUTTA MICKAEL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

peewee licence : Copyright (c) 2010 Charles Leifer 
(https://github.com/coleifer/peewee/blob/master/LICENSE)

This module helps convert a database 
to a folder with all its tables as 
Python objects, using peewee.

Foreign Keys are correctly generated only if both
related tables are in the same database.
Any FK dependancy module is import'ed in the generated files.
"""

# IMPORTS #
# import argparse # imported in if __name__ == "__main__"
import ast
import logging
import os
import re
import shutil
import time
# import sys # imported in if __name__ == "__main__"

# NON-STANDARD IMPORTS #
try:
    import peewee
except ImportError:
    logging.error("Error. This module requires peewee.  \
        You can '$ pip install peewee' or get it from \
        http://peewee.readthedocs.org/en/latest/ .")
    exit(1)
    
# LOCAL IMPORTS #
try:
    from peeweemysqldata import *
except ImportError, i:
    logging.error("Error importing data structures (peeweemysqldata) : %s"%str(i))
    exit(1)

# FUNCTIONS #
################################################################################
################################################################################
################################################################################
def init_db(login, passwd, dbname, addr, port):
    """
    Prepares a connection to your MySQL database.
    """
    db = None
    try:
        if addr is None:
            db = peewee.MySQLDatabase(dbname, user=login, passwd=passwd)
        else:
            db = peewee.MySQLDatabase(dbname, user=login, passwd=passwd, 
                host=addr, port=port)
    except Exception, e:
        logging.error(e)
        db = None
        return db
    db.get_conn().set_character_set('utf8')
    return db

################################################################################
################################################################################
################################################################################
def get_version():
    return "0.1.1.4"

################################################################################
################################################################################
################################################################################
def write_metadb(login, passwd, dbname, addr, port):
    """
    Creates a file called __metadb__.py, which contains 
    any database connection related information.
    All subsequent ORM file will import this one to 
    be able to connect. It also enables one more
    data type for peewee.MySQLDatabase to manage : ENUM.
    """
    metadb = """#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-
'''
Meta-informations about the database.
It includes a new types for MySQLDatabase to manage :
    EnumField
'''
import peewee
from peewee import *

dbname = '%s'
login = '%s'
passwd = '%s'
"""%(dbname, login, passwd)

    if addr is not None:
        metadb += """addr = '%s'
port = %d
"""%(addr,port)

    metadb += """
class EnumField(Field):
    '''
    Enables the enum type for peewee.MySQLDatabase to manage.
    (warning note : 
        http://komlenic.com/244/8-reasons-why-mysqls-enum-data-type-is-evil/ )
    '''
    db_field = 'enum'
    def __init__(self, *args, **kwargs):
        self.enum_values = None
        if "values" in kwargs:
            self.enum_values = kwargs["values"]
        Field.__init__(self, kwargs)

    def db_value(self, value):
        if self.enum_values is None:
            return str(value)
        if value in self.enum_values or value in range(len(self.enum_values)):
            return value
        else:
            return ""
    def python_value(self, value):
        return str(value)

setattr(peewee, "EnumField", EnumField)
MySQLDatabase.register_fields({'enum': 'ENUM'})
db = MySQLDatabase(dbname, user=login, passwd=passwd"""

    if addr is not None:
        metadb += """, host=addr, port=port"""
    metadb += """)
db.get_conn().set_character_set('utf8')

class BaseModel(Model):
    class Meta:
        database = db

"""

    
    if os.path.isdir(dbname):
        shutil.rmtree(dbname)
        time.sleep(1)
    if not os.path.isdir(dbname):
        os.mkdir(dbname)
    filename = dbname+"/__metadb__.py"
    # Create the __metadb__.py file. 
    # It contains everything needed to connect to your database
    # using the credentials you provided.
    if not os.path.isfile(filename):
        openedfile = open(filename, "w+")
        openedfile.write(metadb)
    openedfile.close()

################################################################################
################################################################################
################################################################################
def getcolumnsinfo(db, dbname, tablename):
    """
    Queries the database for fields informations in information_schema.
    """
    result = []
    sql = "SELECT column_name, column_default, column_type, column_key \
        FROM information_schema.columns WHERE table_schema='%s' \
        AND table_name = '%s' ORDER BY table_name, ordinal_position"
    for field in db.execute_sql(sql%(dbname,tablename)):
        """
        buff = []
        for arg in args:
            try:
                buff.append()
            except Exception, e:
                if len(result) == 0:
                    logging.warning("Error occured on the first column.")
                else:
                    logging.warning("Error occured after %s.%s"%(
                        tablename,
                        str(result[-1][3])
                    ))
                logging.warning(e)
                logging.warning("\nResuming...")
                buff.update({arg:"None"})
        """
        result.append(field)
    return result

################################################################################
################################################################################
################################################################################
def getforeignkey(db, dbname, table, column):
    """
    Retrieve, for a given column, its REFERENCED_TABLE_NAME and
    REFERENCED_COLUMN_NAME under a dictionary form. 
    """
    sql = "SELECT `REFERENCED_TABLE_NAME`,`REFERENCED_COLUMN_NAME` \
            FROM information_schema.KEY_COLUMN_USAGE \
            WHERE `TABLE_NAME`='%s' \
            AND `TABLE_SCHEMA`='%s' \
            AND `COLUMN_NAME`='%s' \
            AND `REFERENCED_COLUMN_NAME` IS NOT NULL"%(table, dbname, column)
    result = db.execute_sql(sql)
    result = [list(row) for row in result]
    if result == []:
        return None
    else:
        sql = "SELECT `TYPE` FROM information_schema.`INNODB_SYS_FOREIGN` \
            WHERE `FOR_NAME` LIKE \"%s/%s\" \
            AND `REF_NAME` LIKE \"%s/%s\""%(
                dbname, table,
                dbname, result[0][0]
            )
        constype = None
        for row in db.execute_sql(sql):
            constype = row[0]
        return {column: {
            "reftable":result[0][0],
            "refcol":result[0][1],
            "type" : constype}}

################################################################################
################################################################################
################################################################################
def getindexes(db, dbname, tablename, columnname):
    sql = "SHOW INDEX FROM %s FROM %s WHERE Column_name='%s'"%(
        tablename,
        dbname,
        columnname
    )
    result = {}
    for row in db.execute_sql(sql):
        if "PRIMARY" not in row[2]: # Can't have primaries show up in indexes...
            result.update({row[2]:row[1]})
    if result == {}:
        return None
    return result

################################################################################
################################################################################
################################################################################
def getenumvalues(tabname,colname, db):
    """
    Retrieve the possibilities for a given Enum field.
    """
    sql = "SHOW COLUMNS FROM %s WHERE Field LIKE '%s'"%(tabname, colname)
    result = db.execute_sql(sql)
    result = [row[1] for row in result]
    result = [i.strip("'") for i in result[0].split("enum")[1]
        .strip("()").split(",")]
    return {colname: result}

################################################################################
################################################################################
################################################################################
def write_orm_files(db, dbname, login, passwd, nofk):
    """
    Use the column definitions to generate peewee ORM files.
    """
    # This array is used to know which definition to use depending on column
    # definition.
    possibilities = {
        "Bare" : BareStructure,
        "bigint" : BigIntegerStructure,
        "blob" : BlobStructure,
        "bool" : BooleanStructure,
        "char" : CharStructure,
        "date" : DateStructure,
        "decimal" : DecimalStructure,
        "double" : DoubleStructure,
        "enum" : EnumStructure,
        "float" : FloatStructure,
        "foreignkey" : ForeignKeyStructure if nofk is True else IntegerStructure,
        "int" : IntegerStructure,
        "text": TextStructure,
        "time": TimeStructure,
        "serial": SerialStructure,
        "year": YearStructure
    }

    for tablename in db.get_tables():
        logging.info("    Processing %s..."%tablename)

        fieldlist = StructureList()

        columns = getcolumnsinfo(db, dbname, tablename)
        for result in columns:
            indexes = None
            fieldtype = None
            primary_key = False
            unique = False
            default = None
            max_digits = 10
            decimal_places = 5
            max_length = 255
            reftable = None
            related_name = None
            enum_values = None
            decimals = ()
            in_keys = False
            constype = 48
            #index = {}
            indexes = getindexes(db, dbname, tablename, result[0])
            if result[3] in ["MUL", "PRI"]:
                fk = getforeignkey(db, dbname, tablename, result[0])
                if fk is not None:
                    fieldtype = "foreignkey"
                    reftable = fk[result[0]]["reftable"]
                    related_name = fk[result[0]]["refcol"]
                    constype = fk[result[0]]["type"]
                if "PRI" in result[3]:
                    if fk is None:
                        fieldtype = "int"
                    primary_key = True
            if fieldtype is None:
                for key in possibilities:
                    if key in result[2]:

                        in_keys = True
                        fieldtype = key

                        if "decimal" in key:
                            # Parse the Decimal definition to 
                            # get digits and precison
                            buff = result[2].split("decimal")[1]
                            decimals = ast.literal_eval(buff)
                            max_digits = decimals[0]
                            decimal_places = decimals[1]

                        if "enum" in key:
                            enum_values = getenumvalues(
                                tablename, 
                                result[0], 
                                db)[result[0]]

                        if "char" in key:
                            max_length = int(result[2].split("char")[1]
                                .lstrip("(").rstrip(")"))

                        if "UNI" in result[3] :
                            unique = True
                        break
                # Uknown data type ? => BareField.
                if in_keys == False:
                    fieldtype = "Bare"
                    logging.warning("Couldn't determine field type of %s.%s."%(
                        result[0],
                        result[2]
                    ))
                    logging.warning("BareField() selected.")
            default = None
            try:
                default = ast.literal_eval(result[1])
            except:
                default = result[1]
            fieldlist.append(
                possibilities[fieldtype](
                    name = result[0], 
                    primary_key = primary_key,
                    indexes = indexes,
                    values = enum_values, 
                    default = default, 
                    max_digits = max_digits, 
                    decimal_places = decimal_places, 
                    max_length = max_length, 
                    reftable = reftable, 
                    related_name = related_name,
                    constype = constype)
            )
        # Set up foreign keys and indexes
        fieldlist.set_up()
        # Write the file out !
        basetext = """#!/usr/bin/env python
#-*-encoding: utf-8-*-

from peewee import *
from __metadb__ import *
"""
        for fkey in fieldlist.get_foreign_keys():
            # Update basetext with needed imports for foreign keys
            basetext += "from %s import %s\n"%(fkey.reftable, fkey.reftable)
        basetext += """
class %s(BaseModel):
"""
        openedfile = open(dbname+"/"+tablename+".py", "w+")
        openedfile.write(basetext%tablename)
        # Write all fields
        for field in fieldlist:
            line = str(field)
            if "primary_key = True" in line \
                and len(fieldlist.get_primary_keys()) > 1:
                re.sub("(,)( )*(primary_key = True)(,)*( )*", "", line)
            openedfile.write("    %s\n"%line)
        
        if len(fieldlist.get_primary_keys()) > 1:
            openedfile.write("    class Meta:\n")
            openedfile.write("        primary_key = CompositeKey(")
            keys = fieldlist.get_primary_keys()
            for index in xrange(len(keys)):
                openedfile.write("'"+keys[index].name+"'")
                if index != len(keys) - 1:
                    openedfile.write(", ")
            openedfile.write(")\n")
        indexes = fieldlist.get_indexes()
        if len(indexes) > 0:
            if len(fieldlist.get_primary_keys()) == 1:
                openedfile.write("    class Meta:\n")
            openedfile.write("        indexes = (\n")
            for index in indexes:
                openedfile.write("            ((")
                unique = None
                for field in indexes[index]:
                    openedfile.write("'%s'"%field[0])
                    unique = field[1]
                    if field != indexes[index][-1]:
                        openedfile.write(", ")
                openedfile.write("), %s) # %s\n"%("False" if unique == True else "True", index))
            openedfile.write("        )\n")
        openedfile.close()

################################################################################
################################################################################
################################################################################
def write_module_init(dbname):
    """
    List all .py files under the dbname directory, and write them out
    in the __init__.py file.
    """
    filename = dbname+"/__init__.py"
    if os.path.isfile(filename):
        os.remove(filename)
    index = """#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-

__all__=[
"""
    files = os.listdir("./"+dbname)
    for item in files:
        if ".pyc" in item:
            continue
        index += "    '%s'"%item.split(".")[0]
        if item not in files[-1]:
            index += ",\n"

    index += "\n]\n"
    f = open(filename, "w+")
    f.write(index)
    f.close()

################################################################################
################################################################################
################################################################################
if __name__ == "__main__":
    import argparse
    import sys

    argparser = argparse.ArgumentParser(description="Utility tool to \
        convert a MySQL database into Peewee ORM files.")
    argparser.add_argument('-v', action='store_true', help="prints version")
    argparser.add_argument('-u', '--user', dest='login', nargs=1, help="login")
    argparser.add_argument('-p', '--passwd', nargs=1, help="password")
    argparser.add_argument('-a', '--addr', help="ip address of remote server (default localhost)")
    argparser.add_argument('--port', help="port of remote server (default 3306)")
    argparser.add_argument("--nofk", action='store_true', help="Transform foreign key columns to plain integer columns. Useful for reference cycles.")
    argparser.add_argument('databasename')

    args = argparser.parse_args()
    if args.v == True:
        print "peeweemysqlobjects version %s."%get_version()
        print "Developped and tested with MySQL 5.6.12."
        exit(0)
    
    dbname = args.databasename
    login = args.login[0]
    passwd = args.passwd[0]
    addr = args.addr
    if args.port is None:
        port = 3306
    else:
        port = int(args.port)
    if args.nofk is None:
        nofk = False
    else:
        nofk = True

    db = init_db(login, passwd, dbname, addr, port)
    if db is not None:
        write_metadb(login, passwd, dbname, addr, port)
        write_orm_files(db, dbname, login, passwd, nofk)
        write_module_init(dbname)
        exit(0)

    exit(1)