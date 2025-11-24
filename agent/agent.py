import os
from dotenv import load_dotenv
from google import genai
from google.adk.agents import Agent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import AgentTool, google_search, load_memory
from google.adk.runners import Runner
from google.genai import types

# Load variables from .env
load_dotenv()

# Configura client con API key dal .env
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY non configurata nel file .env!")

client = genai.Client(api_key=api_key)

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=2,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

model = Gemini(
    model="gemini-2.5-flash-lite", 
    api_client=client,  
    retry_options=retry_config,
)

# ---------- Specialized agents ----------

flight_agent = Agent(
    name="FlightAgent",
    model=model,
    instruction=(
        """You are a travel agent tasked with finding 2-3 relevant flight options 
        given an origin airport, destination, and travel dates. Use google_search tool. 
        Return prices, times, and airlines in a concise format.
        
        IMPORTANT: Always respond in the same language the user is using. 
        If the language is unclear, default to English."""
    ),
    tools=[google_search],
    output_key="flight_options",
)

hotel_agent = Agent(
    name="HotelAgent",
    model=model,
    instruction=(
        """You are a hotel agent tasked with finding 2-3 accommodation options 
        given destination, dates, and approximate budget. Use google_search tool. 
        Include area, rating, and price range in your concise response.
        
        IMPORTANT: Always respond in the same language the user is using. 
        If the language is unclear, default to English."""
    ),
    tools=[google_search],
    output_key="hotel_options",
)

activities_agent = Agent(
    name="ActivitiesAgent",
    model=model,
    instruction=(
        """You are an activities agent tasked with recommending 3-5 relevant local 
        activities or excursions for a given destination and trip length. 
        Use google_search tool. Respond with concise bullet points.
        
        IMPORTANT: Always respond in the same language the user is using. 
        If the language is unclear, default to English."""
    ),
    tools=[google_search],
    output_key="activity_options",
)

# ---------- Router Agent ----------

root_agent = LlmAgent(
    name="TravelRouterAgent",
    model=model,
    description="Multi-agent travel concierge router agent with session memory.",
    instruction=(
        """You are a travel concierge assisting user travel planning. 

LANGUAGE: Always respond in the same language the user is using (Italian, English, Spanish, etc.). 
If the language is unclear, default to English.

WORKFLOW:
1. When user says they want to travel, proactively ask for ALL required info:
   - Departure city/airport
   - Destination(s)
   - Travel dates (or month/season)
   - Trip duration
   - Budget range

2. Use load_memory to check if you already know user preferences.

3. When you have ALL travel parameters, you MUST invoke ALL three specialized agents:
   - Call FlightAgent to get flight options
   - Call HotelAgent to get accommodation options  
   - Call ActivitiesAgent to get things to do and activities

4. After receiving results from ALL THREE agents, summarize everything clearly with 
   2-3 complete trip packages including flights, hotels, and activities.

IMPORTANT: 
- Always call all three agents (FlightAgent, HotelAgent, ActivitiesAgent) together 
  when you have complete trip information. Do not skip any agent.
- Maintain the conversation in the user's language throughout the entire interaction.
- If any parameter is missing, ask clarifying questions rather than guessing."""
    ),
    tools=[load_memory, AgentTool(flight_agent), AgentTool(hotel_agent), AgentTool(activities_agent)],
)

# ---------- Session & Memory ----------

db_url = "sqlite+aiosqlite:///./agent_sessions.db"
session_service = DatabaseSessionService(db_url=db_url)
memory_service = InMemoryMemoryService()

runner = Runner(
    agent=root_agent,
    app_name="conciergevoyager",
    session_service=session_service,
    memory_service=memory_service,
)
