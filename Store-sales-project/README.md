# Project Description
The purpose of this project is to use airflow to automate the cleaning of a raw store transaction data and then load it into MYSQL database. After that, analytical queries were then used to generate location-based and store-based profit. This is particularly important for the store in order to garner strategies that can be used to increase their profitability. For example, the analysis of the location-based and store-based profit data can make the store to understand the location and store where they get most profit. Hence, forging strategies to channel more resources to this location. Also, the store with the most profit can also get more attention in terms of inventory scheduling and staffing arrangement in order to better make products readily available to consumers in those locations and stores.

# Files description
`config/airflow.cfg` is the config file that is used to house major settings used by airflow LocalExecutor. I tweaked the __smtp__ settings in the config file in order to successfully email the report of the analytical query. `sql_files` folder contains __SQL__ scripts for creating, inserting clean store transaction data and running analytical queries on MYSQL table. `store_files` folder houses raw store data, clean store data and the data generated from the analytical query. The store_files are also mounted on airflow directory. `docker-compose-LocalExecutor.yml` is used for setting and building the docker images(airflow, postgres and mysql), environments and settings that are used in this project.