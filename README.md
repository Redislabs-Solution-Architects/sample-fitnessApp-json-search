# Storing, Searching, and aggregating JSON documents in a fitness application

#### Store the JSON documents in Redis
* Firstly, we need to spin-up a new Redis Enterprise cluster or Redis Stack server. Make sure you have included RedisJSON and RediSearch module in the Redis Enterprise database
* Then, for storing JSON documents, we need to generate random documents with the below sample:

      '{
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
      }'

  Edit `config.yaml`file to add the number of JSON documents you want to store in Redis database. You can also edit Redis host name, port number, and password in this file.
  
  To store JSON documents in Redis, we will use `store_json.py` file and execute following steps:


      python3 -m venv .env && source .env/bin/activate
      pip3 install -r requirements.txt
      python3 store_json.py


  This will take some time depending upon the number of JSON documents you intend to store.

* Next, since we would be leveraging RediSearch to enable full-text search and aggregation capabilites over JSON documents, we will create a RediSearch index. Execute following command using either redis-cli or RedisInsight tool:


      FT.CREATE steps_idx 
        ON JSON 
           PREFIX 1 "2023" 
        SCHEMA 
          $.ID as ID NUMERIC SORTABLE 
          $.eventDate as eventDate TEXT SORTABLE 
          $.events[0].txnRefNumber as txnRefNumber0 TAG 
          $.events[1].txnRefNumber as txnRefNumber1 TAG 
          $.events[0].eventAttributes[0].name as eventAttributes_name0 TEXT
          $.events[1].eventAttributes[0].name as eventAttributes_name1 TEXT 
          $.events[0].eventValues[0].name as eventValues_name0 TEXT
          $.events[1].eventValues[0].name as eventValues_name1 TEXT 
          $.events[0].eventAttributes[0].value as eventAttributes_value0 TEXT
          $.events[1].eventAttributes[0].value as eventAttributes_value1 TEXT 
          $.events[0].eventValues[0].value as eventValues_value0 NUMERIC SORTABLE
          $.events[1].eventValues[0].value as eventValues_value1 NUMERIC SORTABLE   




* Now, let's test the scenario by executing the following RediSearch queries :    
  1. Full-text Search on all the documents with source Fitbit:
      * `FT.SEARCH steps_idx "Fitbit"`

  2. Search all the documents with IDs between 1000 to 10000:
      * `FT.SEARCH steps_idx '@ID: [1000,10000]'`
  
  3. Perform a search query with filtering based on steps greater than 25000 for the document with source Googlefit:
      * `FT.SEARCH steps_idx "@eventValues_value0:[(25000,inf]"`
  
  4. Count all the documents with Googlefit as source:
      * `FT.AGGREGATE steps_idx "*" GROUPBY 1 @eventAttributes_value0 REDUCE COUNT 0 AS count`
  
  5. Perform an aggregate query to find the maximum steps for each distinct Googlefit source:
      * `FT.AGGREGATE steps_idx "*" GROUPBY 1 @eventAttributes_value0 REDUCE MAX 1 @eventValues_value0 AS max_value`
  
  6. Perform an aggregate query to calculate the sum of all the steps for each distinct Fitbit source:
      * `FT.AGGREGATE steps_idx "*" GROUPBY 1 @eventAttributes_value1 REDUCE SUM 1 @eventValues_value1 AS total_steps`
  
  7. Perform an aggregate query to calculate the average of steps for each distinct Fitbit source:
      * `FT.AGGREGATE steps_idx "*" GROUPBY 1 @eventAttributes_value1 REDUCE AVG 1 @eventValues_value1 AS avg_value`
  
  8. Perform an aggregate query to calculate the sum of steps for each distinct txnRefNumber:
      * `FT.AGGREGATE steps_idx "*" GROUPBY 1 @txnRefNumber0 REDUCE SUM 1 @eventValues_value0 AS total_steps`

******************************************************

