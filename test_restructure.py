import modules.nodify as nodify
import argparse
import pytest
import filecmp


def test_wrong_delimiter_selected():
    test_delims = [",", ".", "\t", "_", "-"]
    pass_all = True
    for delim in test_delims:
        args = argparse.Namespace()
        args.delimiter = delim
        args.filepath = "input1.csv"
        args.output = None
        args.flow = None

        nodes = nodify.Restruct(args)
        nodes.restruct_data_arr()
        if delim == nodes.delimiter:
            pass_all = False

    assert pass_all


def test_no_appropriate_delimiter_possible():
    args = argparse.Namespace()
    args.delimiter = "|"
    args.filepath = "input2.csv"
    args.output = None
    args.flow = None

    nodes = nodify.Restruct(args)
    with pytest.raises(SystemExit):
        nodes.restruct_data_arr()
        out, err = capsys.readouterr()
        out_ok = "No appropriate delimiter has been selected or found. Try setting it with -d \"delim\""
        assert out == out_ok


def test_merged_columns_database():
    args = argparse.Namespace()
    args.delimiter = "|"
    args.filepath = "input1.csv"
    args.output = None
    args.flow = None

    nodes = nodify.Restruct(args)
    nodes.restruct_data_arr()

    assert isinstance(nodes.obj_list[0], type(nodify.Database()))


def test_merged_columns_table():
    args = argparse.Namespace()
    args.delimiter = "|"
    args.filepath = "input1.csv"
    args.output = None
    args.flow = None

    nodes = nodify.Restruct(args)
    nodes.restruct_data_arr()

    assert isinstance(nodes.obj_list[1], type(nodify.Table()))


def test_if_code_removes_tabs_spaces_in_entries():
    args = argparse.Namespace()
    args.delimiter = "|"
    args.filepath = "input1.csv"
    args.output = "output1.txt"
    args.flow = None

    nodes = nodify.Restruct(args)
    nodes.restruct_data_arr()
    nodes.table_output_cl()

    assert filecmp.cmp(nodes.output_file, "output_special_sym.txt")


def test_file_not_specified(capsys):
    args = argparse.Namespace()
    args.delimiter = "|"
    args.filepath = None
    args.output = "output1.txt"
    args.flow = None

    with pytest.raises(SystemExit):
        nodify.argument_input(new_args=args, test_mode=True)
        out, err = capsys.readouterr()
        out_ok = "Filepath value not assigned. Try using -f \"filepath\""
        assert out == out_ok


def test_file_not_existent(capsys):
    args = argparse.Namespace()
    args.delimiter = "|"
    args.filepath = "input1.exe"
    args.output = "output1.txt"
    args.flow = None

    with pytest.raises(SystemExit):
        nodify.argument_input(new_args=args, test_mode=True)
        out, err = capsys.readouterr()
        out_ok = "Input file does not exist. Provide a valid input file"
        assert out == out_ok
