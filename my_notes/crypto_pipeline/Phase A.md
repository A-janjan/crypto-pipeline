#### 4 mehr
i have some trobles with docker compose up [4 mehr]

```
➜  crypto-pipeline sudo docker compose up                                
[+] Running 7/7
 ! mongo          Interrupted                                                                                                                                                      0.5s 
 ✘ kafka Error    Get "https://registry-1.docker.io/v2/": tls: failed to verify certificate: x509: certificate has expired or is not yet valid: current time 2025-...              0.5s 
 ! zookeeper      Interrupted                                                                                                                                                      0.5s 
 ! postgres       Interrupted                                                                                                                                                      0.5s 
 ! elasticsearch  Interrupted                                                                                                                                                      0.5s 
 ! redis          Interrupted                                                                                                                                                      0.5s 
 ! kibana         Interrupted                                                                                                                                                      0.5s 
Error response from daemon: Get "https://registry-1.docker.io/v2/": tls: failed to verify certificate: x509: certificate has expired or is not yet valid: current time 2025-09-26T22:15:08+03:30 is after 2023-10-02T23:59:59Z

```

the is just with kibana.

---
#### 5 mehr

i solved it by changing mirror from elastic.co to docker hub [in my docker compose].

because of conflict i change the port of postgresql in docker-compose file to 5433

the kafka container doesnt have cli so the solution is:

```
# create topic

docker run --rm -it \
  --network=crypto-pipeline_default \
  confluentinc/cp-kafka:7.4.0 \
  kafka-topics --bootstrap-server kafka:9092 --create --topic test-topic --partitions 1 --replication-factor 1


# List topics again

docker run --rm -it \
  --network=crypto-pipeline_default \
  confluentinc/cp-kafka:7.4.0 \
  kafka-topics --bootstrap-server kafka:9092 --list

# Produce messages

docker run --rm -it \
  --network=crypto-pipeline_default \
  confluentinc/cp-kafka:7.4.0 \
  kafka-console-producer --bootstrap-server kafka:9092 --topic test-topic


# Consume messages

docker run --rm -it \
  --network=crypto-pipeline_default \
  confluentinc/cp-kafka:7.4.0 \
  kafka-console-consumer --bootstrap-server kafka:9092 --topic test-topic --from-beginning

```

