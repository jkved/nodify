# nodify
Algorithm to import table of SQL-type info and restructure it to node-like objects

This program is designed to be a command-line input Python code to process the SQL-type data table and convert it to objects which represent nodes. The table is of the following form:

database | table | column | type    | title
DB                        |         | Database name
         | TBL            |         | Table name
         |       | COL1   | integer | Column 1
         |       | COL2   | string  | Column 2
         
The code is made of a few principal parts:

It takes optional arguments for the code using argparse library. Optional arguments are delimiter form, filepath or output file. In addition to that, it is possible to pass the input file by stream (pipeline) to the script. Consider the following CL imput:
cat txt.txt | main.py

The code further employs multipledispatch library to overlead the load function for different type of nodes creation. The same library is later used for type-matching when outputing result. The main algorithm tries to find delimiter if it fails with current one, drops a header line of a file and works with two input methods. As a result nodes list (obj_list) is created as an attribute of class restruct instance.

Code testing is made using pytest and all the tests are stored in test_restructure.py. Furthermore, .csv and .txt files in the main folder are used for method and case testings.

Additional requirements.txt file is provided.

Main module code is provided in the file nodify.py, but main.py is designed to be started from command line.
