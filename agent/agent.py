import os
from dotenv import load_dotenv  # ← Aggiungi questo import
from google import genai
from google.adk.agents import Agent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import AgentTool, google_search, load_memory
from google.adk.runners import Runner
from google.genai import types

# Carica variabili da .env
load_dotenv()  # ← Aggiungi questa riga

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

# ---------- Agenti specializzati ----------

flight_agent = Agent(
    name="FlightAgent",
    model=model,
    instruction=(
        """You are a travel agent tasked with finding 2-3 relevant flight options 
        given an origin airport, destination, and travel dates. Use google_search tool. 
        Return prices, times, and airlines in a concise format."""
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
        Include area, rating, and price range in your concise response."""
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
        Use google_search tool. Respond with concise bullet points."""
    ),
    tools=[google_search],
    output_key="activity_options",
)

# ---------- Router Agent ----------

root_agent = LlmAgent(
    name="TravelRouterAgent",
    model=model,
    description="Multi-agent travel concierge router",
    instruction=(
        """You are a travel concierge coordinating specialized agents.

LANGUAGE: Match the user's language (Italian, English, Spanish, etc.). Default to English if unclear.

STEP-BY-STEP PROCESS:
1. Gather ALL trip details from user:
   - Departure location ✓
   - Destination ✓
   - Dates ✓
   - Duration ✓
   - Budget ✓

2. Check load_memory for any saved preferences

3. When you have complete info, execute this EXACT sequence:
   
   FIRST: Call FlightAgent with departure, destination, and dates
   THEN: Call HotelAgent with destination, dates, and budget  
   FINALLY: Call ActivitiesAgent with destination and duration
   
   YOU MUST CALL ALL THREE AGENTS IN ORDER. No exceptions.

4. After ALL THREE agents respond, compile results into 2-3 trip packages.

CRITICAL RULES:
- Never skip calling any of the three agents
- Always call them in sequence: Flight → Hotel → Activities
- If user gives partial info, ask for missing details before calling agents
- Maintain conversation in user's language"""
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
