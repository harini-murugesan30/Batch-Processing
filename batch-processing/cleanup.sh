#!/bin/bash

# Delete the HDFS output directory
docker exec -it hdfs bash -c "hdfs dfs -rm -r /user/spark/output"