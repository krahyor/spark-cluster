# About the Repo 

This repository is based on the "pyspark-playground" project by Marin (@mrn-aglic) and other contributors. It has been cloned and modified for my personal learning and experimentation.... 🚀

You can view the original repository here: [pyspark-playground](https://github.com/mrn-aglic/pyspark-playground). 🔗


**NOTE**: As I am still a student learning these technologies, there may be some technical inaccuracies or mistakes in the setup or configurations. I apologize for any errors  and appreciate your understanding. 🙏😊📚

---

# Key Changes 📝

The following modifications were made to focus optimize the performance and resource utilization of Spark running on a YARN-managed Hadoop cluster.

- **Update to Spark version 3.5.4**  
- **Update to Hadoop version 3.3.6**
- **Install R-base** for R language support.
- **Install Scala** for Scala language support.
- **Update Python library requirements** in `requirements.txt`.

### YARN Configuration (Cluster Resource Manager)
1. **NodeManager Configuration**:
    - **CPU cores**: 2 cores per node (`yarn.nodemanager.resource.cpu-vcores`).
    - **Memory**: 3.5 GB per node (`yarn.nodemanager.resource.memory-mb`).

2. **Container Allocation Limits**:
    - **Maximum vCores per container**: 2 (`yarn.scheduler.maximum-allocation-vcores`).
    - **Minimum vCores per container**: 1 (`yarn.scheduler.minimum-allocation-vcores`).
    - **Maximum memory per container**: 3.5 GB (`yarn.scheduler.maximum-allocation-mb`).
    - **Minimum memory per container**: 512 MB (`yarn.scheduler.minimum-allocation-mb`).

### MapReduce (YARN) Configuration
1. **ApplicationMaster (AM) Memory**:
    - **1 GB** allocated to the ApplicationMaster (`yarn.app.mapreduce.am.resource.mb`).
    - **Java options for the ApplicationMaster** (`yarn.app.mapreduce.am.command-opts`) set to limit memory to **800 MB** (80% of AM memory).

2. **Mapper/Reducer Configuration**:
    - **Reducer memory**: 2 GB (`mapreduce.reduce.memory.mb`).
    - **Reducer Java options**: 1.6 GB for Java heap (`mapreduce.reduce.java.opts`).

3. **Parallelism**:
    - **Task Sort Buffer**: 256 MB (`mapreduce.task.io.sort.mb`).
    - **Reduce tasks**: 3 reducers (`mapreduce.job.reduces`).

### Spark Configuration on YARN
1. **Driver Memory**: 1 GB memory allocated to the driver (`spark.driver.memory`).
2. **Executor Memory**: 1.5 GB memory per executor (`spark.executor.memory`).
3. **ApplicationMaster Memory**: 1 GB of memory for the YARN ApplicationMaster (`spark.yarn.am.memory`).

### New Additions
- **TeraSort Benchmark using Python**: Added to test Spark performance and integration.
- **Makefile for Running TeraSort Benchmark for Spark on Hadoop Yarn cluster**: Simplifies the execution process, automating commands for benchmark tests.

---

### Example Makefile for TeraSort Benchmark

A **Makefile** has been added to streamline running the TeraSort benchmark with Python. The file automates the setup, execution, and validation of benchmark tests.

```Makefile
MODE?=client
CORES_PER_EXECUTOR?=1
MEMORY_PER_EXECUTOR?=1g

DATA_SIZE?=2GB
DATA_OUTPUT?=DATA_GEN
DATA_INPUT?=DATA_GEN
DATA_SORT_OUTPUT?=DATA_SORT
CHECK_DATA?=DATA_SORT

submit-yarn-cluster-terra-gen:
	docker exec da-spark-yarn-master spark-submit \
	--master yarn \
	--deploy-mode $(MODE) \
	--conf spark.executor.cores=$(CORES_PER_EXECUTOR) \
	--conf spark.executor.memory=$(MEMORY_PER_EXECUTOR) \
	--conf spark.dynamicAllocation.enabled=true \
	--conf spark.dynamicAllocation.executorIdleTimeout=60s \
	./apps/terra_sort_benchmark/terra_gen.py $(DATA_SIZE) $(DATA_OUTPUT)

submit-yarn-cluster-terra-sort:
	docker exec da-spark-yarn-master spark-submit \
	--master yarn \
	--deploy-mode $(MODE) \
	--conf spark.executor.cores=$(CORES_PER_EXECUTOR) \
	--conf spark.executor.memory=$(MEMORY_PER_EXECUTOR) \
	--conf spark.dynamicAllocation.enabled=true \
	--conf spark.dynamicAllocation.executorIdleTimeout=60s \
	./apps/terra_sort_benchmark/terra_sort.py $(DATA_INPUT) $(DATA_SORT_OUTPUT)

submit-yarn-cluster-terra-validate:
	docker exec da-spark-yarn-master spark-submit \
	--master yarn \
	--deploy-mode $(MODE) \
	--conf spark.executor.cores=$(CORES_PER_EXECUTOR) \
	--conf spark.executor.memory=$(MEMORY_PER_EXECUTOR) \
	--conf spark.dynamicAllocation.enabled=true \
	--conf spark.dynamicAllocation.executorIdleTimeout=60s \
	./apps/terra_sort_benchmark/terra_validate.py $(CHECK_DATA)

terra-validate-results:
	docker exec da-spark-yarn-master yarn logs -applicationId $(APPLICATION_ID) | grep -i "Result:"

da-spark-master-bash:
	docker exec -it da-spark-yarn-master bash
```

This configuration aims to optimize resource allocation, improve performance, and expand language support with R and Scala. Feel free to modify and test based on your specific workload! 🚀

---

# Running the code (Spark standalone cluster)
You can run the spark standalone cluster by running:
```shell
make run
```

or with 3 workers using:
```shell
make run-scaled
```

You can submit Python jobs with the command:
```shell
make submit APP=dir/relative/to/spark_apps/dir
```

e.g. 
```shell
make submit APP=data_analysis_book/chapter03/word_non_null.py
```

There are a number of commands to build the standalone cluster,
you should check the Makefile to see them all. But the
simplest one is:
```shell
make build
```

## Web UIs 🌐
- The master node can be accessed on:
`localhost:9090`. 
- The spark history server is accessible through:
`localhost:18080`.

---
# Running the Code (Spark on Hadoop YARN Cluster)

Before running, check the virtual disk size that Docker assigns to the container. In my case, I needed to assign:

- **70 GB** for 3 workers
- **90 GB** for 4 workers

Ensure the disk space is sufficient to handle the data processing and storage needs for your Spark on YARN cluster.

You can run Spark on the Hadoop Yarn cluster by running:
```shell
make run-yarn
```

or with 3 data nodes:
```shell
make run-yarn-scaled
```

or with N data nodes:
```shell
make run-yarn-scaled WORKER=N
```

You can submit an example job to test the setup:
```shell
make submit-yarn-test
```
which will submit the `pi.py` example in cluster mode.

You can also submit a custom job:
```shell
make submit-yarn-cluster APP=data_analysis_book/chapter03/word_non_null.py
```

There are a number of commands to build the cluster,
you should check the Makefile to see them all. But the
simplest one is:
```shell
make build-yarn
```

### For TeraSort benchmark on Spark

**1. Generate data**
```shell
make submit-yarn-cluster-terra-gen MODE=cluster CORES_PER_EXECUTOR=2 MEMORY_PER_EXECUTOR=2g DATA_SIZE=2GB DATA_OUTPUT=data_gen
```

**2. Sort the data**
```shell
make submit-yarn-cluster-terra-sort MODE=cluster CORES_PER_EXECUTOR=2 MEMORY_PER_EXECUTOR=2g DATA_INPUT=data_gen DATA_SORT_OUTPUT=data_sort
```

**3. Validate the data**
to validate the data using the command below
```shell
make submit-yarn-cluster-terra-validate MODE=cluster CORES_PER_EXECUTOR=2 MEMORY_PER_EXECUTOR=2g CHECK_DATA=data_sort
```
to check result of validation if you run on client mode you can just ```grep -i "Result:``` follow command above using pipe, but if you run on cluster mode you can using the command below
```shell
make terra-validate-results APPLICATION_ID=<your_application_id>
```

### For Ridge Regression benchmark on Spark

**1. Pull data using lfs (Pull before running docker-compose)**
```shell
git lfs pull
```

**2. Submit Ridge Regression benchmark**
```shell
make submit-yarn-cluster-ridge-regression MODE=cluster MEMORY_PER_EXECUTOR=2g NUMER_OF_EXECUTOR=3 CORES_PER_EXECUTOR=2
```

## Web UIs 🌐
You can access different web UIs. The one I found the most 
useful is the NameNode UI:
```shell
http://localhost:9870
```

Other UIs:
- ResourceManger - `localhost:8088`
- Spark history server - `localhost:18080`

**NOTE**: If you want to get in to da-spark-yarn-master bash can using command ```make da-spark-master-bash```
