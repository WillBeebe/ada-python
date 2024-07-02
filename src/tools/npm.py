import subprocess

from tools.files import create_directory


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
