# arquitecturas-agiles-g3
Repositorio para Implementación y control del proyecto del Curso Arquitecturas Agiles, Grupo 3

## Configure environment for kafka
- go to directory kafka and execute docker-compose up -d
- download the client https://dlcdn.apache.org/kafka/2.6.2/kafka-2.6.2-src.tgz
- go to directory of kafka-client and execute ``` ./gradlew jar -PscalaVersion=2.13.2 ```


create topic for billing monitor

```
bin/kafka-topics.sh --create \
--zookeeper localhost:22181 \
--replication-factor 1 \
--partitions 1 \
--config retention.ms=-1 \
--topic billing-control ```

```
bin/kafka-topics.sh --create \
--zookeeper localhost:22181 \
--replication-factor 1 \
--partitions 1 \
--config retention.ms=-1 \
--topic billing-health ```



```
bin/kafka-topics.sh --create \
--zookeeper localhost:22181 \
--replication-factor 1 \
--partitions 1 \
--config retention.ms=-1 \
--topic patient-control ```

```
bin/kafka-topics.sh --create \
--zookeeper localhost:22181 \
--replication-factor 1 \
--partitions 1 \
--config retention.ms=-1 \
--topic patient-health ```



delete topic
```
bin/kafka-topics.sh --delete \
--zookeeper localhost:22181 \
--topic unique-topic-name
```

list topics

```
bin/kafka-topics.sh --list --zookeeper localhost:22181
```

read messages
``` 
bin/kafka-console-consumer.sh --bootstrap-server localhost:29092 --topic patient-control --from-beginning
```

write messages

```
kafka/bin/kafka-console-producer.sh \
--broker-list localhost:9092 \
--topic my-topic
```


build docker image 

docker build -t myimage .

run container

 docker run --rm -d --network host --name python_monitor myimage


 docker logs 

 docker logs -f python_monitor