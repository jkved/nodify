import modules.nodify as nodify


def main():
    args = nodify.argument_input(new_args=None)
    nodes = nodify.Restruct(args)
    nodes.restruct_data_arr()
    nodes.table_output_cl()


if __name__ == "__main__":
    main()
