build:
	docker-compose build

build-yarn:
	docker-compose -f docker-compose-yarn.yml build

build-yarn-nc:
	docker-compose -f docker-compose-yarn.yml build --no-cache

build-nc:
	docker-compose build --no-cache

build-progress:
	docker-compose build --no-cache --progress=plain

down:
	docker-compose down --volumes --remove-orphans

down-yarn:
	docker-compose -f docker-compose-yarn.yml down --volumes --remove-orphans

run:
	make down && docker-compose up

run-scaled:
	make down && docker-compose up --scale spark-worker=3

run-d:
	make down && docker-compose up -d

run-yarn:
	make down-yarn && docker-compose -f docker-compose-yarn.yml up

WORKER?=3
run-yarn-scaled:
	make down-yarn && docker-compose -f docker-compose-yarn.yml up --scale spark-yarn-worker=$(WORKER)

stop:
	docker-compose stop

stop-yarn:
	docker-compose -f docker-compose-yarn.yml stop

submit:
	docker exec da-spark-master spark-submit --master spark://spark-master:7077 --deploy-mode client ./apps/$(APP)

submit-da-book:
	make submit app=data_analysis_book/$(APP)

submit-yarn-test:
	docker exec da-spark-yarn-master spark-submit --master yarn --deploy-mode cluster ./examples/src/main/python/pi.py

submit-yarn-cluster:
	docker exec da-spark-yarn-master spark-submit --master yarn --deploy-mode cluster ./apps/$(APP)

rm-results:
	rm -r book_data/results/*

MODE?=client
NUMER_OF_EXECUTOR?=3
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

submit-yarn-cluster-ridge-regression:
	docker exec da-spark-yarn-master spark-submit \
	--master yarn \
	--deploy-mode $(MODE) \
	--executor-memory $(MEMORY_PER_EXECUTOR) \
	--num-executors $(NUMER_OF_EXECUTOR) \
	--executor-cores $(CORES_PER_EXECUTOR) \
	./apps/ridge_regression/ridge_regression_v2.py

submit-yarn-cluster-ridge-regression-results:
	docker exec da-spark-yarn-master hdfs dfs -cat /out/ridge_regression_results/part-00000

da-spark-master-bash:
	docker exec -it da-spark-yarn-master bash
