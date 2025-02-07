import sqlite3
from langchain.chat_models import ChatOllama
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.sql_database import SQLDatabase

# Example-Prompt: Which input-voltage does the product with product-number 2 have? or I heard, the produkt number 2 has now an changed input voltage to 15V.

# Load SQLite database
db_path = "./poc/db/produkte.db"  # Change this to your actual database file
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
database = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# Define query tool for the agent
query_tool = QuerySQLDataBaseTool(db=database)

def select_query(select_sql):
    """Executes an SQL SELECT statement provided by the LLM."""
    try:
        cursor.execute(select_sql)
        result = cursor.fetchone()
        if result:
            column_names = [description[0] for description in cursor.description]
            return dict(zip(column_names, result))
        else:
            return "No results found."
    except sqlite3.Error as e:
        return f"Database query failed: {str(e)}"


def execute_update_query(update_sql):
    """Executes an SQL UPDATE statement provided by the LLM."""
    try:
        cursor.execute(update_sql)
        conn.commit()
        return "Database successfully updated."
    except sqlite3.Error as e:
        return f"Database update failed: {str(e)}"

# Initialize Ollama LLM
model = "llama3.1:latest"
model = "deepseek-r1:14b"
model = "qwen2.5:14b"       # https://github.com/QwenLM/Qwen-Agent?utm_source=chatgpt.com; https://www.reddit.com/r/LocalLLaMA/comments/1gheq9t/imo_the_best_model_for_agents_qwen25_14b/?utm_source=chatgpt.com
llm = ChatOllama(model=model)  # Change to your preferred Ollama model

# Conversation memory to keep context
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define tools for the agent
tools = [
    # Tool(
    #     name="QuerySQLiteDB",
    #     func=query_tool.run,
    #     description="Use this tool when you need to retrieve information from the SQLite database. Table produkte: (product_number INTEGER PRIMARY KEY,input_voltage INTEGER,input_current INTEGER,output_voltage INTEGER,output_current INTEGER,number_io_ports INTEGER,bus_protocol TEXT)."
    # ),
    Tool(
        name="SelectQuery",
        func=select_query,
        description="Use this tool to gather information from the database. You must generate a valid SQL SELECT statement and pass it to this tool. Example: If the user says 'Which input-voltage does the product with product-number 2 have?', generate: 'SELECT * FROM produkte WHERE product_number = 2'. Do NOT generate INSERT, DELETE, or DROP queries. The Table produkte has the following outline: (product_number INTEGER PRIMARY KEY,input_voltage INTEGER,input_current INTEGER,output_voltage INTEGER,output_current INTEGER,number_io_ports INTEGER,bus_protocol TEXT)"
    ),
    Tool(
        name="ExecuteUpdateQuery",
        func=execute_update_query,
        description="Use this tool when the user provides an update statement about the database. You must generate a valid SQL UPDATE statement and pass it to this tool. Example: If the user says 'The input voltage of product 2 changed to 15V', generate: 'UPDATE produkte SET input_voltage = 15 WHERE product_number = 2'. Do NOT generate DELETE, or DROP queries. The Table produkte has the following outline: (product_number INTEGER PRIMARY KEY,input_voltage INTEGER,input_current INTEGER,output_voltage INTEGER,output_current INTEGER,number_io_ports INTEGER,bus_protocol TEXT)"
    )
]

# Initialize LangChain agent
agent = initialize_agent(
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    verbose=True,
    memory=memory,
    system_prompt="You are an AI assistant that helps users interact with a product database. You can retrieve information and update the database based on user queries. Ensure that all SQL queries are valid and safe. Provide your answers in JSON.",
    handle_parsing_errors=True
)

# Run chat loop
print("Chat with the LLM (type 'exit' to stop)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = agent.run(user_input)
    print("LLM:", response)

# Close database connection
conn.close()