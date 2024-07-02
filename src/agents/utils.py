import os


def open_local_file(file_name):
    # Get the directory path of the current module
    module_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the file path relative to the module's directory
    file_path = os.path.join(module_dir, file_name)

    # Open the file
    with open(file_path, 'r') as file:
        content = file.read()

    return content
