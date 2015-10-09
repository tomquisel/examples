#!/usr/bin/env bash

SPARK_PATH=~/spark/spark-1.2.0-bin-hadoop2.4
$SPARK_PATH/bin/spark-submit \
  --class ClickMLApp \
  --master spark://derf:7077 \
  target/scala-2.10/click-ml-project_2.10-1.0.jar \
  $*
