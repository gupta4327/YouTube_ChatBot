from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class Response:

    def __init__(self, model, system_prompt:str, user_id:str, retriever, get_history, parser=None):

        self.model = model
        self.system_prompt = system_prompt
        self.user_id = user_id
        self.retriever = retriever
        self.get_history = get_history
        self.parser = parser or StrOutputParser()
        self.build_chain()

    def get_prompt(self):

        prompt = ChatPromptTemplate.from_messages([("system", self.system_prompt), 
                                    MessagesPlaceholder(variable_name="message_history"),
                                    ("human", "{query}")])
        
        return prompt
        

    def format_docs(self,docs: list) -> str:

        context = " ".join(doc.page_content for doc in docs)
        return context
    
    def get_query(self, input_dict:dict)->str:
        return input_dict["query"]
    
    def get_memory_inputs(self, input_dict:dict)->dict:

        input_copy = input_dict.copy()
        input_copy.pop("query")
        print(input_copy)
        return input_copy
        

    def build_chain(self): 

        prompt = self.get_prompt()

        query_chain = RunnableLambda(self.get_query)
        context_chain = RunnableLambda(self.get_query)|self.retriever | RunnableLambda(self.format_docs)
        memory_chain = RunnableLambda(self.get_memory_inputs)|RunnableLambda(lambda x: self.get_history(x["user_id"], x["video_id"]))

        prompt_input_chain = RunnableParallel({"query": query_chain,
                                          "context": context_chain, 
                                          "message_history": memory_chain})
        
        self.response_chain = prompt_input_chain|prompt|self.model|self.parser

    def response(self, query, video_id):

        self.response_chain.invoke({"query":query, "user_id": self.user_id, "video_id": video_id})




