import asyncio
import sqlite3
from autogen import AssistantAgent, UserProxyAgent

config_list = [
    {
        "model": "deepseek-r1:14b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
]

class DatabaseAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def query_product_data(self, product_number: int):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._query_product_data, product_number)
        return result

    def _query_product_data(self, product_number: int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produkte WHERE product_number=?", (product_number,))
            result = cursor.fetchone()
            conn.close()
            return result
        except sqlite3.DatabaseError as e:
            return f"Database error: {e}"

async def main() -> None:
    assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
    user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})
    db_agent = DatabaseAgent("./poc/db/produkte.db")

    product_info = await db_agent.query_product_data(2)  # Querying product number 2
    print(f"Product Info: {product_info}")

    await user_proxy.initiate_chat(assistant, message="Which input voltage does the product with the product number 1 have? Take a look in your database first.")

asyncio.run(main())
