# vectorstore_utils.py

import os
import asyncio
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from utils.youtube_transcript_processor import AsyncYouTubeTranscriptProcessor  # Ensure this is in the same directory or installed as a module
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

class FAISSVectorStoreManager:

    def __init__(self, db_dir: str = "faiss_transcript_index", embedding_model=None):
        self.db_dir = db_dir
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.vectorstore = self._load_or_initialize_faiss()

    def _load_or_initialize_faiss(self):
        """
        Load FAISS vector store from disk if available; otherwise, initialize a new one.
        """
        if os.path.exists(self.db_dir):
            print(f"[INFO] Loading existing FAISS vector store from: {self.db_dir}")
            return FAISS.load_local(self.db_dir, self.embedding_model, allow_dangerous_deserialization=True)
        else:
            print(f"[INFO] No existing FAISS index found. Initializing a new vector store.")
            return FAISS.from_documents([Document(page_content="Init doc", metadata={"source": "init"})], self.embedding_model)

    def save_faiss(self):
        """
        Save the current FAISS index to disk.
        """
        print(f"[INFO] Saving FAISS index to: {self.db_dir}")
        self.vectorstore.save_local(self.db_dir)

    async def ingest_youtube_videos(self, video_ids: list[str]):
        """
        Ingest YouTube video transcripts into the FAISS vector store.
        """
        processor = AsyncYouTubeTranscriptProcessor(
            embedding_model=self.embedding_model,
            vector_store=self.vectorstore
        )

        await processor.batch_process_video_ids(video_ids)
        self.save_faiss()
        print(f"[INFO] Successfully ingested {len(video_ids)} video(s).")

    def get_available_videos(self):
        # Get all document metadata
        metadatas = list(self.vectorstore.docstore._dict.values())
        #print(type(metadatas))
        video_metadata = {}
        for doc in metadatas:
            meta = doc.metadata
            if "video_id" in meta:
                channel = meta["channel"]
                title = meta["title"]
                video_name = channel + " - " + title
                video_id = meta["video_id"]
                video_metadata[video_name] = video_id
               
        return video_metadata


# Example usage
if __name__ == "__main__":
    async def main():
        video_ids = ["Gfr50f6ZBvo"]  # replace with your list of video IDs
        vectorstore_manager = FAISSVectorStoreManager()
        print(vectorstore_manager.get_available_videos())
        #await vectorstore_manager.ingest_youtube_videos(video_ids)

    asyncio.run(main())
