import time
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator
import numpy as np

# Initialize Spark session
spark = SparkSession.builder.appName("RidgeRegressionCalCOFI").getOrCreate()
sc = spark.sparkContext

# Load data from HDFS
data_path = "hdfs://spark-yarn-master:9000/opt/spark/data/data_model/CalCOFI_processed_data.csv"
df = spark.read.csv(data_path, header=True, inferSchema=True)

# Define feature columns and target
feature_names = ['Depthm', 'T_degC', 'Salnty', 'Depthm_T_degC', 'T_degC_Salnty',
                 'Depthm_Salnty', 'Depthm_squared', 'T_degC_squared', 'Salnty_squared']
label_col = 'O2ml_L'

# Assemble features into a single vector column
assembler = VectorAssembler(inputCols=feature_names, outputCol="features")
data = assembler.transform(df).select("features", label_col)

# Split data into training and test sets
train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

# Define Ridge regression model
lr = LinearRegression(featuresCol="features", labelCol=label_col, elasticNetParam=0.0)  # Ridge (L2 only)

# Generate alpha values (regParam) from 0.0 to 0.05 with a step of 0.01
alpha_values = np.arange(0.0, 0.05, 0.01).tolist()  # Converts to a Python list

# Define parameter grid for alpha (regParam)
param_grid = ParamGridBuilder().addGrid(lr.regParam, alpha_values).build()

# Set up cross-validator for k-fold CV
cv = CrossValidator(estimator=lr,
                    estimatorParamMaps=param_grid,
                    evaluator=RegressionEvaluator(labelCol=label_col, metricName="rmse"),
                    numFolds=5)

# Start timer
start_time = time.time()

# Fit the model with cross-validation
cv_model = cv.fit(train_data)

# End timer
end_time = time.time()
training_time = end_time - start_time

# Get the best model
best_model = cv_model.bestModel
best_alpha = best_model._java_obj.getRegParam()

# Evaluate the best model on the test set
def evaluate_model(model, data):
    predictions = model.transform(data)
    evaluator_rmse = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="rmse")
    evaluator_r2 = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="r2")
    rmse = evaluator_rmse.evaluate(predictions)
    r2 = evaluator_r2.evaluate(predictions)
    return rmse, r2

rmse, r2 = evaluate_model(best_model, test_data)

# Estimate FLOPs and calculate GFLOPs
N = df.count()  # Get actual dataset size from DataFrame
d = len(feature_names)  # Number of features
k = 5  # Number of CV folds
num_alphas = len(alpha_values)

total_flops = k * num_alphas * (N * d**2 + d**3)  # FLOPs estimation
gflops = total_flops / (training_time * 10**9)

# Prepare output as a list of strings
output = [
    f"Training Time (seconds): {training_time}",
    f"Best Alpha: {best_alpha}",
    f"Best RMSE: {rmse}",
    f"Best R²: {r2}",
    f"Best Coefficients: {best_model.coefficients}",
    f"Intercept: {best_model.intercept}",
    f"Estimated GFLOPs: {gflops}"
]

# Delete existing output directory if it exists
output_path = "hdfs://spark-yarn-master:9000/out/ridge_regression_results"
fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(sc._jsc.hadoopConfiguration())
hdfs_path = sc._jvm.org.apache.hadoop.fs.Path(output_path)
if fs.exists(hdfs_path):
    fs.delete(hdfs_path, True)  # True enables recursive deletion

# Write output to HDFS
sc.parallelize(output).coalesce(1).saveAsTextFile(output_path)

# Stop Spark session
spark.stop()
