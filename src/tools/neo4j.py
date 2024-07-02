from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "test"

driver = GraphDatabase.driver(uri, auth=(username, password))


def run_query(query, parameters=None)-> str:
    records = []
    with driver.session() as session:
        result = session.run(query, parameters)
        records = [record for record in result]
    # Convert each record to a string
    record_strings = [str(record) for record in records]

    # Join the record strings with a comma and space
    return ', '.join(record_strings)
