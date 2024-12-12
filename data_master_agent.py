from uagents import Agent, Context, Model
from typing import List, Optional
from datetime import datetime, timedelta

class MessageModel(Model):
    id: int
    heart_rate: int
    blood_oxygen: float
    hrv: Optional[float]  # HRV can be None
    glucose_level: Optional[float]  # Glucose level can be None
    latitude: float
    longitude: float
    timestamp: datetime

# Health data on a 30-second interval for driver emergencies
base_time = datetime.now()
health_data = {
    "low-blood-sugar": [
        {
            "id": 1,
            "heart_rate": 110 + i * 2,
            "blood_oxygen": 95.0 - i * 0.5,
            "hrv": 25.0 - i * 0.5,
            "glucose_level": 55.0 + i * 1.5,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timestamp": base_time + timedelta(seconds=i * 30),
        }
        for i in range(10)
    ],
    "heart-attack": [
        {
            "id": 2,
            "heart_rate": 200 - i * 5,
            "blood_oxygen": 85.0 + i * 0.5,
            "hrv": 5.0 + i * 0.5,
            "glucose_level": None,
            "latitude": 34.0522,
            "longitude": -118.2437,
            "timestamp": base_time + timedelta(seconds=i * 30),
        }
        for i in range(10)
    ],
    "low-blood-oxygen": [
        {
            "id": 3,
            "heart_rate": 120 - i * 2,
            "blood_oxygen": 78.0 + i * 1.0,
            "hrv": 15.0 + i * 0.5,
            "glucose_level": None,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": base_time + timedelta(seconds=i * 10),
        }
        for i in range(10)
    ],
}

# Create the Agent
agent = Agent(
    seed="data_master_monitor",
    port=8000,
    endpoint=["http://localhost:8000/health_monitor"]
)

i = 0
choice = None  # Initialize the global variable for health data choice


def pickCase(case_name: str) -> List[dict]:
    return health_data[case_name]


@agent.on_event("startup")
def initialize_choice(ctx: Context):
    """Initialize the choice of health data case at startup"""
    global choice
    choice = pickCase("heart-attack")  # You can change the case here
    ctx.logger.info(f"Initialized health data case: {choice}")


@agent.on_message(model=MessageModel)
async def handle_message(ctx: Context, sender: str, msg: MessageModel):
    """Log the received message along with its sender"""
    ctx.logger.info(f"Received message from {sender}: {msg}")


@agent.on_interval(period=10.0)
async def send_message(ctx: Context):
    """Send a message to agent Dr.Emergent by specifying its address"""
    global i  # Declare i as global to modify it
    if choice is None:
        ctx.logger.error("Health data choice is not initialized.")
        return

    data_point = choice[i]
    await ctx.send(
      
        "test-agent://agent1q2uhfdfh7c7z930hq40zrzu83u2eemu7np2qmsdteyqttkv3ra78vcgxkvm",
        MessageModel(**data_point)
    )
    ctx.logger.info(f"Message has been sent to Dr.Emergent: {data_point}")

    i += 1
    if i >= len(choice):  # Reset i after the last data point
        i = 0


if __name__ == "__main__":
    agent.run()
