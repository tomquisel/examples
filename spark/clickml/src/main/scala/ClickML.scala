/* SimpleApp.scala */
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD

import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.tree.RandomForest
import org.apache.spark.mllib.tree.model.RandomForestModel
import org.apache.spark.mllib.regression.LinearRegressionWithSGD
import org.apache.spark.mllib.classification.LogisticRegressionWithLBFGS
import org.apache.spark.mllib.classification.LogisticRegressionWithSGD
import org.apache.spark.mllib.classification.LogisticRegressionModel
import org.apache.spark.mllib.regression.RegressionModel
import org.apache.spark.mllib.evaluation.RegressionMetrics
import org.apache.spark.mllib.linalg.DenseVector
import org.apache.spark.mllib.linalg.SparseVector


object ClickMLApp {
  val featureVectorLength = 1000

  def main(args: Array[String]) {
    val conf = new SparkConf().setAppName("Click ML")
    val sc = new SparkContext(conf)
    val loader = new Loader(sc)
    val fullData = loader.loadAndParse(args(0))
    val data = loader.removeColumns(fullData, Set(10, 11))

    //data.take(5).foreach(row => println(row mkString(" ")))
    //println("-------------")
    //val firstColumn = data.map(row => row(0))
    //val firstColCounts = firstColumn.countByValue()
    //println(firstColCounts mkString("\n"))
    //println("-------------")
    val labelledData = loader.hashRDDFeatures(data)
    labelledData.take(300).foreach(println)
    //val (mappedData, categoryCountMap) = loader.mapCategories(data)
    //mappedData.take(5).foreach(row => println(row mkString " "))
    //println(categoryCountMap mkString "\n")
    //val labelledData = loader.formatForMllib(mappedData)

    val splits = labelledData.randomSplit(Array(0.7, 0.3))
    val (trainingData, testData) = (splits(0).cache(), splits(1))

    displayCorrespondence(trainingData)

    val model = trainRegressor(trainingData)
    //val model = trainHashedRF(trainingData)
    //println(model.toDebugString)

    //val testErr = testRF(model, testData)
    //val trainingErr = testRF(model, trainingData)

    val testErr = testRegressor(model, testData)
    val trainingErr = testRegressor(model, trainingData)

    println("training Error: " + trainingErr)
    println("Test Error: " + testErr)
  }

  class Loader(
    val sc : org.apache.spark.SparkContext
  ) {

    def loadAndParse(filename: String): RDD[Array[String]] = {
      // .tail strips off the csv header
      val data = sc.textFile(filename)
      val headerlessData = removeHeader(data)
      val parsedData = headerlessData.map { line =>
        // .tail strips off the ID, which is not useful for classifying
        val parts = line.split(',').tail
        parts
      }
      parsedData
    }

    def removeHeader(data: RDD[String]): RDD[String] = {
      val headerlessData = data.mapPartitionsWithIndex((idx, lines) => {
          if (idx == 0) {
            lines.drop(1)
          }
          lines
        })
      headerlessData
    }

    def removeColumns(data: RDD[Array[String]], cols: Set[Int]): RDD[Array[String]] = {
      val filteredData = data.map { row => 
        row.zipWithIndex.filterNot { x => cols.contains(x._2) }.unzip._1.toArray
      }
      filteredData
    }

    // makes categorical values compatible with mllib by:
    // 1) identifying distinct values
    // 2) sorting them
    // 3) mapping each distinct value to its position in the sorted list
    def mapCategories(data: RDD[Array[String]]): (RDD[Array[Int]], Map[Int, Int]) = {
      val labeledFields = data.flatMap(_.zipWithIndex.map(_.swap))
      // create an array of distinct values in each column
      val distinctValues = labeledFields.combineByKey(
        {v => Set(v)}, 
        {(s: Set[String], v) => s + v},
        {(s1: Set[String], s2: Set[String]) => s1 ++ s2}
      ).mapValues(v => v.toArray.sorted).collect()
      
      val distinctCountByColumn = distinctValues.map{ case (c, vals) => (c, vals.size) }.sorted
      println(distinctCountByColumn mkString "\n")

      val distinctCountMap = distinctCountByColumn.tail.map{ case (col, count) => (col-1, count) }.toMap

      val distinctValueMap = distinctValues.map{ case (c, vals) => (c, vals.zipWithIndex.toMap)}.toMap

      val mappedData = data.map( row => {
        0.until(row.length).map{ i => distinctValueMap(i)(row(i)) }.toArray
      })

      (mappedData, distinctCountMap)
    }

    def formatForMllib(data: RDD[Array[Int]]): RDD[LabeledPoint] = {
      val parsedData = data.map { row =>
        LabeledPoint(row(0).toDouble, new DenseVector(row.tail.map(x => x.toDouble)))
      }
      parsedData
    }

    def hashRDDFeatures(data: RDD[Array[String]]): RDD[LabeledPoint] = {
      data.map(hashRow)
    }
  }

  def hashRow(row: Array[String]): LabeledPoint = {
    val label = row(0).toDouble
    val features = row.tail
    val hashedFeatures = hashFeatures(features, label)
    new LabeledPoint(label, hashedFeatures)
  }
  def hashFeatures(features: Array[String], label: Double) = {
    val indices = features.zipWithIndex.map(hash)
    val uniqueIndices = indices.toSet.toArray
    val values = uniqueIndices.map(x => 1.0)
    new SparseVector(featureVectorLength, uniqueIndices, values)
    ///if (label == 1.0) {
    ///  new DenseVector(new SparseVector(featureVectorLength + 1, uniqueIndices ++ Array(featureVectorLength), values ++ Array(1.0)).toArray)
    ///} else {
    ///  new DenseVector(new SparseVector(featureVectorLength + 1, uniqueIndices, values).toArray)
    ///}
  }
  def hash(x: (String, Int)): Int = {
    x match {
      case (feature, index) => {
        //(features.hashCode() % (2 * featureVectorLength)) - featureVectorLength
        math.abs(feature.hashCode() + index) % featureVectorLength
      }
    }
  }

  def trainCategoricalRF(data: RDD[LabeledPoint], categoryCountMap: Map[Int, Int]) = {

    val numClasses = 2
    val numTrees = 3 // Use more in practice.
    val featureSubsetStrategy = "auto" // Let the algorithm choose.
    val impurity = "gini"
    val maxDepth = 30
    val maxBins = 4000

    val model = RandomForest.trainClassifier(data, numClasses, categoryCountMap,
      numTrees, featureSubsetStrategy, impurity, maxDepth, maxBins)
    model
  }

  def trainHashedRF(data: RDD[LabeledPoint]) = {

    val numClasses = 2
    val numTrees = 100
    val featureSubsetStrategy = "auto" // Let the algorithm choose.
    val impurity = "gini"
    val maxDepth = 4
    val maxBins = 30

    val model = RandomForest.trainClassifier(data, numClasses,
      Map.empty[Int, Int], numTrees, featureSubsetStrategy, impurity,
      maxDepth, maxBins)
    model
  }

  def trainRegressor(data: RDD[LabeledPoint]) = {
    val numIterations = 100
    //val model = LinearRegressionWithSGD.train(data, numIterations)
    val model = new LogisticRegressionWithLBFGS().run(data).clearThreshold()
    model
  }

  def testRF(model: RandomForestModel, data: RDD[LabeledPoint]) = {
    val predictionsAndLabels = data.map { point =>
      (model.predict(point.features), point.label)
    }
    val testErr = predictionsAndLabels.filter(r => r._1 != r._2).count.toDouble / data.count()
    println(predictionsAndLabels.take(100).mkString("\n"))
    println(predictionsAndLabels.countByValue.mkString("\n"))
    testErr
  }

  def testRegressor(model: LogisticRegressionModel, data: RDD[LabeledPoint]) = {
    val predictionsAndLabels = data.map { point =>
      (model.predict(point.features), point.label)
    }
    println(predictionsAndLabels.take(100).mkString("\n"))
    //println(predictionsAndLabels.countByValue.mkString("\n"))
    //val testErr = new RegressionMetrics(predictionsAndLabels).meanAbsoluteError
    //println(predictionsAndLabels.countByValue.mkString("\n"))
    val testErr = computeLogLoss(predictionsAndLabels)
    testErr
  }

  def computeLogLoss(predictionsAndLabels: RDD[(Double, Double)]): Double = {
    val logLosses = predictionsAndLabels.map{ case (yp, yt) => -(yt*math.log(yp) + (1.0 - yt)*math.log(1-yp))}
    logLosses.mean()
  }

  def displayCorrespondence(data: RDD[LabeledPoint]) = {
    val labelledIndexes = data.flatMap( x => {
      x.features match {
        case features:SparseVector => {
          features.indices.map( ind => (ind, x.label) )
        }
        case features:DenseVector => {
          features.toArray.zipWithIndex.filter{ case (value, ind) => value != 0.0 }.map{ case(value, ind) => (ind, x.label) }
        }
      }
    })
    val labelCountsByIndex = labelledIndexes.aggregateByKey(
      Array(0, 0))(
      (countPair, label) => {
        countPair(label.toInt) += 1
        countPair
      },
      (counts1, counts2) => {
        counts1 zip counts2 map { case (c1, c2) => c1 + c2 }
      }
    )
    val trueLabelRatioByIndex = labelCountsByIndex.map { case (key, counts) => (key, counts(1).toDouble / (counts.sum))}
    //println(labelCountsByIndex.sortBy( _._1 ).values.collect.map ( x => x mkString ",") mkString " ")
    println(trueLabelRatioByIndex.sortBy( _._1 ).values.collect mkString " ")
  }
}
