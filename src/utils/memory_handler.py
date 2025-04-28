import pandas as pd
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from langchain_core.messages import AIMessage, HumanMessage
import os

class MemoryHandler:
    def __init__(self, db_path: str = "memory_db.xlsx"):
        """
        Initialize MemoryHandler. Loads memory dataframe from file or creates a new one.
        """
        self.db_path = db_path
        
        if os.path.exists(self.db_path):
            try:
                self.memory_df = pd.read_excel(self.db_path)
            except Exception as e:
                raise RuntimeError(f"Failed to load existing memory database: {e}")
        else:
            # Create a new DataFrame if no file exists
            self.memory_df = pd.DataFrame(columns=["id", "timestamp", "user_id", "video_id", "role", "content"])

    
    def _cleanup_old_records(self):
        """
        Remove records older than 15 minutes from memory.
        """
        try:
            ist_curr_time = datetime.now(ZoneInfo("Asia/Kolkata"))
            time_15min_prior = ist_curr_time - timedelta(minutes=15)

            # Filter only fresh records
            self.memory_df = self.memory_df[self.memory_df["timestamp"] > time_15min_prior]

        except Exception as e:
            raise RuntimeError(f"Error cleaning old records: {e}")

    def get_history(self, user_id: str, video_id: str):
        """
        Fetch chat history for a user and video within the last 15 minutes.
        """
        messages = []
        try:
            # Current IST time
            ist_curr_time = datetime.now(ZoneInfo("Asia/Kolkata"))
            time_15min_prior = ist_curr_time - timedelta(minutes=15)

            # Filter out old messages
            self.memory_df = self.memory_df[self.memory_df["timestamp"] > time_15min_prior]

            # Filter relevant history
            history_df = self.memory_df[
                (self.memory_df["user_id"] == user_id) & (self.memory_df["video_id"] == video_id)
            ].sort_values(by="timestamp", ascending=True)

            for _, row in history_df.iterrows():
                message_row = dict(row)
                if message_row["role"] == "AI":
                    messages.append(AIMessage(message_row["content"]))
                elif message_row["role"] == "Human":
                    messages.append(HumanMessage(message_row["content"]))
                else:
                    print(f"Discarding message: {message_row['content']} as role is neither AI nor Human")

            return messages

        except Exception as e:
            raise RuntimeError(f"Error fetching chat history: {e}")

    def add_record(self, data: dict):
        """
        Add a new record to memory and persist after cleaning old records.
        """
        try:
            record_id = str(uuid.uuid4())
            ing_data = {key: [value] for key, value in data.items()}
            ing_data["id"] = [record_id]
            ing_data["timestamp"] = [datetime.now(ZoneInfo("Asia/Kolkata"))]

            add_df = pd.DataFrame(ing_data)

            self.memory_df = pd.concat([self.memory_df, add_df], ignore_index=True)

            # Clean old records before saving
            self._cleanup_old_records()

            self.memory_df.to_excel(self.db_path, index=False)

        except Exception as e:
            raise RuntimeError(f"Error adding new record: {e}")
