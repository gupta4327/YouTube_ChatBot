from langchain_community.vectorstores import FAISS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from pytube import YouTube
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import asyncio

class AsyncYouTubeTranscriptProcessor:

    def __init__(self, embedding_model, vector_store, splitter= None): 
        
        self.vectorstore = vector_store
        self.splitter = splitter or RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        self.embedding_model = embedding_model
     
    async def _fetch_video_metadata(self, video_id):

        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            yt = await asyncio.to_thread(YouTube, video_url)
            video_metadata = {"video_id": self.video_id, 
                                "title": yt.title,
                                "channel": yt.author, 
                                "published": yt.publish_date, 
                                "video_url": video_url}
            
            return video_metadata
        
        except Exception as e:

            raise RuntimeError(f"Error in extracting metadata for video : {e}")
    

    
    async def _fetch_transcript(self, video_id):
        
        try:
            transcript_list = await asyncio.to_thread(lambda : YouTubeTranscriptApi.get_transcript(self.video_id, languages=["en"]))
            transcript = " ".join(trans["text"] for trans in transcript_list)
            return transcript
        
        except TranscriptsDisabled:
            raise ValueError("Transcript is disabled for this video")
        
        except Exception as e:
            raise RuntimeError(f"failed in fetching metadata for video {video_id} with error : {e}")
    
    def _document_splitter(self, transcript, metadata):

        try:

            doc = Document(page_content=transcript)
            doc.metadata = metadata

            docs = self.splitter.split_documents([doc])
            
            return docs
        except Exception as e:
            raise RuntimeError(f"failed in splitting the document with error : {e}")

    def _ingest_vectorstore(self, docs):

        try:
        
            self.vectorstore.add_documents(docs)
        
        except Exception as e:
            raise RuntimeError(f"Failed in storing a document to vector store : {e}")

    async def process_video(self, video_id):

        metadata = await self._fetch_video_metadata(video_id)
        transcript =  await self._fetch_transcript(video_id)
        docs = self._document_splitter(transcript= transcript, metadata=metadata)
        self._ingest_vectorstore(docs=docs)

    def get_vectorstore_retriever(self, search_type = "similarity", k =3, **kwargs):

        retriever = self.vectorstore.as_retriever(search_type = search_type, k= k) 
        return retriever   
    
    async def batch_process_video_ids(self, video_ids):
        await asyncio.gather(*(self.process_video(vid) for vid in video_ids))

        
    


    