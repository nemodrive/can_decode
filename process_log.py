from argparse import ArgumentParser
import re
import time

def replace(file, patterns, subst, out_suffix="_change"):
    # Read contents from file as a single string
    file_handle = open(file, 'r')
    file_string = file_handle.read()
    file_handle.close()

    # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
    for pattern in patterns:
        file_string = (re.sub(pattern, subst, file_string))

    # Write contents to file.
    # Using mode 'w' truncates the file.
    file_name = file+out_suffix
    file_handle = open(file_name, 'w')
    file_handle.write(file_string)
    file_handle.close()
    return file_name


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument('dbc', help='DBC file to convert.')
    arg_parser.add_argument('--one_shot', action='store_false',
                            default=True, help='change live.')

    change_with = ["@1+", "@1-", "@0+", "@0-"]
    change_what = [x[:2] + "\\" + x[2:] for x in change_with]

    args = arg_parser.parse_args()
    dbc_file = args.dbc
    one_shot = args.one_shot
    while True:

        for ch in change_with:
            changed_file = replace(dbc_file, change_what, ch, out_suffix="_"+ch)

        if not one_shot:
            break

        time.sleep(1)
