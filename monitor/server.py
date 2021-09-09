import schedule
import threading, time
import uuid
import json
from datetime import datetime



from kafka import KafkaConsumer, KafkaProducer

topic_billing_control = "billing-control"
topic_billing_health = "billing-health"

topic_patient_control = "patient-control"
topic_patient_health = "patient-health"

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

        message_to_billing = {
                "microservice_name": "message_billing",
                "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "transaction_id": str(uuid.uuid4())
            }

        patient_to_billing = {
                "microservice_name": "message_patient",
                "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "transaction_id": str(uuid.uuid4())
            }

        producer = KafkaProducer(bootstrap_servers='localhost:29092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic_billing_control, json.dumps(message_to_billing))

        producer.send(topic_patient_control, json.dumps(patient_to_billing))
        producer.close()


class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='localhost:29092',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe([topic_billing_control, topic_patient_control])

        while not self.stop_event.is_set():
            for message in consumer:
                print(message)
                if self.stop_event.is_set():
                    break

        consumer.close()


def main():
    tasks = [
        Producer(),
        Consumer()
    ]

    for t in tasks:
        t.start()

if __name__ == "__main__":
    main()