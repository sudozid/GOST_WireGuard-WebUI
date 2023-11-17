from flask import Flask, jsonify, request, render_template
import re
import wg_mgmt
import gost_mgmt

import logging

app = Flask(__name__)

def validate_interface_name(interface_name):
    # Check if 'interface' is specified
    if not interface_name:
        return {
            "status": "error",
            "message": "No interface specified"
        }, 400  # HTTP status code for Bad Request

    # Validate the 'interface' parameter to match the expected 'wgX' format
    if not re.match(r'^wg\d+$', interface_name):
        return {
            "status": "error",
            "message": "Invalid interface format. Expected format is 'wgX' where X is a number."
        }, 400  # HTTP status code for Bad Request
    
    # If validation passes, return None to indicate success
    return None

# WireGuard Interfaces
@app.route('/api/wireguard/interfaces', methods=['GET'])
def get_all_wireguard_interface_names():
    try:
        interface_names = wg_mgmt.get_wireguard_interface_names()
        return jsonify({"status": "success", "data": interface_names})
    except Exception as e:
        # Log the exception
        return jsonify({"status": "error", "message": str(e)}), 500


#up wireguard interfaces
@app.route('/api/wireguard/get_active_interfaces', methods=['GET'])
def api_get_active_wireguard_interfaces():
    interfaces = wg_mgmt.get_active_wireguard_interfaces()
    if interfaces is None:
        return jsonify({"status": "error", "message": "Could not retrieve WireGuard interfaces"}), 500
    return jsonify({"status": "success", "data": interfaces})


#Add wireguard
@app.route('/api/wireguard/add', methods=['POST'])
def add_wireguard_interface():
    wg_config = request.form.get('wg_config')
    print(wg_config)

    if not wg_config:
        return jsonify({"status": "error", "message": "No configuration provided."}), 400

    result = wg_mgmt.add_wireguard_config(wg_config)

    if result["status"] == "success":
        return jsonify({"status": "success", "message": "WireGuard interface added successfully."}), 201
    else:
        print(result)
        return jsonify({"status": "error", "message": "Failed to add WireGuard interface."}), 500

@app.route('/api/wireguard/get_config', methods=['GET'])
def get_config():
    interface_name = request.args.get('interface')
    if interface_name and re.match(r'^wg\d+$', interface_name):
        try:
            config = wg_mgmt.display_config(f"{interface_name}.conf")
            return jsonify({"status": "success", "message": config})
        except FileNotFoundError:
            return jsonify({"status": "error", "message": "File not found"}), 404  # Not Found
        except Exception as e:
            return jsonify({"status": "error", "message": f"Exception occurred: {e}"}), 500  # Internal Server Error
    else:
        return jsonify({"status": "error", "message": "Invalid config"}), 400  # Bad Request

@app.route('/api/wireguard/modify_config', methods=['POST'])
def modify_config():
    interface_name = request.form.get('interface')
    config = request.form.get('config')
    try:
        wg_mgmt.save_config(interface_name, config)
        return jsonify(({"status" : "success", "message": "WireGuard Config modified sucessfully"}))
    except Exception as e:
        return jsonify(({"status" : "error", "message": f"Exception {e}"}))

@app.route('/api/wireguard/start_config', methods=['GET'])
def start_config():
    interface_name = request.args.get('interface')
    try:
        result = wg_mgmt.bring_interface_up(interface_name)
        if result['status'] == 'success':
            return jsonify({"status": "success", "message": f"{interface_name} brought up successfully"})
        else:
            return jsonify({"status": "error", "message": f"Failed to bring up {interface_name}: {result['error_message']}"})
    except Exception as e:
        return jsonify(({"status" : "error", "message": f"Exception {e}"}))


@app.route('/api/wireguard/stop_config', methods=['GET'])
def stop_config():
    # Try to get 'interface' from query params if it's a GET request, otherwise try form data
    if request.method == 'GET':
        interface_name = request.args.get('interface')
    else:  # For POST and other methods
        interface_name = request.form.get('interface')
    
    validation_result = validate_interface_name(interface_name)
    if validation_result is not None:
        return jsonify(validation_result[0]), validation_result[1]

    try:
        result = wg_mgmt.bring_interface_down(interface_name)
        print(result)
        if result['status'] in ['success', 'warning']:
            return jsonify({
                "status": result['status'],
                "message": f"{interface_name} brought down successfully",
                "error_code": result.get('error_code', 0)  # Include error_code if present
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to bring down {interface_name}",
                "error_code": result.get('error_code', None),
                "error_message": result.get('error_message', '')
            })
    except Exception as e:
        print(result)
        return jsonify({
            "status": "error",
            "message": f"Exception occurred: {e}",
            "error_code": getattr(e, 'errno', None)  # If the exception has an errno attribute
        })

@app.route('/api/wireguard/remove_config', methods=['GET'])
def api_remove_wireguard_config():
    interface_name = request.args.get('interface')
    
    if not interface_name:
        return jsonify({"status": "error", "message": "Interface name is required"}), 400
    
    if not re.match(r'^wg\d+$', interface_name):
        return jsonify({"status": "error", "message": "Invalid interface format. Expected format is 'wgX' where X is a number."}), 400
    
    success = wg_mgmt.remove_wireguard_config(interface_name)
    
    if success:
        return jsonify({"status": "success", "message": f"WireGuard interface '{interface_name}' removed successfully."})
    else:
        return jsonify({"status": "error", "message": f"Failed to remove WireGuard interface '{interface_name}'."}), 500

######################################GOST######################################################

@app.route('/api/gost/get_config', methods=['GET'])
def gost_get_config():
    try:
        config_data = gost_mgmt.parameters_to_list()
        return jsonify({
            "status": "success",
            "data": config_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/gost/generate_command', methods=['GET'])
def generate_command():
    try:
        config = gost_mgmt.construct_command()
        return jsonify({
            "status": "success",
            "data": config
        })
    except ValueError as e:  # Specific exceptions you expect to handle
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:  # General exception for any unexpected errors
        return jsonify({
            "status": "error",
            "message": "An error occurred while generating the command."
        }), 500

@app.route('/api/gost/remove_config', methods=['GET'])
def remove_config():
    csv_path = 'path_to_your_csv.csv'  # Replace with the path to your CSV file
    item_id = request.form.get('id')  # Get the 'id' from GET parameter

    # Check if 'id' parameter is provided
    if not item_id:
        return jsonify({"status": "error", "message": "No ID specified"}), 400

    try:
        gost_mgmt.remove_item_by_id(item_id)
        return jsonify({"status": "success", "message": f"Item with ID {item_id} has been removed"})
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "CSV file not found"}), 404
    except Exception as e:
        # Log the exception e to your logging framework
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gost/add_config', methods=['POST'])
def add_config():
    # Retrieve form data
    username = request.form.get('username')
    password = request.form.get('password')
    port = request.form.get('port')
    interface = request.form.get('interface')

    # Perform the validations
    if not username or not password or not port or not interface:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    if not gost_mgmt.is_valid_port(port):
        return jsonify({"status": "error", "message": "Port must be a number between 1 and 65535."}), 400

    if interface not in gost_mgmt.get_network_interfaces():
        return jsonify({"status": "error", "message": "Invalid network interface."}), 400

    if gost_mgmt.port_exists(port):
        return jsonify({"status": "error", "message": "Port already exists."}), 400

    try:
        gost_mgmt.add_item( username, password, port, interface)
        return jsonify({"status": "success", "message": "Configuration added successfully"})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/gost/get_interfaces', methods=['GET'])
def api_get_network_interfaces():
    try:
        interfaces = gost_mgmt.get_network_interfaces()
        return jsonify(interfaces)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")