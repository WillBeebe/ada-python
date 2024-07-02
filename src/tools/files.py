import logging
import os
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the global ignore list
ignore_list = ['.git', 'node_modules', 'package-lock.json', '.gitignore', '__pycache__', 'poetry.lock', '.ruff_cache', '.pytest_cache']

def create_file_with_directories(filepath, content):
    # Extract the directory path from the given file path
    directory = os.path.dirname(filepath)

    # Create the directory path if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create the file
    with open(filepath, 'w') as file:
        file.write(content)  # You can write an empty string or any initial content


def get_directory_structure(directory, level=0):
    result = []
    indentation = '  ' * level
    result.append(f'{indentation}- {os.path.basename(directory)}')

    with os.scandir(directory) as it:
        for entry in it:
            if entry.name in ignore_list:
                continue
            if entry.is_dir():
                result.append(get_directory_structure(entry.path, level + 1))
            else:
                result.append(f'{indentation}  - {entry.name}')

    return '\n'.join(result)


def create_directory(directory: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory)
        return f"created {directory} successfully"
    else:
        return f"{directory} already exists"

def file_write(file_path: str, file_content: str) -> str:
    logger.info(f"updating file: {file_path}")
#   print(f"updating file: {file_path} content: {file_content}")
    try:
        create_file_with_directories(file_path, file_content)
    except Exception as e:
        logger.error("Error in tool action: %s", e, exc_info=True)
        return "there was an error writing that file, be sure to check that the file_path is correct, both for the parent project directory and the app directory."

    return f"Successfully wrote the file: {file_path}"

def repo_get_structure(directory) -> str:
    logger.info(f"getting directory structure for {directory}")
    structure = ""
    try:
        structure = get_directory_structure(directory)
    except Exception as e:
        logger.error("Error in tool action: %s", e, exc_info=True)
        structure = "that file does not exist at that path"
    # print(structure)

    return structure

def repo_read_all_files(directory) -> str:
    print('reading all repo files')
    result = ""

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Check if the file is in the ignore list
            if any(ignored in file_path for ignored in ignore_list):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result += f"path: {file_path}\n```\n{content}\n```\n\n"
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

    return result

def read_one_file(file_path) -> str:
    try:
        f = open(file_path, 'r', encoding='utf-8')
        return f.read()
    except Exception as e:
        logger.error("Error in tool action: %s", e, exc_info=True)
        return f"the file ${file_path} does not exist"

def delete_one_file(file_path) -> str:
    try:
        os.remove(file_path)
    except Exception as e:
        logger.error("Error in tool action: %s", e, exc_info=True)
        return f"the file ${file_path} does not exist"

def move_one_file(source_file_path, destination_file_path) -> str:
    try:
        shutil.move(source_file_path, destination_file_path)
    except Exception as e:
        logger.error("Error in tool action: %s", e, exc_info=True)
        return f"there was an error moving the file, please continue with other tasks"
