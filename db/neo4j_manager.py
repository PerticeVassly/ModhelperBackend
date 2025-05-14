from neo4j import GraphDatabase
from typing import List
from .base import BaseGraphDB, ModRelation
from config import settings
import logging
import time

logger = logging.getLogger("database")

class Neo4jGraphDB:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URL, 
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        self._test_connection()
        self._init_constraints()
        logger.info(f"Connected to Neo4j at {settings.NEO4J_URL}")

    def _test_connection(self):
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j connection test passed")
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            raise RuntimeError("Failed to connect to Neo4j database")
    
    def _init_constraints(self):
        with self.driver.session() as session:
            session.run("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (m:Mod) REQUIRE m.mod_id IS UNIQUE
                        """)
            logger.info("Neo4j constraints initialized.")

    def __del__(self):
        self.driver.close()
        logger.info("Neo4j connection closed.")
    
    def add(self, relation: ModRelation) -> bool:

        query = """
        MERGE (source:Mod {name: $source_name})
        MERGE (target:Mod {name: $target_name})
        MERGE (source)-[r:RELATION {type: $rel_type}]->(target)
        RETURN r        
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, 
                            source_name=relation.source_mod, 
                            target_name=relation.target_mod, 
                            rel_type=relation.relationship_type.value
                        )
                if success := bool(result.single()):
                    logger.info(f"Added relation: {relation.source_mod} -[{relation.relationship_type.value}]-> {relation.target_mod}")
                return success
        except Exception as e:
            logger.error(f"Failed to add relation: {e}")
            return False
            
    
    def search_related(self, mod_name: str) -> List[ModRelation]:
        query = """
        MATCH (source:Mod {name: $mod_name})-[r:RELATION]->(target:Mod)
        RETURN source.name, target.name, r.type
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, mod_name=mod_name)
                relations = [
                    ModRelation(
                        row["source.name"],
                        row["target.name"],
                        row["r.type"]
                    )
                    for row in result
                ]
                logger.info(f"Found {len(relations)} related mods for {mod_name}")
                return relations
        except Exception as e:
            logger.error(f"Failed to search related mods: {e}")
            return []
            
    
    def check_conflict(self, mod_name1: str, mod_name2: str) -> bool:
        query = """
        MATCH (m1:Mod {name: $mod_name1})-[r:RELATION {type: 'conflicts_with'}]->(m2:Mod {name: $mod_name2})
        RETURN r
        UNION
        MATCH (m1:Mod {name: $mod_name1})<-[r:RELATION {type: 'conflicts_with'}]-(m2:Mod {name: $mod_name2})
        RETURN r
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, mod_name1=mod_name1, mod_name2=mod_name2)
                conflict_exists = bool(result.single())
                logger.info(f"Conflict check: {mod_name1} <-> {mod_name2}: {conflict_exists}")
                return conflict_exists
        except Exception as e:
            logger.error(f"Failed to check conflict: {e}")
            return False


graphDB = Neo4jGraphDB()