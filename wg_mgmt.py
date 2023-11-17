import os
import re
import subprocess
import  logging
import csv

logger = logging.getLogger(__name__)

wg_config_path = '/etc/wireguard'

def get_wireguard_interfaces():
    try:
        wg_output = os.popen('wg').read()
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "error", "message": f"{e}"}
    interfaces = re.findall(r'interface: (\S+)', wg_output)
    return interfaces

def add_wireguard_config(wireguard_config):
    # Normalize line endings and escape characters
    wireguard_config = wireguard_config.replace('\\n', '\n').replace('\n', os.linesep)
    wireguard_config = remove_dns_from_interface_section(wireguard_config)
    wireguard_config = add_table_off_to_interface_section(wireguard_config)

    # Get a list of existing WireGuard config files
    try:
        existing_configs = os.listdir(wg_config_path)
    except FileNotFoundError:
        print("The directory does not exist. Make sure you have WireGuard installed and the correct path is set.")
        return {"status": "error", "message": "Directory does not exist"}

    # Pattern to match the files in the format 'wgX.conf'
    pattern = re.compile(r'wg(\d+)\.conf$')

    # Find the highest number (X) used in the existing config files
    highest_number = 0
    for config in existing_configs:
        match = pattern.match(config)
        if match:
            number = int(match.group(1))
            highest_number = max(highest_number, number)

    # Set the new config file name to one number higher than the highest found
    new_config_file = f"wg{highest_number + 1}.conf"

    # Path for the new config file
    new_config_path = os.path.join(wg_config_path, new_config_file)

    # Check if the new config file already exists by some other means
    if os.path.exists(new_config_path):
        print(f"The file {new_config_file} already exists. Incrementing to a higher number.")
        # If for some reason it exists, increment until we find a free number
        highest_number += 1
        new_config_file = f"wg{highest_number + 1}.conf"
        new_config_path = os.path.join(wg_config_path, new_config_file)

    # Write the WireGuard configuration to the new config file
    try:
        with open(new_config_path, 'w') as config_file:
            config_file.write(wireguard_config)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
        return {"status": "error", "message": f"Failed to write configuration"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to write configuration because {e}"}
    return {"status": "success", "message": "Configuration saved and interface updated"}


def get_wireguard_interface_names():
    try:
        interface_names = []
        pattern = re.compile(r'^wg\d+\.conf$')

        if not os.path.exists(wg_config_path):
            raise FileNotFoundError(f"The directory {wg_config_path} does not exist.")

        with os.scandir(wg_config_path) as entries:
            for entry in entries:
                if entry.is_file() and pattern.match(entry.name):
                    name_without_extension, _ = os.path.splitext(entry.name)
                    interface_names.append(name_without_extension)

        return interface_names
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        raise
    except OSError as e:
        logger.error(f"File system error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

#to avoid changing default route
def add_table_off_to_interface_section(wireguard_config):
    wireguard_config = wireguard_config.replace('\\n', '\n').replace('\n', os.linesep)
    
    # Define the regex pattern for the [Interface] section and capturing the content after it
    interface_section_pattern = r'(\[Interface\][^[]*)(\[Peer\]|\Z)'
    # Search for the [Interface] section and the start of the [Peer] section or end of the string
    match = re.search(interface_section_pattern, wireguard_config, re.DOTALL)

    if match and 'Table=off' not in match.group(1):
        # Construct the replacement string with "Table=off" and a newline
        replacement = match.group(1).rstrip() + '\nTable=off\n\n' + match.group(2)
        # Replace the matched text with the new string
        wireguard_config = wireguard_config[:match.start(1)] + replacement + wireguard_config[match.end(2):]
    print(wireguard_config)
    return wireguard_config

def remove_dns_from_interface_section(wireguard_config):
    # Define the regex pattern for the [Interface] section and capturing the content after it
    interface_section_pattern = r'(\[Interface\][^[]*)(\[Peer\]|\Z)'
    # Search for the [Interface] section and the start of the [Peer] section or end of the string
    match = re.search(interface_section_pattern, wireguard_config, re.DOTALL)

    if match:
        # Remove DNS settings from the [Interface] section if present
        interface_section = match.group(1)
        interface_section = re.sub(r'DNS\s*=\s*[^\\n]+', '', interface_section)

        # Construct the replacement string
        replacement = interface_section.rstrip() + '\n\n' + match.group(2)

        # Replace the matched text with the new string
        wireguard_config = wireguard_config[:match.start(1)] + replacement + wireguard_config[match.end(2):]

    return wireguard_config

def bring_interface_up(new_config_file):
    # Remove the '.conf' extension from the config file name
    interface_name = new_config_file.replace('.conf', '')

    # Construct the command to bring the interface up
    command = ['wg-quick', 'up', interface_name]

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Command executed successfully: {' '.join(command)}")
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess failed with error code {e.returncode}: {e.stderr}")
        return {"status": "error", "error_code": e.returncode, "error_message": e.stderr}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"status": "error", "error_code": 3, "error_message": str(e)} 

def bring_interface_down(new_config_file):
    print(new_config_file)
    try:
        # Remove the '.conf' extension from the config file name
        interface_name = new_config_file.replace('.conf', '')
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"status": "error", "error_code": 3, "error_message": str(e)}
    command = ['wg-quick', 'down', interface_name]

    try:
        p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if p.returncode == 0:
            logger.info("wg-quick down completed successfully.")
            return {"status": "success", "message": "Interface down successfully", "error_code": 0}
        elif p.returncode == 1:
            logger.warning("Config already down or another error occurred.")
            return {"status": "warning", "message": "Config may already be down", "error_code": 1}
        else:
            logger.error(f"Error on wg-quick down: {p.stderr}")
            return {"status": "error", "message": "Failed to bring interface down", "error_code": p.returncode, "error_message": p.stderr}

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess failed with error code {e.returncode}: {e.stderr}")
        return {"status": "error", "error_code": e.returncode, "error_message": e.stderr}
    except FileNotFoundError as e:
        logger.error(f"Command not found: {e}")
        return {"status": "error", "error_code": 2, "error_message": str(e)}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"status": "error", "error_code": 3, "error_message": str(e)}


def display_config(interface_name):
    config_file_path = os.path.join(wg_config_path, interface_name)
    
    with open(config_file_path, 'r') as file:
        config_data = file.read()
    return config_data

def save_config(interface_name, new_config_data):
    new_config_data = remove_dns_from_interface_section(new_config_data)
    new_config_data = add_table_off_to_interface_section(new_config_data)

    config_file_path = os.path.join(wg_config_path, f"{interface_name}.conf")
    config_lines = new_config_data.split('\\n')
    try:
        with open(config_file_path, 'w') as file:
            for line in config_lines:
                file.write(line + '\n')  # Append a newline character after each line
        print(f"Configuration saved to {config_file_path}")
    except IOError as e:
        print(f"Failed to write configuration to {config_file_path}: {e}")

    bring_interface_down(interface_name)
    bring_interface_up(interface_name)

def get_active_wireguard_interfaces():
    try:
        # Run the 'wg' command and capture the output
        wg_output = subprocess.check_output(['wg'], text=True)

        # Regular expression to extract the interface names that are "up"
        interface_pattern = r'^interface: (\S+)'
        interfaces = re.findall(interface_pattern, wg_output, re.MULTILINE)

        return interfaces
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing 'wg': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return []

def remove_wireguard_config(interface_name):
    parameters_csv_path = "parameters.csv"
    config_file_path = os.path.join(wg_config_path, f"{interface_name}.conf")
    parameters_updated = False

    if os.path.isfile(config_file_path):
        try:
            os.remove(config_file_path)
            logger.info(f"Removed WireGuard config for interface: {interface_name}")
        except Exception as e:
            logger.error(f"Failed to remove WireGuard config for interface: {interface_name}. Exception: {e}")
            return False

        # Now, update the parameters.csv
        try:
            # Read all data from the CSV
            with open(parameters_csv_path, newline='') as csvfile:
                reader = list(csv.DictReader(csvfile))

            # Replace interface with 'lo' where the interface matches the one being removed
            for row in reader:
                if row['interface'] == interface_name:
                    row['interface'] = 'lo'
                    parameters_updated = True

            # Write data back to CSV
            with open(parameters_csv_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=reader[0].keys())
                writer.writeheader()
                writer.writerows(reader)

            if parameters_updated:
                logger.info(f"WireGuard interface {interface_name} replaced with 'lo' in parameters.csv")
            else:
                logger.warning(f"No matching interface found in parameters.csv to replace with 'lo'")
            return True
        except Exception as e:
            logger.error(f"Failed to update parameters.csv. Exception: {e}")
            return False
    else:
        logger.warning(f"No config file found for interface: {interface_name}. Nothing to remove.")
        return False