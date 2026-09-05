import os

neo4j_url = os.getenv("neo4jurl")
neo4j_user = os.getenv("noe4juser")
neo4j_password = os.getenv("neo4jpass")

from neo4j import GraphDatabase

driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

def drop_projection(projection_name):
    query = """
    CALL gds.graph.exists($projection_name)
    YIELD exists
    RETURN exists
    """

    records, _, _ = driver.execute_query(
        query,
        parameters_={"projection_name": projection_name},
    )

    if records[0]["exists"]:
        driver.execute_query(
            "CALL gds.graph.drop($projection_name)",
            parameters_={"projection_name": projection_name},
        )
        print(f"Projection '{projection_name}' removed")
    else:
        print(f"Projection '{projection_name}' does not exist")