from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from datacleaner import data_cleaner
from airflow.operators.email_operator import EmailOperator

date_of_transaction = "2019-11-26"

default_args = {
    'owner': 'Airflow',
    'start_date': datetime(2021, 5, 25),
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

# Instantiating our dag (Setting catch=False, helps to avoid backfilling)
# template
dag = DAG(
    dag_id='store_dag',
    default_args=default_args,
    schedule_interval='@daily',
    template_searchpath=['/usr/local/airflow/sql_files'],
    catchup=False
)

# Try to check if the file to be cleaned and transformed is present in airflow directory
# To do this, we set a bash operator
t1 = BashOperator(
    task_id='check_if_file_exists',
    bash_command='shasum ~/store_files_airflow/raw_store_transactions.csv',
    retries=2,
    retry_delay=timedelta(seconds=15),
    dag=dag
)

# To clean the raw store data
t2 = PythonOperator(
    task_id='clean_raw_csv',
    python_callable=data_cleaner,
    dag=dag
)

# To create table in mysql database for housing the clean store data
t3 = MySqlOperator(
    task_id='create_mysql_table',
    mysql_conn_id='mysql_conn',
    sql='create_table.sql',
    dag=dag
)

# To insert table from local csv data into mysql database
t4 = MySqlOperator(
    task_id='insert_into_mysql_table',
    mysql_conn_id='mysql_conn',
    sql='insert_into_table.sql',
    dag=dag
)

# To generate location-wise and store-wise profit via aggregation
t5 = MySqlOperator(
    task_id='select_from_table',
    mysql_conn_id='mysql_conn',
    sql='select_from_table.sql',
    dag=dag
)

# Rename the location_wise_profit.csv to reflect the date of transaction
t6 = BashOperator(
    task_id="move_file_1",
    bash_command="cat ~/store_files_airflow/location_wise_profit.csv && mv ~/store_files_airflow/location_wise_profit.csv ~/store_files_airflow/location_wise_profit_%s.csv" % date_of_transaction,
    dag=dag
)

# Rename the store_wise_profit.csv to reflect the date of transaction
t7 = BashOperator(
    task_id="move_file_2",
    bash_command="cat ~/store_files_airflow/store_wise_profit.csv && mv ~/store_files_airflow/store_wise_profit.csv ~/store_files_airflow/store_wise_profit_%s.csv" % date_of_transaction,
    dag=dag
)

# Specify email to send report to
t8 = EmailOperator(
    task_id="send_email",
    to=['kevlararamid@gmail.com', 'mubarak.alliyu@gmail.com'],
    subject="Daily report generated",
    html_content = '<h1> Awesome power of computing, Your report is ready!!!</h1>',
    files=['/usr/local/airflow/store_files_airflow/location_wise_profit_%s.csv' % date_of_transaction,
    '/usr/local/airflow/store_files_airflow/store_wise_profit_%s.csv' % date_of_transaction],
    dag=dag
)

# Reaname the raw_transaction data to include day of transaction to avoid ambiguity. Since, the client is gonna send
# the report the next day
t9 = BashOperator(
    task_id="rename_raw_file",
    bash_command="mv ~/store_files_airflow/raw_store_transactions.csv ~/store_files_airflow/raw_store_transactions_%s.csv" % date_of_transaction,
    dag=dag
)


t1 >> t2 >> t3 >> t4 >> t5 >> [t6,t7] >> t8 >> t9