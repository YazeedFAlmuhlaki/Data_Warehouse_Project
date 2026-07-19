 # Data Warehouse Project 

  This project builds a cloud-based data warehouse using Amazon Redshift. It extracts and transforms raw JSON log data from S3 and loads it into Redshift staging tables, then transforms it into analytics-ready fact and dimension tables using a star schema.

  ## 📁 Project Structure

  ├── create_tables.py      # Drops and creates tables in Redshift  
  ├── etl.py                # Loads data from S3 and inserts it into star schema  
  ├── sql_queries.py        # SQL queries for all operations  
  ├── dwh.cfg               # Redshift, IAM, and S3 configurations  
  └── README.md             # Project documentation

  ## ⚙️ How to Run

  1. Configure your `dwh.cfg` file:
     - Redshift cluster endpoint and credentials
     - IAM role ARN
     - S3 paths to `log-data`, `song-data`, and `log_json_path.json`

  Example `dwh.cfg`:
  [CLUSTER]
  HOST=your-redshift-cluster
  DB_NAME=dev
  DB_USER=awsuser
  DB_PASSWORD=yourpassword
  DB_PORT=5439

  [IAM_ROLE]
  ARN=arn:aws:iam::your-account-id:role/your-iam-role

  [S3]
  LOG_DATA='s3://udacity-dend/log-data'
  LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
  SONG_DATA='s3://udacity-dend/song-data'
  REGION='us-west-2'

  2. Run these scripts:

     ```bash
     python create_tables.py   # Drops and recreates all tables
     python etl.py             # Loads and transforms the data
     ```

  ## Schema Design (Star Schema)

  - **Fact Table**
    - `songplays`: All song play events with timestamp, user, song, artist, etc.

  - **Dimension Tables**
    - `users`: App users
    - `songs`: Song details
    - `artists`: Artist info
    - `time`: Timestamps split into hour, day, week, etc.

  ## ETL Flow

  - Stage raw data from S3 into `staging_events` and `staging_songs`
  - Insert data into fact and dimension tables using SQL joins and filters

  ## How to Verify

  Run these in Redshift to confirm loads:

  ```sql
  SELECT COUNT(*) FROM staging_events;
  SELECT COUNT(*) FROM staging_songs;
  SELECT COUNT(*) FROM songplays;
