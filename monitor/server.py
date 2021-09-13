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



topic_monito_control = "monitor_control"
topic_microservices_healt = "microservices_health"
boostrap_servers = 'localhost:9092'
schema_registry_url = 'http://localhost:8081'

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        schedule.every(1).seconds.do(self.job)

        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def job(self):

        value_schema = avro.load('avro/ValueSchema.avsc')
        key_schema = avro.load('avro/KeySchema.avsc')
        avroProducer = AvroProducer(
        {'bootstrap.servers': boostrap_servers, 'schema.registry.url': schema_registry_url},
          default_key_schema=key_schema, default_value_schema=value_schema)
          
        key = str(uuid.uuid4())


        message_to_microservice = {
                "timestamp": str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")),
                "transaction_id": str(uuid.uuid4())
            }
       
        avroProducer.produce(topic=topic_monito_control, value=message_to_microservice, key=key, key_schema=key_schema, value_schema=value_schema)
        avroProducer.flush()



class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        c = AvroConsumer(
        {'bootstrap.servers': boostrap_servers, 'group.id': 'monitor-2', 'schema.registry.url': schema_registry_url,
        "api.version.request": True})
        c.subscribe([topic_microservices_healt])

        running = True
        while running:
            msg = None
            try:
                msg = c.poll(10)
                if msg:
                    if not msg.error():
                        print(msg.value())
                        print(msg.key())
                        print(msg.partition())
                        print(msg.offset())
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


def main():
    tasks = [
        Producer()
        
    ]

    for t in tasks:
        t.start()

if __name__ == "__main__":
    main()