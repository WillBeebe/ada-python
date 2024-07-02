import subprocess


def run_ada_command(directory: str, command: str):
  command = ['ada'] + command.split()
  print(f"running: {command}")
  result = subprocess.run(command, cwd=directory, capture_output=True, text=True)

  print("Standard Output:")
  print(result.stdout)

  print("Error Output:")
  print(result.stderr)
  return result.stdout
