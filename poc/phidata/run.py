from phi.agent import Agent
from phi.model.ollama import Ollama



from phi.storage.agent.sqlite import SqlAgentStorage

# Create a storage backend using the Sqlite database
storage = SqlAgentStorage(
    table_name="product data (product_number INTEGER PRIMARY KEY,input_voltage INTEGER,input_current INTEGER,output_voltage INTEGER,output_current INTEGER,number_io_ports INTEGER,bus_protocol TEXT)",
    db_file="./poc/db/produkte.db",
)

agent = Agent(
        model=Ollama(id="llama3.1:latest"),
    markdown=True,
    storage=storage
)

# Print the response in the terminal
# agent.print_response("Welchen Ausgangsstrom hat Produkt 1?")

agent.print_response("Which input voltage does the product with the product number 2 have? Take a look in your database first.")
