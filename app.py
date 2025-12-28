

from src.loaders import ChatMessageVectorRepository
from src.extractors import ingest_data

chat_repo = ChatMessageVectorRepository()
def query_db(query:str):
    user_ids = chat_repo.get_messages(query=query,result_count=3, threshold=0.5)
    print(f"Relevant users for the query: {query}\nUser IDs: {user_ids}")

def main():
    # ingest_data("data/chats.json")
    
    #  query_db(query="Users asking for financial investment advice.")
    query_db(query=" cooking chocolate chip cookies.")
if __name__ == "__main__":
    main()