import schedule
import threading, time
import uuid
from datetime import datetime


from confluent_kafka import KafkaError
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.cimpl import TopicPartition



topic_monitor_control = "monitor_control"
topic_microservices_health = "microservices_health"
boostrap_servers = 'localhost:9092'
schema_registry_url = 'http://localhost:8081'


class Consumer(threading.Thread):


    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.value_schema = avro.load('avro/ValueSchemaFact.avsc')
        self.key_schema = avro.load('avro/KeySchemaFact.avsc')

    def stop(self):
        self.stop_event.set()

    def run(self):
        c = AvroConsumer(
        {'bootstrap.servers': boostrap_servers, 'group.id': 'monitor-2', 'schema.registry.url': schema_registry_url,
        "api.version.request": True})
        c.subscribe([topic_monitor_control])

        running = True
        while running:
            msg = None
            try:
                msg = c.poll(1)
                if msg:
                    if not msg.error():
                        print(msg.value())
                        print(msg.key())
                        self.send_message(msg)
                        c.commit(msg)
                    elif msg.error().code() != KafkaError._PARTITION_EOF:
                        print(msg.error())
                        running = False
                else:
                    print("No Message!! Happily trying again!!")
            except SerializerError as e:
                print("Message deserialization failed for %s: %s" % (msg, e))
                running = False
        c.commit()
        c.close()


    def send_message(self, msg):
        message_to_microservice = {
                "timestamp": str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")),
                "transaction_id": str(uuid.uuid4()),
                "service_name": "facturacion"
            }
        avroProducer = AvroProducer(
                                    {
                                        'bootstrap.servers': boostrap_servers,
                                        'schema.registry.url': schema_registry_url
                                    },
                                    default_key_schema=self.key_schema,
                                    default_value_schema=self.value_schema
                                    )
        avroProducer.produce(topic=topic_microservices_health, value=message_to_microservice, key=msg.key(), key_schema=self.key_schema, value_schema=self.value_schema)
        avroProducer.flush()

def main():
    tasks = [
        Consumer()
        
    ]

    for t in tasks:
        t.start()

if __name__ == "__main__":
    main()