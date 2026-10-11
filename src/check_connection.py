import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / "cred.env")

uri = os.environ["NEO4J_URI"]
auth = (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])

with GraphDatabase.driver(uri, auth=auth) as driver:
    driver.verify_connectivity()
    with driver.session() as session:
        msg = session.run("RETURN 'Connected to Neo4j' AS msg").single()["msg"]
        print(msg)