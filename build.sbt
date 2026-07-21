name := "PhishPipe"
version := "0.1.0"
scalaVersion := "2.12.21"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.5.0",
  "org.apache.spark" %% "spark-sql" % "3.5.0",
  "org.scalatest" %% "scalatest" % "3.2.15" % Test
)