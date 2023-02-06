from multipledispatch import dispatch
from pathlib import Path
from functools import partial
import argparse
import sys

# Method for input argument processing if initial data is passed by path to file
def argument_input():
    parser = argparse.ArgumentParser(prog="templateIO",
                                     description="This program reads an SQL-type data structure from a file or as pipeline input. After that, the code prints it in command line or output file.\nFor file input use optional argument -f.\nFor stream input use like this: \"cat txt.txt | py main.py\"."
                                     )
    parser.add_argument('flow',
                        nargs="?",
                        help="see description for input types",
                        type=argparse.FileType('r'),
                        default=(None if sys.stdin.isatty() else sys.stdin)
                        )
    parser.add_argument("-f",
                        "--filepath",
                        action="store",
                        help="path to file containing input table",
                        default=None,
                        metavar="")
    parser.add_argument("-o",
                        "--output", 
                        action="store", 
                        help="name of the file for output to be printed",
                        metavar="",
                        default=None)
    parser.add_argument("-d",
                        "--delimiter",
                        help="sets the default delimiter for imported data structure (current - \",\"), must be passed in between \"\"",
                        metavar="",
                        default="|")

    args = parser.parse_args()
    if args.flow == None:
        target_file = Path(args.filepath)

        if not target_file.exists():
            print("Error: Input file does not exist")
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
class restruct:
    L_DB_NAME_INDEX = 0
    L_TBL_NAME_INDEX = 1
    L_COL_NAME_INDEX = 2
    L_COL_DTYPE_INDEX = 3
    L_TITLE_INDEX = 4


    def __init__(self, args) -> None:
        self.filepath = args.filepath
        self.delimiter = args.delimiter
        self.output_file = args.output
        self.flow = args.flow

        self.col_len=[0, 0, 0, 0, 0]
        self.obj_list=[]

    # Dispatched load functions for 3 types of nodes
    @dispatch(Database, list)
    def load(self, obj, vals) -> None:
        obj.name = vals[self.L_DB_NAME_INDEX]
        obj.title = vals[-1]

        self.col_len[self.L_DB_NAME_INDEX] = max(self.col_len[self.L_DB_NAME_INDEX], len(obj.name))
        self.col_len[self.L_TITLE_INDEX] = max(self.col_len[self.L_TITLE_INDEX], len(obj.title))

    @dispatch(Table, list)
    def load(self, obj, vals) -> None:
        obj.name = vals[self.L_TBL_NAME_INDEX]
        obj.title = vals[-1]

        self.col_len[self.L_TBL_NAME_INDEX] = max(self.col_len[self.L_TBL_NAME_INDEX], len(obj.name))
        self.col_len[self.L_TITLE_INDEX] = max(self.col_len[self.L_TITLE_INDEX], len(obj.title))

    @dispatch(Column, list)
    def load(self, obj, vals) -> None:
        obj.name = vals[self.L_COL_NAME_INDEX]
        obj.title = vals[-1]
        if vals[self.L_COL_DTYPE_INDEX].casefold() == "integer":
            obj.dtype = Integer()
            obj.dtype.name = vals[self.L_COL_DTYPE_INDEX]
        elif vals[self.L_COL_DTYPE_INDEX].casefold() == "string":
            obj.dtype = String()
            obj.dtype.name = vals[self.L_COL_DTYPE_INDEX]

        self.col_len[self.L_COL_NAME_INDEX] = max(self.col_len[self.L_COL_NAME_INDEX], len(obj.name))
        self.col_len[self.L_COL_DTYPE_INDEX] = max(self.col_len[self.L_COL_DTYPE_INDEX], len(obj.dtype.name))
        self.col_len[self.L_TITLE_INDEX] = max(self.col_len[self.L_TITLE_INDEX], len(obj.title))

    # Method to enable two types of inputs (from file or as stream)
    def input_method(self, filename) -> str:
        if self.flow == None:
            return filename.readline()
        else:
            return sys.stdin.readline()

    # In case wrong delimiter is selected
    def determine_delimiter(self, header) -> str:
        try_delims = [",", "|", "\t", "."]
        for delim in try_delims:
            if len(header.split(delim)) >= 3:
                print("Delimiter has been changed from \""+self.delimiter+"\" to \""+delim+"\".")
                return delim
        print("No appropriate delimiter has been selected or found.")
        raise SystemExit(1)

    # Main algorithm to restructure input data to node-type objects
    def restruct_data_arr(self) -> None:
        # Selects appropriate input type
        if self.flow == None:
            filename = open(self.filepath)
        else:
            filename = None

        # Making sure that data goes first instead of header and that correct delimiter was chosen
        header = self.input_method(filename)
        if len(header.split(self.delimiter)) < 3: # in the least delimiter case (for database), at least three values are present
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
        
        if self.flow == None:
            filename.close()
    
    # Utility methods for output
    @dispatch(Database)
    def objAttr_to_list(self, obj) -> list:
        return list([obj.name, "", "", "", obj.title])

    @dispatch(Table)
    def objAttr_to_list(self, obj) -> list:
        return list(["", obj.name, "", "", obj.title])

    @dispatch(Column)
    def objAttr_to_list(self, obj) -> list:
        return list(["", "", obj.name, obj.dtype.name, obj.title])

    # Command line print method
    def table_output_cl(self) -> None:
        if self.output_file != None:
            filename = open(self.output_file, "w+")
            foo = filename.write
        else:
            foo = partial(print, end="")

        for obj in self.obj_list:
                line_vals = self.objAttr_to_list(obj)
                #foo(self.delimiter)
                for i, elem in enumerate(line_vals):
                    foo("{:^{l}}".format(elem, l=self.col_len[i]))
                    if i != 4:
                        foo(self.delimiter)
                foo("\n")
        if self.output_file != None:
            filename.close()