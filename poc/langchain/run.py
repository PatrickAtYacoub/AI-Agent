import logging
import re
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, text
from sqlalchemy.orm import sessionmaker
from langchain_community.chat_models import ChatOllama
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_community.utilities import SQLDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = "./poc/db/produkte.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)
database = SQLDatabase(engine)

# Define SQLAlchemy metadata
metadata = MetaData()
produkte = Table(
    'produkte', metadata,
    Column('product_number', Integer, primary_key=True),
    Column('input_voltage', Integer),
    Column('input_current', Integer),
    Column('output_voltage', Integer),
    Column('output_current', Integer),
    Column('number_io_ports', Integer),
    Column('bus_protocol', String),
)

@contextmanager
def get_db_session():
    """Provides a managed database session."""
    session = Session()
    try:
        yield session
    finally:
        session.close()

# Query functions
def select_query(select_sql, params=None):
    """Executes an SQL SELECT statement safely with parameters."""
    try:
        with get_db_session() as session:
            query = text(select_sql)
            result = session.execute(query, params).fetchone()
            return result if result else "No results found."
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        return f"Database query failed: {str(e)}"

def execute_update_query(update_sql, params=None):
    """Executes an SQL UPDATE statement safely with parameters."""
    try:
        with get_db_session() as session:
            sql = text(update_sql)
            res = session.execute(sql, params)  # Falls hier eine Exception kommt, wird sie gefangen
            
            affected_rows = res.rowcount  # Anzahl der betroffenen Zeilen
            
            if affected_rows == 0:
                session.rollback()  # Falls keine Zeilen betroffen sind, kein Commit!
                return "No rows were updated."
            
            session.commit()  # Commit erst, wenn sicher ist, dass die Query erfolgreich war
            return f"Database successfully updated."
    
    except Exception as e:
        logger.error(f"Database update failed: {str(e)}")
        return f"Database update failed: {str(e)}"



# Initialize Planner and Executor LLMs
planner_llm = ChatOllama(model="llama3.1:latest")
executor_llm = ChatOllama(model="qwen2.5:14b")

# Conversation memory to keep context
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define tools for the executor
tools = [
    Tool(
        name="SelectQuery",
        func=select_query,
        description="Use this tool to gather information from the database. The database outline is: Table Produkte (product_number INTEGER PRIMARY KEY,input_voltage INTEGER,input_current INTEGER,output_voltage INTEGER,output_current INTEGER,number_io_ports INTEGER,bus_protocol TEXT). Generate a valid SQL SELECT statement and pass it to this tool. Example: 'SELECT * FROM produkte WHERE product_number = 2'."
    ),
    Tool(
        name="ExecuteUpdateQuery",
        func=execute_update_query,
        description="Use this tool to update records. The database outline is: Table Produkte (product_number INTEGER PRIMARY KEY,input_voltage INTEGER,input_current INTEGER,output_voltage INTEGER,output_current INTEGER,number_io_ports INTEGER,bus_protocol TEXT). Example: 'UPDATE produkte SET input_voltage = 15 WHERE product_number = 2'."
    )
]

prompt_template = """
You are an SQL expert. Answer the user's questions by querying the database about the product data.
Only run a query if necessary, and stop once you retrieve the needed information.
Your database looks like this:
Table: Produkte: product_number INTEGER PRIMARY KEY, input_voltage INTEGER, input_current INTEGER, output_voltage INTEGER, output_current INTEGER, number_io_ports INTEGER, bus_protocol TEXT

User Question: {input}

Thought: {agent_scratchpad}
"""

# Load planner and executor
planner = load_chat_planner(planner_llm)
executor = load_agent_executor(executor_llm, tools, verbose=False)

# Initialize Plan-and-Execute Agent
agent = PlanAndExecute(planner=planner, executor=executor, verbose=False)

if __name__ == "__main___":
    you = "You: "

    # Example prompt
    prompt1 = "Which input-voltage does the product with product-number 2 have?"
    print(you+prompt1)
    response = agent.run(prompt1)
    print("LLM:", response)

    prompt2 = "Update the input-voltage of the product with product-number 2 to 18V."
    print(you+prompt2)
    response = agent.run(prompt2)
    print("LLM:", response)

    print(you+prompt1)
    response = agent.run(prompt1)
    print("LLM:", response)

    prompt = "Welche technischen Daten hat Produkt 3"
    print(you+prompt)
    response = agent.run(prompt)
    print("LLM:", response)

    exit()

    # Interactive chat loop
    print("Chat with the LLM (type 'exit' to stop)")
    while True:
        user_input = input(you)
        if user_input.lower() == "exit":
            break
        response = agent.run(user_input)
        print("LLM:", response)
