import sys
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder.appName("Sort Data").getOrCreate()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: terra_srot.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        # Load the input data
        rdd = spark.sparkContext.textFile(input_file)
        
        # Validate data format
        if rdd.isEmpty():
            print(f"Error: Input file {input_file} is empty or not accessible.")
            sys.exit(1)

        # Parse and sort the data by key
        sorted_rdd = (
            rdd.map(lambda line: (line.split("\t")[0], line))  # Extract key-value pairs
               .sortByKey()  # Sort by key
               .map(lambda x: x[1])  # Extract original lines
        )

        # Delete the existing output directory, if necessary
        hadoop_fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
        output_path = spark._jvm.org.apache.hadoop.fs.Path(output_file)

        if hadoop_fs.exists(output_path):
            print(f"Warning: Output path {output_file} exists. Deleting it.")
            hadoop_fs.delete(output_path, True)  # Recursive delete

        # Save sorted data
        sorted_rdd.saveAsTextFile(output_file)

        print(f"Result: Sorted data from {input_file} and saved to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        spark.stop()
