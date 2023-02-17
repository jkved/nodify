# from ast import Try
from multipledispatch import dispatch
from pathlib import Path
from functools import partial
import argparse
import sys


# Method for input argument processing if initial data is passed by path to file
def argument_input(new_args, test_mode=False):
    if not test_mode:
        parser = argparse.ArgumentParser(prog="templateIO",
                                         description="""This program reads an SQL-type data structure from a file or as
                                          pipeline input. After that, the code prints it in command line or output file.
                                          \nFor file input use optional argument -f.\nFor stream input use like this: 
                                          \"cat txt.txt | py main.py\".""",
                                         )
        parser.add_argument('flow',
                            nargs="?",
                            help="see description for input types",
                            type=argparse.FileType('r'),
                            default=(None if sys.stdin.isatty() else sys.stdin),
                            )
        parser.add_argument("-f",
                            "--filepath",
                            action="store",
                            help="path to file containing input table",
                            default=None,
                            metavar="",
                            )
        parser.add_argument("-o",
                            "--output", 
                            action="store", 
                            help="name of the file for output to be printed",
                            metavar="",
                            default=None,
                            )
        parser.add_argument("-d",
                            "--delimiter",
                            help="""sets the default delimiter for imported data structure (current - \",\"), 
                                    must be passed in between \"\"""",
                            metavar="",
                            default="|",
                            )

        args = parser.parse_args()
    else:
        args = new_args
    if args.flow is None:
        try:
            target_file = Path(args.filepath)
        except TypeError:
            # print(e)
            print("Filepath value not assigned. Try using -f \"filepath\"")
            raise SystemExit(1)
        if not target_file.exists():
            print("Input file does not exist. Provide a valid input file")
            raise SystemExit(1)

    return args


# These are node-type classes for creating objects for data
class Node:
    name: str
    title: str


class Database(Node):
    pass


class Table(Node):
    pass


class DataType:
    name: str


class Column(Node):
    dtype: DataType


class Integer(DataType):
    pass


class String(DataType):
    pass


# This is a class for main implementation
class Restruct:
    db_name_index = 0
    tbl_name_index = 1
    col_name_index = 2
    col_dtype_index = 3
    all_title_index = 4

    def __init__(self, args) -> None:
        self.filepath = args.filepath
        self.delimiter = args.delimiter
        self.output_file = args.output
        self.flow = args.flow

        self.col_len = [0, 0, 0, 0, 0]
        self.obj_list = []

    # Dispatched load functions for 3 types of nodes
    @dispatch(Database, list)
    def load(self, obj, vals) -> None:
        obj.name = vals[self.db_name_index]
        obj.title = vals[-1]

        self.col_len[self.db_name_index] = max(self.col_len[self.db_name_index], len(obj.name))
        self.col_len[self.all_title_index] = max(self.col_len[self.all_title_index], len(obj.title))

    @dispatch(Table, list)
    def load(self, obj, vals) -> None:
        obj.name = vals[self.tbl_name_index]
        obj.title = vals[-1]

        self.col_len[self.tbl_name_index] = max(self.col_len[self.tbl_name_index], len(obj.name))
        self.col_len[self.all_title_index] = max(self.col_len[self.all_title_index], len(obj.title))

    @dispatch(Column, list)
    def load(self, obj, vals) -> None:
        obj.name = vals[self.col_name_index]
        obj.title = vals[-1]
        if vals[self.col_dtype_index].casefold() == "integer":
            obj.dtype = Integer()
            obj.dtype.name = vals[self.col_dtype_index]
        elif vals[self.col_dtype_index].casefold() == "string":
            obj.dtype = String()
            obj.dtype.name = vals[self.col_dtype_index]

        self.col_len[self.col_name_index] = max(self.col_len[self.col_name_index], len(obj.name))
        self.col_len[self.col_dtype_index] = max(self.col_len[self.col_dtype_index], len(obj.dtype.name))
        self.col_len[self.all_title_index] = max(self.col_len[self.all_title_index], len(obj.title))

    # Method to enable two types of inputs (from file or as stream)
    def input_method(self, filename) -> str:
        if self.flow is None:
            return filename.readline()
        else:
            return sys.stdin.readline()

    # In case wrong delimiter is selected
    def determine_delimiter(self, header) -> str:
        try_delims = [",", "|", "." "\t", "_"]
        for delim in try_delims:
            if len(header.split(delim)) >= 3:
                print("Delimiter has been changed from \""+self.delimiter+"\" to \""+delim+"\".")
                return delim
        print("No appropriate delimiter has been selected or found. Try setting it with -d \"delim\"")
        raise SystemExit(1)

    # Main algorithm to restructure input data to node-type objects
    def restruct_data_arr(self) -> None:
        # Selects appropriate input type
        if self.flow is None:
            filename = open(self.filepath)
        else:
            filename = None

        # Making sure that data goes first instead of header and that correct delimiter was chosen
        header = self.input_method(filename)
        # in the least delimiter counts case (for database), at least three values are present
        if len(header.split(self.delimiter)) < 3:
            self.delimiter = self.determine_delimiter(header)

        if all(header.split(self.delimiter)) != "":
            content_line = self.input_method(filename)
        else:
            content_line = header

        # Reading single line at a time and converting to node
        while content_line != "":
            content_line = [elem.strip() for elem in content_line.split(self.delimiter)]
        
            if content_line[0] != "":
                self.load(node := Database(), content_line)
            elif content_line[1] != "":
                self.load(node := Table(), content_line)
            else:
                self.load(node := Column(), content_line)

            self.obj_list.append(node)
            content_line = self.input_method(filename)
        
        if self.flow is None:
            filename.close()
    
    # Utility methods for output
    @dispatch(Database)
    def obj_attr_to_list(self, obj) -> list:
        return list([obj.name, "", "", "", obj.title])

    @dispatch(Table)
    def obj_attr_to_list(self, obj) -> list:
        return list(["", obj.name, "", "", obj.title])

    @dispatch(Column)
    def obj_attr_to_list(self, obj) -> list:
        return list(["", "", obj.name, obj.dtype.name, obj.title])

    # Command line or output file print method
    def table_output_cl(self) -> None:
        if self.output_file is not None:
            filename = open(self.output_file, "w+")
            foo = filename.write
        else:
            foo = partial(print, end="")

        for obj in self.obj_list:
            line_vals = self.obj_attr_to_list(obj)
            # foo(self.delimiter)
            for i, elem in enumerate(line_vals):
                foo("{:^{l}}".format(elem, l=self.col_len[i]))
                if i != 4:
                    foo(self.delimiter)
            foo("\n")
        if self.output_file is not None:
            filename.close()