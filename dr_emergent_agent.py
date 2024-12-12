from uagents import Agent, Context, Model
from analysis import analyze_biometric_data  # Import the analysis function
from datetime import datetime
from typing import List, Optional

class MessageModel(Model):
    id: int
    heart_rate: int
    blood_oxygen: float
    hrv: Optional[float]  # HRV can be None
    glucose_level: Optional[float]  # Glucose level can be None
    latitude: float
    longitude: float
    timestamp: datetime
    
# Create the Health Monitoring Agent
health_monitoring_agent = Agent(
    seed="emergent_health_monitor_1",  # Replace with your actual seed
    port=8002,
    endpoint=["http://localhost:8002/health_monitor"]  # Adjust as needed
)

print(health_monitoring_agent.address)

@health_monitoring_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Health Monitoring Agent is now active.")

@health_monitoring_agent.on_message(model=MessageModel)  # Expecting a MessageModel as input
async def health_data_handler(ctx: Context, sender: str, data: MessageModel):
    # Analyze the received biometric data
    analysis_results = analyze_biometric_data(data.dict())  # Convert Pydantic model to dict for analysis
    
    # Log the analysis results
    ctx.logger.info(f"Received data from {sender}: {data.dict()}")
    ctx.logger.info(f"Analysis results: {analysis_results}")

    # Here we can implement further actions based on the analysis results
    # For example, sending alerts or notifications if issues are detected
  
# @health_monitoring_agent.on_interval(period=10.0)
# async def send_message(ctx: Context):
#   await ctx.send(
#         '',
#         ""
#     )
#     ctx.logger.info(f"Message has been sent to Dr.Emergent: {data_point}")

if __name__ == "__main__":
    health_monitoring_agent.run()