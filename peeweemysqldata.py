#!/usr/bin/env python2.7
#-*-encoding: utf-8-*-
"""
peeweemysqldata.py

Author : BROUTTA MICKAEL
Year : 2014
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

peewee Copyright (c) 2010 Charles Leifer 
(https://github.com/coleifer/peewee/blob/master/LICENSE)

This module helps convert a database 
to a folder with all its tables as 
Python objects, using peewee.
"""

from abc import ABCMeta

class BaseFieldStructure(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.comma_needed = False
        try:
            self.indexes = kwargs["indexes"]
        except:
            self.indexes = None
        try:
            self.primary_key = kwargs["primary_key"]
        except:
            self.primary_key = False
        try:
            self.default = kwargs["default"]
        except:
            self.default = None
        try:
            self.name = kwargs["name"]
        except:
            print "Error : a field must have a name !"
            exit(1)
        self.index = None
        self.unique = None
    def __str__(self):
        result = ""
        result += self.add_parameter(self.primary_key == True,
            "primary_key = True")
        result += self.add_parameter(self.index == True, "index = True")
        result += self.add_parameter(self.index == True and self.unique == False, "unique = True")
        result += self.add_parameter(self.default != None 
            and self.default != "", "default = " + str(self.default))
        # If we want to print the same line again 
        # somewhere in the code, we must reset !
        self.comma_needed = False 
        return result
    def add_parameter(self, parameter, value):
        result = ""
        if parameter == True:
            if self.comma_needed == True:
                result += ", "
            self.comma_needed = True
            result += value
        return result

################################################################################
################################################################################
################################################################################

class BareStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = BareField(" + \
            BaseFieldStructure.__str__() + ")"

class BigIntegerStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = BigIntegerField(" + \
            BaseFieldStructure.__str__(self) + ")"

class BlobStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = BlobField(" + \
            BaseFieldStructure.__str__(self) + ")"

class BooleanStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = BooleanField(" + \
            BaseFieldStructure.__str__(self) + ")"

class CharStructure(BaseFieldStructure):
    def __init__(self, max_length = 255, *args, **kwargs):
        self.max_length = max_length
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = CharField("
        result += self.add_parameter(True, "max_length = %s"%self.max_length)
        result += BaseFieldStructure.__str__(self)
        result += ")"
        return result

class DateStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = DateField(" + \
            BaseFieldStructure.__str__(self) + ")"

class DecimalStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        try:
            self.max_digits = kwargs["max_digits"]
        except:
            self.max_digits = 10
        try:
            self.decimal_places = kwargs["decimal_places"]
        except:
            self.decimal_places = 5
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = DecimalField("
        result += self.add_parameter(True, "max_digits = "+ str(self.max_digits))
        result += self.add_parameter(True, "decimal_places = " + str(self.decimal_places))
        result += BaseFieldStructure.__str__(self) + ")"
        return result

class DoubleStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = DoubleField(" + \
            BaseFieldStructure.__str__(self) + ")" 

class EnumStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        try:
            self.values = kwargs["values"]
        except:
            self.values = None
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = EnumField("
        result += self.add_parameter(self.values is not None, "values = " + str(self.values))
        result += BaseFieldStructure.__str__(self) + ")"
        return result

class FloatStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = FloatField(" + \
            BaseFieldStructure.__str__(self) + ")"
        return result

class IntegerStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = IntegerField("
        result += BaseFieldStructure.__str__(self) + ")"
        return result

class TextStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = TextField(" + \
            BaseFieldStructure.__str__(self) + ")"

class TimeStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = TimeField(" + \
            BaseFieldStructure.__str__(self) + ")"

class SerialStructure(BigIntegerStructure):
    def __init__(self, *args, **kwargs):
        BigIntegerStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return BigIntegerStructure.__str__(self)

class YearStructure(TimeStructure):
    def __init__(self, *args, **kwargs):
        TimeStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return TimeStructure.__str__(self)

################################################################################
################################################################################
################################################################################
class ForeignKeyStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):

        self.types = {
            1: "on_delete = \"CASCADE\"",
            2: "on_update = \"SET NULL\"",
            4: "on_update = \"CASCADE\"",
            8: "on_delete = \"SET NULL\"",
            16: "on_delete = \"NO ACTION\"", # same as on_delete = "RESTRICT"
            32: "on_update = \"NO ACTION\"" # same as on_update = "RESTRICT"
        }

        try:
            self.reftable = kwargs["reftable"]
            try:
                self.related_name = kwargs["related_name"]
            except:
                self.related_name = "NullName"
        except:
            self.reftable = "NullRefTable"
            self.related_name = "NullName"
        try:
            self.constraints = kwargs["constype"]
        except:
            self.constaints = 48
        self.related_name = "fk_" + self.reftable + \
            "_" + self.related_name
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        self.index = False
        self.unique = False
        result = self.name + " = ForeignKeyField("
        if self.reftable is not None:
            result += self.add_parameter(True, self.reftable)
            result += self.add_parameter(self.related_name is not None,
                "related_name = '" + self.related_name + "'")
            result += self.add_parameter(True, "db_column = \"" \
                + self.name + "\"")
            result += self.add_parameter(self.constraints is not None \
                and self.constraints == 0, 
                "on_delete = \"RESTRICT\", on_update = \"RESTRICT\"")
            if self.constraints is not None and self.constraints != 0:
                for key in self.types:
                    result += self.add_parameter((key & self.constraints) == key, self.types[key])
        result += BaseFieldStructure.__str__(self) + ")"
        return result

################################################################################
################################################################################
################################################################################
class StructureList(list):
    foreign_keys = {}
    
    def __init__(self, *args, **kwargs):
        self.primary_keys = []
        self.indexes = {}
        list.__init__(self, *args, **kwargs)

    def append(self, *args, **kwargs):
        for instance in args:
            if not hasattr(instance, "__str__"):
                raise ValueError("Unable to append element "+ instance)
            if hasattr(instance, "primary_key") and \
                instance.primary_key == True:
                self.primary_keys.append(instance)
            if hasattr(instance, "indexes"):
                self.add_indexes(instance.name, instance.indexes)
        list.append(self, *args, **kwargs)

    def __getitem__(self, index):
        return list.__getitem__(self, index),  \
            list.__getitem__(self, index).__str__()

    def add_indexes(self, colname, indexes):
        if indexes is not None:
            for index in indexes:
                if index not in self.indexes:
                    self.indexes.update({index:[]})
                self.indexes[index].append([colname, indexes[index]])

    def get_primary_keys(self):
        return [i for i in self if i.primary_key == True]

    def get_foreign_keys(self):
        return [i for i in self 
            if i.__class__.__name__ == "ForeignKeyStructure"]

    def get_indexes(self):
        return self.indexes

    def set_up(self):
        """
        Sets up anything needed related to index keys, unique index keys
        and foreign keys.
        """
        for fkey in self.get_foreign_keys():
            if fkey.related_name not in self.foreign_keys:
                self.foreign_keys.update({fkey.related_name:0})
            else:
                self.foreign_keys.update(
                    {fkey.related_name : self.foreign_keys[fkey.related_name]+1}
                )
                fkey.related_name = fkey.related_name + "_" + \
                    str(self.foreign_keys[fkey.related_name])
        buff = []
        for index in self.indexes:
            if len(self.indexes[index]) == 1: 
                # Index is on a single column. 
                # If it is, it's not needed to write it in Meta.indexes.
                buff.append(index)
                for column in self:
                    if column.name == self.indexes[index][0][0]:
                        column.index = True
                        column.unique = (self.indexes[index][0][1] == 1)
        for index in buff:
            self.indexes.pop(index)