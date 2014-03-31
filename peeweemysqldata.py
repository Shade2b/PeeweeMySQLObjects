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

peewee licence : Copyright (c) 2010 Charles Leifer 
(https://github.com/coleifer/peewee/blob/master/LICENSE)

This module helps convert a database 
to a folder with all its tables as 
Python objects, using peewee.
"""

class BaseFieldStructure():
    def __init__(self, *args, **kwargs):
        self.coma_needed = False
        try:
            self.primary_key = kwargs["primary_key"]
        except:
            self.primary_key = False
        try:
            self.unique = kwargs["unique"]
        except:
            self.unique = False
        try:
            self.default = kwargs["default"]
        except:
            self.default = None
        try:
            self.name = kwargs["name"]
        except:
            print "Error : a field must have a name !"
            exit(1)
    def __str__(self):
        result = ""
        if self.primary_key == True:
            if self.coma_needed == True:
                result += ", "
            result += "primary_key = True"
            self.coma_needed = True
        if self.unique == True:
            if self.coma_needed == True:
                result += ", "
            result += "unique = True"
            self.coma_needed = True
        if self.default is not None:
            if self.coma_needed == True:
                result += ", "
            result += "default = " + str(self.default)
            self.coma_needed = True
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
        try:
            kwargs["default"] = "\""+kwargs["default"]+"\""
        except:
            pass
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = CharField(max_length = %s"%self.max_length
        if self.primary_key == True or self.unique == True:
            result += ", "
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
        result += "max_digits = "+ str(self.max_digits) + ", "
        result += "decimal_places = " + str(self.decimal_places) 
        self.coma_needed = True
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
        if self.values is not None :
            result += "values = " + str(self.values)
            self.coma_needed = True
        result += BaseFieldStructure.__str__(self) + ")"
        return result

class FloatStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        result = self.name + " = FloatField(" + \
            BaseFieldStructure.__str__(self) + ")"
        return result

class ForeignKeyStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):

        self.types = {
            1: "on_delete = \"CASCADE\"",
            2: "on_update = \"SET NULL\"",
            4: "on_update = \"CASCADE\"",
            8: "on_delete = \"SET NULL\"",
            16: "on_delete = \"NO ACTION\"", # on_delete = "RESTRICT"
            32: "on_update = \"NO ACTION\"" # on_update = "RESTRICT"
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
        result = self.name + " = ForeignKeyField("
        if self.reftable is not None:
            result += self.reftable
            if self.related_name is not None:
                result += ", related_name = '" + self.related_name + "'"
            self.coma_needed = True
            result += ", db_column = \"" + self.name + "\""
            for key in self.types:
                if (key & self.constraints) == key:
                    result += ", "+self.types[key]
        result += BaseFieldStructure.__str__(self) + "); "
        return result

class IntegerStructure(BaseFieldStructure):
    def __init__(self, *args, **kwargs):
        BaseFieldStructure.__init__(self, *args, **kwargs)
    def __str__(self):
        return self.name + " = IntegerField(" + \
            BaseFieldStructure.__str__(self) + ")"

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

class StructureList(list):
    foreign_keys = {}

    def __init__(self, *args, **kwargs):
        self.primary_keys = []
        list.__init__(self, *args, **kwargs)

    def append(self, *args, **kwargs):
        for instance in args:
            if not hasattr(instance, "__str__"):
                raise ValueError("Unable to append element "+ str(instance))
            if hasattr(instance, "primary_key") and \
                instance.primary_key == True:
                self.primary_keys.append(instance)
        list.append(self, *args, **kwargs)

    def __getitem__(self, index):
        return list.__getitem__(self, index),  \
            list.__getitem__(self, index).__str__()

    def get_primary_keys(self):
        return [i for i in self if i.primary_key == True]

    def get_foreign_keys(self):
        return [i for i in self 
            if i.__class__.__name__ == "ForeignKeyStructure"]

    def set_up_foreign_keys(self):
        for fkey in self.get_foreign_keys():
            if fkey.related_name in self.foreign_keys:
                self.foreign_keys.update(
                    {fkey.related_name : self.foreign_keys[fkey.related_name] + 1}
                )
                fkey.related_name = fkey.related_name + "_" + \
                    str(self.foreign_keys[fkey.related_name])
            else:
                self.foreign_keys.update({fkey.related_name:0})
