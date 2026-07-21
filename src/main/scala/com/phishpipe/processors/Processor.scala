package com.phishpipe.processors

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

case class PhishingRecord(
  address: String,
  emailType: String,
  date: String
)

object Processor {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("PhishPipeProcessor")
      .getOrCreate()

    process(spark, args(0), args(1))

    spark.stop()
  }

  def process(spark: SparkSession, inputPath: String, outputPath: String): Unit = {
    import spark.implicits._

    val raw_df = spark.read.textFile(inputPath)
    
     val phishingDF = raw_df.flatMap { line => 
      if (line.startsWith("#") || line.trim.isEmpty) {
        None
      } else {
        val parts = line.split(",")

        val date = parts(2)  

        Some(
          PhishingRecord(
            parts(0),
            parts(1),
            parts(2)
            )
          )
      }
    }.toDF()

    // date is in format yyyyMMdd for example 20230615, we need to convert it to yyyy-MM-dd format
    val clean_df = phishingDF.withColumn("date", to_date(col("date"), "yyyyMMdd"))

    // save the clean dataframe to parquet format
    clean_df
      .write
      .mode("overwrite")
      .parquet(outputPath)
  }
}
