from pydantic import BaseModel
from utils.memory_handler import MemoryHandler
from utils.response import Response
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Setup class
class ChatbotOrchestrator:

    def __init__(self, faiss_db_path: str, system_prompt: str, memory_db_path: str = "memory_db.xlsx"):
        """
        Initialize the chatbot orchestrator with required components.
        """
        self.model = ChatOpenAI()

        if not os.path.exists(faiss_db_path):
            raise FileNotFoundError(f"FAISS DB path {faiss_db_path} not found.")

        self.retriever = FAISS.load_local(faiss_db_path, OpenAIEmbeddings(),  allow_dangerous_deserialization=True).as_retriever(search_type = "similarity", k = 3)

        self.memory_handler = MemoryHandler(db_path=memory_db_path)
        self.system_prompt = system_prompt

    def chat(self, user_id: str, video_id: str, query: str) -> str:
        """
        Handle a user query and return the AI's response.
        """
        try:
            # Step 1: Initialize the Response Chain
            response_chain = Response(
                model=self.model,
                system_prompt=self.system_prompt,
                user_id=user_id,
                retriever=self.retriever,
                get_history=self.memory_handler.get_history
            )
            
            # Step 2: Generate the AI response
            answer = response_chain.response_chain.invoke({
                "query": query,
                "user_id": user_id,
                "video_id": video_id
            })

            # Step 3: Save the user query in memory (as Human)
            self.memory_handler.add_record({
                "user_id": user_id,
                "video_id": video_id,
                "role": "Human",
                "content": query
            })


            # Step 4: Save the AI response in memory (as AI)
            self.memory_handler.add_record({
                "user_id": user_id,
                "video_id": video_id,
                "role": "AI",
                "content": answer
            })

            return answer

        except Exception as e:
            raise RuntimeError(f"Failed to handle chat interaction: {e}")
        


if __name__== "__main__":
        
    # Instantiate Orchestrator
    orchestrator = ChatbotOrchestrator(     
        faiss_db_path="faiss_transcript_index",        
        system_prompt="You are a helpful assistant.That gives an answer from video transcript {context}"
    )

    try:
        answer = orchestrator.chat(
            user_id="aman.gupta",
            video_id="Gfr50f6ZBvo",
            query="is the topic of nuclear fusion discussed in this video? if yes then what was discussed"
        )
        print(answer)

    except Exception as e:
        raise RuntimeError(f"ChatBot Failed to answer : {e}")

