from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator

# Initialize Spark session
spark = SparkSession.builder.appName("RidgeRegressionCalCOFI").getOrCreate()

# Load data from HDFS
data_path = "hdfs://spark-yarn-master:9000/data/CalCOFI_processed_data.csv"
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

# Define parameter grid for alpha (regParam)
param_grid = ParamGridBuilder().addGrid(lr.regParam, [0.0, 0.01, 0.05, 0.1, 0.5]).build()

# Set up cross-validator for k-fold CV
cv = CrossValidator(estimator=lr,
                    estimatorParamMaps=param_grid,
                    evaluator=RegressionEvaluator(labelCol=label_col, metricName="rmse"),
                    numFolds=5)

# Fit the model with cross-validation
cv_model = cv.fit(train_data)

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

# Output results
print(f"Best Alpha: {best_alpha}")
print(f"Best RMSE: {rmse}")
print(f"Best R²: {r2}")
print(f"Best Coefficients: {best_model.coefficients}")
print(f"Intercept: {best_model.intercept}")

# Stop Spark session
spark.stop()