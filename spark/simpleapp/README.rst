To Run
------

**Start a Spark Cluster**
https://spark.apache.org/docs/latest/cluster-overview.html
```bash
cd ~/spark/spark-1.2.0-bin-hadoop2.4/
./sbin/start-master.sh
# Check the web UI at http://localhost:8080/ to see where the master is running.
./bin/spark-class org.apache.spark.deploy.worker.Worker spark://derf:7077
```

**Submit this application**
https://spark.apache.org/docs/latest/submitting-applications.html
```bash
cd ~/spark/spark-1.2.0-bin-hadoop2.4/
./bin/spark-submit \
  --class SimpleApp \
  --master spark://derf:7077 \
  ~/code/examples/spark/simpleapp/target/scala-2.10/simple-project_2.10-1.0.jar
```
