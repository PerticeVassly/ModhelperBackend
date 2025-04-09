from .base import (
    ModMetadata,
    ModPlatform,
    ModRelation,
    ModRelationType,
    BaseMetadataDB,
    BaseVectorDB,
    BaseGraphDB
)
from .sqlite3_manager import relationDB
from .chroma_manager import vectorDB
from .neo4j_manager import graphDB
from .mongodb_manager import usersCollection, conversationsCollection, messagesCollection
from config.logging_config import setup_logging

__all__ = [
    "relationDB",
    "vectorDB",
    "graphDB",
    "ModMetadata",
    "ModPlatform",
    "ModRelation",
    "ModRelationType",
    "usersCollection",
    "conversationsCollection",
    "messagesCollection",
]

setup_logging()
