import csv

# https://docs.python.org/3/library/csv.html

def write_csv(data: str, path: str):
  with open(path, "w") as file:
    file.write(data)
  return ""

def sum_column(file_path: str, column_name: str):
  with open(file_path) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    index = 0
    temp_column = 0
    sum = 0
    for row in spamreader:
        if index == 0:
          row_index = 0
          for col in row:
            result = col.lower().find(column_name)
            if result >= 0:
              temp_column = row_index
            row_index += 1
        else:
          sum += float(row[temp_column])
        index += 1

  return f"{sum}"

def average_column(file_path: str, column_name: str):
  with open(file_path) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    index = 0
    temp_column = 0
    sum = 0
    rows = 0
    for row in spamreader:
        if index == 0:
          row_index = 0
          for col in row:
            result = col.lower().find(column_name)
            if result >= 0:
              temp_column = row_index
            row_index += 1
        else:
          sum += float(row[temp_column])
          rows += 1
        index += 1

  return f"{sum/rows}"
