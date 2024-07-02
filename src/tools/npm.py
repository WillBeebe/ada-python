import subprocess

from tools.files import create_directory


# todo: add tracing to all function calls
def install_npm_package(package: str, development: bool):
  save_dev = "--save-dev " if development else ""
  print(f"running: npm {save_dev}install {package}")
  return "ran successfully"

def run_npx_command(directory: str, command: str):
  print(f"running: mkdir {directory}")
  print(create_directory(directory))

  # Command to create a new React app
  command = ['npx'] + command.split() + ['--use-npm']
  print(f"running: {command}")
  result = subprocess.run(command, cwd=directory, capture_output=True, text=True)

  # Print the standard output
  print("Standard Output:")
  print(result.stdout)

  # Print the error output
  print("Error Output:")
  print(result.stderr)
  return "ran successfully"
