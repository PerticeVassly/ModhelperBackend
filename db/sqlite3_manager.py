import sqlite3
import logging
from typing import Optional
from .base import BaseMetadataDB, ModMetadata
from config import settings
from pathlib import Path

logger = logging.getLogger("database")

class SQLiteMetadataDB:
    def __init__(self):
        db_path = Path(settings.SQLITE_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._create_table()
        logger.info(f"Connected to SQLite database at {db_path}")

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mod_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    tags TEXT NOT NULL DEFAULT '[]',
                    description TEXT NOT NULL,
                    support_platform TEXT CHECK(support_platform IN ('java', 'bedrock', 'cross-platform')),
                    download_url TEXT
                )
            """)
            logger.info("Table `mod_info` checked/created successfully.")
    
    def add(self, mod: ModMetadata) -> bool:
        try:
            cursor = self.conn.cursor()    
            self.conn.execute(
                "INSERT INTO mod_info (name, tags, description, support_platform, download_url) VALUES (?, ?, ?, ?, ?)",
                (mod.name, ",".join(mod.tags), mod.description, mod.support_platform.value, mod.download_url)
            )
            self.conn.commit()
            logger.info(f"Added mod {mod.name} successfully.")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Mod {mod.name} already exists in database.")
            return False
    
    def get(self, name: str) -> Optional[ModMetadata]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mod_info WHERE name = ?", (name,))
        if row := cursor.fetchone():
            return ModMetadata(
                name=row[1],
                tags=row[2].split(","),
                description=row[3],
                support_platform=row[4],
                download_url=row[5]
            )
        logger.warning(f"Mod {name} not found.")
        return None

    def get_all_mod_names(self) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM mod_info")
        mod_names = [row[0] for row in cursor.fetchall()]
        logger.info(f"Retrieved all mod names: {mod_names}")
        return mod_names
    
    def search(self, keyword: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mod_info WHERE name LIKE ? OR description LIKE ?",
            (f"%{keyword}%", f"%{keyword}%"))
        results = [ModMetadata(
                name=row[1],
                tags=row[2].split(","),
                description=row[3],
                support_platform=row[4],
                download_url=row[5]
            ) for row in cursor.fetchall()]
        logger.info(f"Search for '{keyword}' returned {len(results)} results.")
        return results
    
    def __del__(self):
        self.conn.close()
        logger.info("SQLite connection closed.")

relationDB = SQLiteMetadataDB()