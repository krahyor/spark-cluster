import sys
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder.appName("Validate Data").getOrCreate()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: terra_validate.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Load the input data
    rdd = spark.sparkContext.textFile(input_file)

    # Parse the data
    keys = rdd.map(lambda line: line.split("\t")[0]).collect()

    # Validate sorting
    is_sorted = all(keys[i] <= keys[i+1] for i in range(len(keys) - 1))

    if is_sorted:
        print(f"Result: The data in {input_file} is sorted correctly.")
    else:
        print(f"Result: The data in {input_file} is NOT sorted correctly.")
    
    spark.stop()
