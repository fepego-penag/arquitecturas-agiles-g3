# arquitecturas-agiles-g3
Repositorio para Implementación y control del proyecto del Curso Arquitecturas Agiles, Grupo 3

## Prerequisitos
Es necesario contar con docker y la herramienta docker-compose

## Configuracion inicial de kafka
A continuación encontrara los pasos a seguir para configurar el ambiente de zookeeper, kafa, kafka-connector, y mysql

- Nos ubicamos en el directorio **kafka** and execute ```docker-compose up -d ```
- Descargamos el cliente de kafka https://dlcdn.apache.org/kafka/2.6.2/kafka-2.6.2-src.tgz
- Procedemos a descomprimir el archivo anterior y lo ubicamos en un directorio fuera de nuestro repositorio, esto con el fin de no subirlo a github
-  una vez que se descomprimiese el cliente de kafka procedemos entonces a construir las fuentes ejecutando el comando ``` ./gradlew jar -PscalaVersion=2.13.2 ```

Una vez que ya se hubiese subido el ambiente de desarrollo procedemos a crear los topics que usaremos para nuestro monitor

#### Creacion de topics

Una vez constriuido el cliente de kafka ejecutaremos en su directorio raiz las siguientes instrucciones para crear los topics 

```
bin/kafka-topics.sh --create \
--zookeeper localhost:2181 \
--replication-factor 1 \
--partitions 1 \
--config retention.ms=-1 \
--topic monitor_control
```

```
bin/kafka-topics.sh --create \
--zookeeper localhost:2181 \
--replication-factor 1 \
--partitions 1 \
--config retention.ms=-1 \
--topic microservices_health 
```

Una vez finalizada la creacion de topics procedemos a crear nuestra base de datos en mysql con el fin que la informacion persista en este motor.

**Recuerde:** para poder gestionar nuestra base de datos es necesario que el ambiente de kafka y sus componentes se encuentren arriba, para verificar esto nos dirigimos al directotio **kafka** ubicado en el repositorio de nuestro proyecto  ejecutamos ```
docker-compose ps``` 
los siguientes componentes deben de estar en stado Up
| zookeeper |      ... Up |
| --- | ----------- |
| broker     |     ... Up |
| schema-registry| ... Up |
| kafka-connect|   ... Up |
| ksqldb        |  ... Up |
| mysql         |  ... Up |
| kafkacat      |  ... Up |


una vez que confirmemos que el ambiente esta arriba ejecutaremos ```
docker exec -it mysql bash -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD' ```  de esta manera ingresaremos al contenedor de base de datos y ejecutaremos alli la creacionde nustra base de datos 

```
create database poc_clinical_monitor;
GRANT  CREATE, ALTER, DROP, SELECT, INSERT, UPDATE, DELETE ON poc_clinical_monitor.* TO connect_user;
```

## Configuración monitor
Para configurar el monitor es necesario ubicarse en el directorio ```monitor``` de nuestro proyecto aqui crearemos la imagen de nuestro contenedor mediante el comando ```docker build -t monitor-image .``` una vez finalice la creacion de la imagen procedemos a correr el contenedor mediante el comando ```docker run --rm -d --network host --name python_monitor monitor-image``` para asegurarnos que esten enviandose los mensajes correctamente lo podemos hacer usando el cliente de kafka de la misma manera que creamos los topics nos ubicamos en ese directorio y ejecutamos el comando  ```bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic monitor_control --from-beginning``` 

### Configuracion kafka-connect
A continuación vamos a configurar el connector para enviar la informacion a nuestra base de datos, para ello ejecutamos la ejecucion del siguiente contrto de servicio 
NOTA: !se debe realizar en la raíz del cliente de kafka.

```
curl --location --request PUT 'http://localhost:8083/connectors/sink-jdbc-mysql-01/config' \
--header 'Content-Type: application/json' \
--data-raw '{
    "connector.class"                    : "io.confluent.connect.jdbc.JdbcSinkConnector",
    "connection.url"                     : "jdbc:mysql://mysql:3306/poc_clinical_monitor",
    "topics"                             : "monitor_control, microservices_health",
    "key.converter"                      : "org.apache.kafka.connect.storage.StringConverter",
    "value.converter"                    : "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081",
    "connection.user"                    : "connect_user",
    "connection.password"                : "asgard",
    "auto.create"                        : true,
    "auto.evolve"                        : true,
    "insert.mode"                        : "insert",
    "pk.mode"                            : "record_key",
    "pk.fields"                          : "MESSAGE_KEY"
}'
```

para asegurarnos que la configuración  hubiese sido exitosa ingresaremos por medio de nuestro contenedor a la base de datos de nuevo y validaremos que las tablas se encuentren creadas y los mensajes esten insertados

para ello ejecutar los siguientes comandos

``` docker exec -it mysql bash -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD poc_clinical_monitor' ```

luego 
```
show tables;

select * from monitor_control; 
```
