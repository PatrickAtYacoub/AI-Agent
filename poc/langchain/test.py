import unittest
from sqlalchemy import text
from poc.langchain.agents import execute_update_query, get_db_session, select_query, agent


class TestDB(unittest.TestCase):
    successful_update = "Database successfully updated."
    no_result_found = "No results found."
    db_query_failed = "Database query failed: "

    def test_connection(self):
        with get_db_session() as session:
            result = session.execute(text("SELECT * FROM produkte")).fetchall()
            self.assertTrue(result)

    def test_execute_update_query(self):

        with get_db_session() as session:
            # Test
            result = execute_update_query("UPDATE produkte SET input_voltage = 15 WHERE product_number = 1")
            self.assertEqual(result, self.successful_update)
            # Cleanup
            session.execute(text("UPDATE produkte SET input_voltage = 5 WHERE product_number = 1"))

    def test_execute_update_query_fail(self):
        # Test
        result = execute_update_query("UPDATE produkte SET input_voltage = 15 WHERE product_number = 100")
        self.assertNotEqual(result, self.successful_update, f"Expected: {self.successful_update}, Got: {result}")

    def test_execute_update_query_invalid_sql(self):
        # Test
        result = execute_update_query("UPDATE products SET input_voltage = 15 WHERE product_number = 1")
        self.assertNotEqual(result, self.successful_update, f"Expected: {self.successful_update}, Got: {result}, thats {self.successful_update == result}")

    def test_select_query(self):
        # Test
        result = select_query("SELECT * FROM produkte WHERE product_number = 1")
        res = result is not self.no_result_found and self.db_query_failed not in result
        self.assertTrue(res)

    def test_select_query_fail(self):
        # Test
        result = select_query("SELECT * FROM produkte WHERE product_number = 100")
        self.assertEqual(result, self.no_result_found)

    def test_select_query_invalid_sql(self):
        # Test
        result = select_query("SELECT * FROM products WHERE product_number = 1")
        res = self.db_query_failed in result
        self.assertTrue(res)

class TestLLM(unittest.TestCase):
    def test_select_statements(self):
        test_data = [
            ("Which input voltage does product 1 have?", "SELECT input_voltage FROM produkte WHERE product_number = 1"), 
            ("Which output voltage does product 2 have?", "SELECT output_voltage FROM produkte WHERE product_number = 2"),
            ("Which bus protocol does product 3 use?", "SELECT bus_protocol FROM produkte WHERE product_number = 3"),
            ("How many IO ports does product 4 have?", "SELECT number_io_ports FROM produkte WHERE product_number = 4"),
            ("Which technical data does product 2 have?", "SELECT * FROM produkte WHERE product_number = 2")
        ]

        testres = True
        for question, expected in test_data:
            llm_result = agent.invoke(question).get("output")
            with get_db_session() as session:
                dbres = session.execute(text(expected)).fetchone()
            testres = testres and all(str(part) in llm_result for part in dbres)
            print(f"{all(str(part) in llm_result for part in dbres)}: {dbres}")
            if not all(str(part) in llm_result for part in dbres):
                print(f"Expected: {dbres}, Got: {llm_result}")

        self.assertTrue(testres)

    def test_update_statements(self):

        with get_db_session() as session:
            session.execute(text("UPDATE produkte SET input_voltage = 5 WHERE product_number = 1"))
            session.commit()
            session.execute(text("UPDATE produkte SET output_voltage = 10 WHERE product_number = 2"))
            session.commit()
            session.execute(text("UPDATE produkte SET bus_protocol = 'SPI' WHERE product_number = 3"))
            session.commit()
            session.execute(text("UPDATE produkte SET number_io_ports = 4 WHERE product_number = 4"))
            session.commit()

        test_data = [
            ("Update the input voltage of product 1 to 15V.", "SELECT input_voltage FROM produkte WHERE product_number = 1", "15"),
            ("Update the output voltage of product 2 to 5V.", "SELECT output_voltage FROM produkte WHERE product_number = 2", "5"),
            ("Update the bus protocol of product 3 to 'I2C'.", "SELECT bus_protocol FROM produkte WHERE product_number = 3", "I2C"),
            ("Update the number of IO ports of product 4 to 8.", "SELECT number_io_ports FROM produkte WHERE product_number = 4", "8"),
        ]

        testres = True
        for question, expected, res in test_data:
            llm_result = agent.invoke(question).get("output")
            
            with get_db_session() as session:
                dbres = session.execute(text(expected)).fetchone()
                session.commit()
            testres = testres and str(dbres[0]) == res
            print(f"{str(dbres[0]) == res}: {dbres[0]} == {res}")

        self.assertTrue(testres)

if __name__ == "__main__":
    unittest.main()
