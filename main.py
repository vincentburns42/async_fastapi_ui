import asyncio
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from confluent_kafka import Producer

# Define a class for our task
class MyClass:
    def __init__(self):
        """
        Initialize MyClass instance.

        Attributes:
        - running (bool): Flag to indicate if the task is running or not.
        - task (asyncio.Task): Reference to the running task.
        """
        self.running = False
        self.task = None

    async def start(self):
        """
        Start the task.

        Prints "Hello World" every second until running is set to False.
        Publishes message to kafka test topic until running is set to False.
        """
        self.running = True
        
        def delivery_report(err, msg):
            """ Called once for each message produced to indicate delivery result.
                Triggered by poll() or flush(). """
            if err is not None:
                print(f"Message delivery failed: {err}")
            else:
                print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        # Set up the Kafka configuration
        config = {
            'bootstrap.servers': 'kafka:9092',  # Replace with the address of your Kafka broker
        }

        # Create a Kafka producer instance with provided configurations
        producer = Producer(config)

        # Wait for any outstanding messages to be delivered and delivery reports to be received
        producer.flush()
        while self.running:
            print("Hello World")
            # Produce a message to the 'test' topic (replace 'test' with your target topic)
            producer.produce('test', key='key', value='value', callback=delivery_report)
            await asyncio.sleep(1)

    async def stop(self):
        """
        Stop the task.

        Sets running to False and waits for the running task to finish.
        """
        self.running = False
        if self.task:
            await self.task


# Create an instance of MyClass
app = FastAPI()
app.my_class = MyClass()


@app.post("/start")
async def start():
    """
    Start endpoint.

    If the task is not running or already done, create a new task and start it.
    """
    my_class = app.my_class
    if not my_class.task or my_class.task.done():
        my_class.task = asyncio.create_task(my_class.start())
        return {"message": "Started"}
    else:
        return {"message": "Already started"}


@app.post("/stop")
async def stop():
    """
    Stop endpoint.

    If the task is running, stop it.
    """
    if app.my_class.running:
        await app.my_class.stop()
        return {"message": "Stopped"}
    else:
        return {"message": "Already Stopped"}


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns the contents of the "index.html" file.
    """
    return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
