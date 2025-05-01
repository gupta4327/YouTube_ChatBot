from main_response import ChatbotOrchestrator
from main_ingestion import FAISSVectorStoreManager


def get_bot_response(user_id, video_id, query):

    orchestrator = ChatbotOrchestrator(     
        faiss_db_path="faiss_transcript_index",        
        system_prompt="You are a helpful assistant.That gives an answer from video transcript {context}"
    )

    try:
        answer = orchestrator.chat(
            user_id=user_id,
            video_id=video_id,
            query=query
        )
        return answer

    except Exception as e:
        raise RuntimeError(f"ChatBot Failed to answer : {e}")
    

def get_available_videos():
    vs = FAISSVectorStoreManager()
    videos = vs.get_available_videos()
    return videos