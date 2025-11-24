# ConciergeVoyager
Your travel concierge agent that helps you organize and book your next trip

## Overview

ConciergeVoyager is a multi-agent travel concierge assistant that helps users plan trips by interactively gathering travel preferences (dates, destinations, duration, departure airport) and then providing curated flight, hotel, and activity options.

The agent system consists of:
- A Router Agent that manages conversation flow and decides which travel agents to invoke
- Flight, Hotel, and Activities Agents that search online for the best options
- A session memory system that retains user preferences through the conversation

## Architecture

- **Router Agent (TravelRouterAgent)** routes queries and collects required trip parameters.
- **FlightAgent** retrieves flight options based on the user's input.
- **HotelAgent** suggests hotels matching trip criteria.
- **ActivitiesAgent** recommends local activities and excursions.
- **Memory Layer** remembers past inputs and preferences to improve conversations.

## Usage

1. Create and activate virtual environment:
python3.11 -m venv venv 
source venv/bin/activate

2. Install dependencies:
 - pip install -r requirements.txt

3. Configure environment variables
 Create a .env file in the project root directory:
 GOOGLE_API_KEY=your_google_api_key_here
 Important:
 - et your API key from Google AI Studio
 - Never commit the .env file to version control (it's already in .gitignore)
 - Use .env.example as a template

3. Before running the project, you must export your Google API Key (required for Gemini models).
 - export GOOGLE_API_KEY=your_api_key

4. Run the CLI:
 - python run.py
 Or launch the ADK web interface (if applicable):
 - adk web .

5. Start by typing natural language requests like:
 "I want to plan a trip to Italy next April"
The agent will proactively ask for missing details (e.g., "From which airport?", "How many days?") before searching.

## Project Structure

- `agent.py`: Defines all agents and routing logic.
- `run.py`: CLI script to start the interactive session.
- `requirements.txt`: Python dependencies.

## Notes

This project uses Google's Gemini model through the Google ADK for multi-agent handling, online search tools, and conversational memory.