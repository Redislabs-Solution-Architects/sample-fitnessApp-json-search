import redis
import json
import random
import string
from datetime import datetime, timedelta
import yaml


# Read the YAML file
with open('config.yaml', 'r') as file:
    yaml_data = yaml.safe_load(file)

# Retrieve the inputs from the YAML data
redis_host_name = yaml_data['connection_details']['redis_host_name']
redis_port = yaml_data['connection_details']['redis_port']
redis_password = yaml_data['connection_details']['redis_password']
no_of_json = yaml_data['json_details']['number_of_documents']


# Connect to Redis
r = redis.Redis(host=redis_host_name, port=redis_port, password=redis_password)

# Sample JSON object
sample_json = '''
{
  "events": [
    {
      "eventAttributes": [
        {
          "name": "source",
          "value": "googlefit"
        }
      ],
      "eventValues": [
        {
          "name": "steps",
          "value": "7852"
        }
      ],
      "txnRefNumber": "c1LBiQCcCM22"
    },
    {
      "eventAttributes": [
        {
          "name": "source",
          "value": "Fitbit"
        }
      ],
      "eventValues": [
        {
          "name": "steps",
          "value": "10942"
        }
      ],
      "txnRefNumber": "UdGlg3VXLHOZ5"
    }
  ],
  "ID": "1181",
  "eventDate": "2023-03-24"
}
'''

# Parse JSON object
data = json.loads(sample_json)

# Define start and end date range
start_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2023-12-31", "%Y-%m-%d")

n = no_of_json

# Generate and store random keys based on eventDate and ID
for i in range(n):
    
    # Generate a random date within the range
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    # Format the random date as "YYYY-MM-DD"
    formatted_date = random_date.strftime("%Y%m%d")


    # Generate random data
    random_txn_ref_0 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    random_txn_ref_1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    random_id = random.randint(1, 100000)
    random_step_0 = random.randint(1, 50000)
    random_step_1 = random.randint(1, 50000)

    # Combine eventDate and ID as the key
    key = formatted_date + "_" + str(random_id)

    # Change nested child attribute values
    data['ID'] = random_id
    data['eventDate'] = random_date.strftime("%Y-%m-%d")
    data['events'][0]['eventValues'][0]['value'] = random_step_0
    data['events'][1]['eventValues'][0]['value'] = random_step_1
    data['events'][0]['txnRefNumber'] = random_txn_ref_0
    data['events'][1]['txnRefNumber'] = random_txn_ref_1

    # Convert the modified JSON object back to a string
    modified_json = json.dumps(data)

    # Set JSON object in Redis
    r.execute_command('JSON.SET', key, '$', modified_json)
    

    # Optional: Print the generated key
print("Stored " + str(n) + " JSON documents")
