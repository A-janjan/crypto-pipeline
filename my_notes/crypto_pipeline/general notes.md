testing kafka container:
```
docker run --rm -it \
  --network=crypto-pipeline_default \
  confluentinc/cp-kafka:7.4.0 \
  kafka-topics --bootstrap-server kafka:9092 --list
```

testing postgresql container:
```
psql -h localhost -p 5433 -U dev -d crypto

```

redis:
```
redis-cli -h localhost
```

mongo:
```
mongosh localhost:27017
```

Elasticsearch: open [http://localhost:9200](http://localhost:9200)

Kibana: open [http://localhost:5601](http://localhost:5601)