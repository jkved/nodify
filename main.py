import modules.nodify as nodify

def main():
    args = nodify.argument_input()
    nodes = nodify.restruct(args)
    nodes.restruct_data_arr()
    nodes.table_output_cl()


if __name__ == "__main__":
    main()