import csv
import json
import redis
import yaml

# Read the YAML file
with open('config.yaml', 'r') as file:
    yaml_data = yaml.safe_load(file)

# Retrieve the inputs from the YAML data
redis_host_name = yaml_data['connection_details']['redis_host_name']
redis_port = yaml_data['connection_details']['redis_port']
redis_password = yaml_data['connection_details']['redis_password']


# Connect to Redis
r = redis.Redis(host=redis_host_name, port=redis_port, password=redis_password)


# Open a CSV file for writing
with open('redisjson_data.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=None)

    # Perform SCAN operation to retrieve all keys matching the pattern
    cursor = '0'
    keys = []
    while True:
        # Perform SCAN command
        cursor, partial_keys = r.scan(cursor, match='*')

        # Iterate through the partial_keys
        for key in partial_keys:
            # Check if the key holds a JSON document using JSON.GET command
            json_data = r.execute_command('JSON.GET', key)

            # Check if the key holds a JSON document
            if json_data is not None:
                # Parse JSON data
                data = json.loads(json_data)

                def flatten_json(data):
                    flattened = {}

                    def flatten(d, prefix=''):
                        if isinstance(d, dict):
                            for key, value in d.items():
                                flatten(value, prefix + key + '_')
                        elif isinstance(d, list):
                            for index, item in enumerate(d):
                                flatten(item, prefix + str(index) + '_')
                        else:
                            flattened[prefix[:-1]] = d

                    flatten(data)
                    return flattened

                # Flatten the JSON data
                flattened_data = flatten_json(data)

                # Extract the field names from the flattened data
                field_names = list(flattened_data.keys())

                # Set the fieldnames for the CSV writer if not set
                if writer.fieldnames is None:
                    writer.fieldnames = field_names
                    writer.writeheader()

                # Write the flattened data rows
                writer.writerow(flattened_data)

        # Check if the SCAN operation is complete
        if cursor == 0:
            break

print("CSV file generated successfully.")
