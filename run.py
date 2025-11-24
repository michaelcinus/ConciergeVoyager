import asyncio
from agent import runner, session_service, memory_service
from google.genai import types

USER_ID = "user1"
SESSION_ID = "session1"

async def main():
    while True:
        query = input("> ").strip()
        
        if not query:
            break
        
        query_content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )
        
        response_text = ""
        async for event in runner.run_debug(query_content):
            if event.content and event.content.parts:
                if event.content.parts[0].text:
                    response_text += event.content.parts[0].text
        
        print(f"{response_text}\n")
        
        # Salva la sessione in memoria dopo ogni risposta
        session = await session_service.get_session(
            app_name="chatbot",
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        await memory_service.add_session_to_memory(session)

if __name__ == "__main__":
    asyncio.run(main())
