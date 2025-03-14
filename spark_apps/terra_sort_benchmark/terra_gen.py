import sys
import random
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder.appName("Generate Data").getOrCreate()

# Approximate size of a single record (key + value + separator + newline)
BYTES_PER_RECORD = 102

# Generate random key-value pairs
def generate_data(_):
    key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))  # 10-char key
    value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=90))  # 90-char value
    return f"{key}\t{value}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: terra_gen.py <data_size> <output_file>")
        print("Example: terra_gen.py 2GB hdfs://namenode:9000/output_data")
        sys.exit(1)

    data_size = sys.argv[1].upper()  # Input data size (e.g., "2GB" or "2MB")
    output_file = sys.argv[2]

    # Convert data size to bytes
    if data_size.endswith("GB"):
        total_bytes = int(data_size[:-2]) * 1024 * 1024 * 1024
    elif data_size.endswith("MB"):
        total_bytes = int(data_size[:-2]) * 1024 * 1024
    else:   
        print("Usage: Invalid data size format. Use 'GB' or 'MB'.")
        sys.exit(1)

    # Calculate the number of records needed
    num_records = total_bytes // BYTES_PER_RECORD

    print(f"Progress: Generating approximately {num_records} records for a total size of {data_size}...")

    # Create RDD with random data (distributed generation)
    rdd = spark.sparkContext.parallelize(range(num_records), numSlices=10).map(generate_data)
    
    # Delete the existing output directory, if necessary
    hadoop_fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    output_path = spark._jvm.org.apache.hadoop.fs.Path(output_file)

    if hadoop_fs.exists(output_path):
        print(f"Warning: Output path {output_file} exists. Deleting it.")
        hadoop_fs.delete(output_path, True)  # Recursive delete

    # Save the data to the output directory
    rdd.saveAsTextFile(output_file)

    print(f"Result: Generated data of size {data_size} and saved to {output_file}")

    spark.stop()
