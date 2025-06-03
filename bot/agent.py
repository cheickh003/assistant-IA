from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

from bot.tools import send_email, add_event, web_search, add_note, list_notes

llm = ChatOpenAI(model="gpt-4o-mini")

tools = [
    Tool.from_function(send_email, name="send_email", description="Envoyer un e-mail"),
    Tool.from_function(add_event, name="add_event", description="Créer un événement calendrier"),
    Tool.from_function(web_search, name="search_web", description="Recherche Web"),
    Tool.from_function(add_note, name="add_note", description="Ajouter une note"),
    Tool.from_function(list_notes, name="list_notes", description="Lister les notes"),
]

agent = initialize_agent(
    tools,
    llm=llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# Fonction wrapper pour s'assurer que l'agent retourne toujours une chaîne
def process_agent_response(user_input):
    try:
        result = agent.invoke(user_input)
        if isinstance(result, dict) and "output" in result:
            return result["output"]
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        return f"Désolé, je n'ai pas pu traiter votre demande : {str(e)}" 