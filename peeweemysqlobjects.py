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

This module helps convert a database 
to a folder with all its tables as 
Python objects, using peewee.

Used as an executable, it takes three arguments:
    username
    password
    local mysql database name

Foreign Keys are correctly generated only if both
tables are in the same database.
Any FK dependancy module is import'ed.
"""

# IMPORTS #
import ast
import os
import shutil
import sys

# NON-STANDARD IMPORTS #
try:
    import peewee
except ImportError:
    print "Error. This module requires peewee. You can '$ pip install peewee' or get it from http://peewee.readthedocs.org/en/latest/ ."
    exit(1)
    
# GLOBALS #
dbname = None
login = None
passwd = None
db = None

# FUNCTIONS #
###############################################################################
###############################################################################
###############################################################################
def init_db():
    """
    Prepares a connection to your MySQL database.
    """
    global db
    try:
        db = peewee.MySQLDatabase(dbname, user=login, passwd=passwd)
    except Exception, e:
        print e
        db = None
        return
    db.get_conn().set_character_set('utf8')

###############################################################################
###############################################################################
###############################################################################
def write_metadb():
    """
    Creates a file called metadb.py, which contains any database connection related information.
    All subsequent ORM file will import this one to be able to connect. It also enables one more
    data type for peewee.MySQLDatabase to manage : ENUM.
    """
    metadb = """#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-
'''
Meta-informations about the database.
It includes two new types for MySQLDatabase to manage :
    EnumField
    DecimalField
For any peewee.Model subclass, import this module
and set :
    class Meta:
        database=metadb.db
'''
import peewee

dbname = '%s'
login = '%s'
passwd = '%s'

class EnumField(peewee.Field):
    '''
    Enables the enum type for peewee.MySQLDatabase to manage.
    (warning note : http://komlenic.com/244/8-reasons-why-mysqls-enum-data-type-is-evil/ )
    '''
    db_field = 'enum'

    def __init__(self, *args, **kwargs):
        self.enum_values = None
        if "values" in kwargs:
            self.enum_values = kwargs["values"]
        peewee.Field.__init__(self, kwargs)

    def db_value(self, value):
        if self.enum_values is None:
            return str(value)
        if value in self.enum_values or value in range(0,len(self.enum_values)):
            return value
        else:
            return ""
    def python_value(self, value):
        return str(value)

setattr(peewee, "EnumField", EnumField)
peewee.MySQLDatabase.register_fields({'enum': 'ENUM'})

db = peewee.MySQLDatabase(dbname, user=login, passwd=passwd)
db.get_conn().set_character_set('utf8')

"""%(dbname, login, passwd)

    if os.path.isdir(dbname):
        shutil.rmtree(dbname)
    if not os.path.isdir(dbname):
        os.mkdir(dbname)
    # Delete old metadb for new connections
    if os.path.isfile(dbname+"/metadb.py"):
        os.remove(dbname+"/metadb.py")
    # Create the metadb.py file. It contains everything needed to connect to your database.
    # Change MySQLDatabase to whatever suits your needs. You will also have to change the queries below though.
    if not os.path.isfile(dbname+"/metadb.py"):
        openedfile = open(dbname+"/metadb.py", "w+")
        openedfile.write(metadb)
    openedfile.close()

###############################################################################
###############################################################################
###############################################################################
def get_tables():
    """
    Queries the database for its tables names.
    """
    global db
    sql = "SHOW TABLES"
    tables = [str(result[0]) for result in db.execute_sql(sql)]
    return tables

###############################################################################
###############################################################################
###############################################################################
def getcolumns(dbname, tablename, *args, **kwargs):
    """
    Queries the database for fields informations in information_schema.
    Returns the fields from the information_schema you want based on their position.
    Ex : getcolumns(dbname, tablename, 3, 15, 16)
    will return you the fields 3, 15 and 16 (column name, column type, key type)
    List of fields:
    0 : the table catalog (usually u"def")
    1 : the table schema
    2 : the table name
    3 : the column name
    4 : the ordinal position
    5 : the column default value
    6 : Is the column nullable ? Contains u"YES" or u"NO"
    7 : the column data type
    8 : the character maximum length
    9 : the character octet length
    10: the numeric precision
    11: the numeric scale
    12: the datetime precision
    13: the character set name
    14: the collation name
    15: the column type (to not mismatch with column data type)
    16: what type of key is the column (if applicable.)
    17: the "extra" info (like "auto_increment")
    18: the priviliges
    19: the column comment

    Can serve as a generic function inside another module.
    """
    global db
    result = []
    sql = "SELECT * FROM information_schema.columns WHERE table_schema='%s' AND table_name = '%s' ORDER BY table_name, ordinal_position"
    for field in db.execute_sql(sql%(dbname,tablename)):
        buff = ()
        for arg in args:
            try:
                buff += (str(field[arg]),)
            except Exception, e:
                print "Error occured after %s.%s"%(tablename,str(result[-1][0]))
                print e
                print "\nResuming..."
                buff += ("None",)
        result.append(buff)
    return result

###############################################################################
###############################################################################
###############################################################################
def getforeignkey(table, column):
    """
    Retrieves, for a given column, its REFERENCED_TABLE_NAME and REFERENCED_COLUMN_NAME
    under a dictionary form. 
    """
    dbbuff = peewee.MySQLDatabase("information_schema", user=login, passwd=passwd)
    sql = "SELECT `REFERENCED_TABLE_NAME`,`REFERENCED_COLUMN_NAME` \
            FROM KEY_COLUMN_USAGE \
            WHERE `TABLE_NAME`='%s' \
            AND `TABLE_SCHEMA`='%s' \
            AND `COLUMN_NAME`='%s' \
            AND `REFERENCED_COLUMN_NAME` IS NOT NULL"%(table, dbname, column)
    result = dbbuff.execute_sql(sql)
    result = [list(row) for row in result]
    if result == []:
        return None
    else:
        return {column: {"reftable":result[0][0], "refcol":result[0][1]}}

###############################################################################
###############################################################################
###############################################################################
def getenumvalues(tabname,colname):
    """
    Retrieves the possibilities for a given Enum field.
    """
    global db
    sql = "SHOW COLUMNS FROM %s WHERE Field LIKE '%s'"%(tabname, colname)
    result = db.execute_sql(sql)
    result = [row[1] for row in result]
    result = [i.strip("'") for i in result[0].split("enum")[1].lstrip("(").rstrip(")").split(",")]
    return {colname: result}

###############################################################################
###############################################################################
###############################################################################
def write_orm_files(tables):
    """
    Uses the column definitions to generate peewee ORM files.
    """
    possibilities = {
        "Bare": "Bare",
        "bigint": "BigInteger",
        "blob":"Blob",
        "bool":"Boolean",
        "char":"Char",
        "date":"Date",
        "decimal":"Decimal",
        "double":"Double",
        "enum":"Enum",
        "float":"Float",
        "foreignkey":"ForeignKey",
        "int":"Integer",
        "text":"Text",
        "time":"Time",
        "serial":"BigInteger",
        "year":"Time"
    }

    for tablename in tables:
        print "    Processing %s..."%tablename
        primary_key = []
        fields = []
        fieldnames = []
        fieldtypes = []
        foreignkeys = {}
        enum_values = {}
        char_length = {}
        decimals = {}
        unique_key = []
        for result in getcolumns(dbname, tablename, 3, 15, 16): # 3 = colname, 15 = coltype, 16 = Primary / FK ?
            fieldnames.append(result[0])
            in_keys = False
            if result[2] in ["MUL", "PRI"]:
                fk = getforeignkey(tablename, result[0])
                if fk is not None:
                    fieldtypes.append("foreignkey")
                    foreignkeys.update(fk)
                if "PRI" in result[2]:
                    if fk is None:
                        fieldtypes.append("int")
                    primary_key.append(result[0])
            else:
                for key in possibilities:
                    if key in result[1]:
                        in_keys = True
                        fieldtypes.append(key)
                        if "decimal" in key:
                            # Parse the Decimal definition to get digits and precison
                            buff = result[1].split("decimal")[1]
                            decimals.update({result[0]:ast.literal_eval(buff)})
                        if "enum" in key:
                            enum_values.update(getenumvalues(tablename, result[0]))
                        if "char" in key:
                            buff = int(result[1].split("char")[1].lstrip("(").rstrip(")"))
                            char_length.update({result[0]:buff})
                        if "UNI" in result[2] :
                            unique_key.append(result[0])
                        break
                # Uknown data type ? => BareField.
                if in_keys == False:
                    fieldtypes.append("Bare")
                    print "Couldn't determine field type of %s.%s. BareField() selected."%(result[0],result[1])
        basetext = """#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-

import peewee
import metadb
"""
        for tabname in foreignkeys:
            basetext += "import %s\n"%foreignkeys[tabname]["reftable"]
        basetext += """
class %s(peewee.Model):
"""
        openedfile = open(dbname+"/"+tablename+".py", "w+")
        openedfile.write(basetext%tablename)
        # Write all fields
        for index in xrange(len(fieldnames)):
            openedfile.write("    "+fieldnames[index]+" = ")
            openedfile.write("peewee."+possibilities[fieldtypes[index]]+"Field(")

            if "Char" in possibilities[fieldtypes[index]]:
                openedfile.write("max_length = "+str(char_length[fieldnames[index]]))

            if "ForeignKey" in possibilities[fieldtypes[index]]:
                openedfile.write(foreignkeys[fieldnames[index]]["reftable"]+"."+foreignkeys[fieldnames[index]]["reftable"])
                openedfile.write(", related_name = 'fk_"+tablename+"_"+foreignkeys[fieldnames[index]]["reftable"]+"'")

            if "Decimal" in possibilities[fieldtypes[index]]:
                openedfile.write("max_digits = "+str(decimals[fieldnames[index]][0])+", decimal_places = "+str(decimals[fieldnames[index]][1])+", auto_round = True")

            if "Enum" in possibilities[fieldtypes[index]]:
                openedfile.write("values="+str(enum_values[fieldnames[index]]))

            if len(primary_key) == 1 and fieldnames[index] in primary_key:
                if possibilities[fieldtypes[index]] in ["Char", "Decimal", "ForeignKey"]:
                    openedfile.write(", ")
                openedfile.write("primary_key = True")

            if fieldnames[index] in unique_key:
                openedfile.write(", unique = True")
            openedfile.write(")\n")
            
        openedfile.write("""    class Meta:
        database=metadb.db
""")
        
        if len(primary_key) > 1:
            openedfile.write("        primary_key=peewee.CompositeKey(")
            for key in primary_key:
                openedfile.write("'"+key+"'")
                if key != primary_key[-1]:
                    openedfile.write(", ")
            openedfile.write(")\n")
        openedfile.close()

###############################################################################
###############################################################################
###############################################################################
def write_module_init():
    if os.path.isfile(dbname+"/__init__.py"):
        os.remove(dbname+"/__init__.py")
    index = """#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-

__all__=[
"""
    files = os.listdir("./"+dbname)
    for item in files:
        if ".pyc" in item:
            continue
        index += "    '"+item.split(".")[0]+"'"
        if item not in files[-1]:
            index += ",\n"

    index += "\n]\n"
    f = open(dbname+"/__init__.py", "w+")
    f.write(index)
    f.close()

###############################################################################
###############################################################################
###############################################################################
if __name__ == "__main__":
    print "MAIN"
    if len(sys.argv) < 4:
        print "Usage : peeweemysqlobjects.py login password dbname"
        exit(1)

    dbname = sys.argv[3]
    login = sys.argv[1]
    passwd = sys.argv[2]
    
    print "INIT DB"
    init_db()
    print "WRITE METADB"
    write_metadb()
    print "RETRIEVE TABLES"
    tables = get_tables()
    print "WRITE ORM FILES"
    write_orm_files(tables)
    print "WRITE MODULE INIT"
    write_module_init()
    print "DONE"
