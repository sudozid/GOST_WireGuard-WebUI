import csv
import subprocess
import base64
import os
import re

filepath = 'parameters.csv'

def sanitize_csv_value(value):
    # Remove CSV special characters (commas and double-quotes)
    # and strip leading/trailing whitespace
    return re.sub(r'[,"]', '', value).strip()

def is_valid_port(port):
    try:
        return 1 <= int(port) <= 65535
    except ValueError:
        return False

def port_exists(port):
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['port'] == port:
                return True
    return False

def cleanup_csv_ids():
    # Read all data from the CSV
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)  # Convert the reader to a list to iterate over it twice

    # Reset IDs to be sequential starting from 1
    for i, row in enumerate(rows, start=1):
        row['id'] = str(i)

    # Write the data back to the CSV
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def read_parameters_from_csv(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

def write_parameters_to_csv(filepath, parameters):
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['username', 'password', 'port', 'interface']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for param in parameters:
            writer.writerow(param)

def base64_encode_username_password(username, password):
    credentials = f"{username}:{password}"
    credentials_bytes = credentials.encode('utf-8')
    base64_bytes = base64.b64encode(credentials_bytes)
    return base64_bytes.decode('utf-8')


def get_network_interfaces():
    base_path = '/sys/class/net/'
    interfaces = os.listdir(base_path)
    return interfaces  

def construct_command():
    parameters = read_parameters_from_csv(filepath)
    command_parts = ["gost"]
    for index, param in enumerate(parameters):
        encoded_auth = base64_encode_username_password(param['username'], param['password'])
        listener = f"-L :{param['port']}?auth={encoded_auth} -F direct://:0?interface={param['interface']}"
        command_parts.append(listener)
        if index > 0:
            # Add the separator before all listeners except the first one
            command_parts.insert(-1, "--")
    return " ".join(command_parts)

def parameters_to_list():
    dict_rows = read_parameters_from_csv(filepath)
    lines = [list(row.values()) for row in dict_rows]
    return lines


def remove_item_by_id(item_id):
    # Read all data from the CSV
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader if row['id'] != item_id]

    # Write data back to CSV, excluding the row with the specified ID
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    cleanup_csv_ids()


def add_item(username, password, port, interface):
    # Sanitize username and password
    username = sanitize_csv_value(username)
    password = sanitize_csv_value(password)

    # Check for valid port number
    if not is_valid_port(port):
        raise ValueError("Port must be a number between 1 and 65535.")

    # Check for a valid interface
    if interface not in get_network_interfaces():
        raise ValueError("Invalid network interface.")

    # Read the existing data to find the maximum id
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        existing_ids = [int(row['id']) for row in reader if row['id'].isdigit()]
        max_id = max(existing_ids, default=0)

    if port_exists(port):
        raise ValueError("Port already exists.")

    # Write the new entry with the next id
    with open(filepath, 'a', newline='') as csvfile:
        fieldnames = ['id', 'username', 'password', 'port', 'interface']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if csvfile.tell() == 0:  # File is empty, write header
            writer.writeheader()
        
        writer.writerow({
            'id': max_id + 1,
            'username': username,
            'password': password,
            'port': port,
            'interface': interface
        })


    
if __name__ == "__main__":
    print(get_network_interfaces())
"""    filepath = 'parameters.csv'  # The CSV file path
    parameters = read_parameters_from_csv(filepath)
    command = construct_command(parameters)
    print(f"Running command: {command}")
    run_command(command)"""
