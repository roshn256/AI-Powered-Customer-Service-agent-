import os
import utils
import hashlib
import streamlit as st
from streaming import StreamHandler

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


st.set_page_config(page_title="VJCET Document Chat", page_icon="🏛️")
st.markdown("""
<style>
    .header-section {
        background: linear-gradient(45deg, #004aad, #002850);
        color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-bubble {
        background: #004aad;
        color: #ffffff;
        margin-left: auto;
        border: 1px solid #002850;
    }
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.9);
        color: #000000;
        border: 1px solid #e0e0e0;
    }
    .hover-effect {
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .hover-effect:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .button-hover-effect:hover {
        background: #001529;
        transform: scale(1.05);
    }
    .popover-section {
        background: rgba(240, 248, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e0e0e0;
    }
    .popover-section:hover {
        background: rgba(240, 248, 255, 1);
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="header-section hover-effect"><h1>📚 VJCET Intelligent Document Assistant</h1></div>', unsafe_allow_html=True)
st.write('Chat with college documents and get instant answers about policies, procedures, and academic matters')

class PersistentDocChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        self.embedding_model = utils.configure_embedding_model()
        self.vector_store_path = "vjcet_vector_store"
        self.processed_hashes_path = "processed_hashes.txt"

    def save_file(self, file):
        """Save uploaded file to temporary directory"""
        folder = 'uploaded_docs'
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        return file_path

    def load_existing_hashes(self):
        """Load set of processed file hashes"""
        if os.path.exists(self.processed_hashes_path):
            with open(self.processed_hashes_path, 'r') as f:
                return set(f.read().splitlines())
        return set()

    def update_vector_store(self, uploaded_files):
        """Process new documents and update persistent vector store"""
        processed_hashes = self.load_existing_hashes()
        new_docs = []
        
        for file in uploaded_files:
            file_hash = hashlib.sha256(file.getvalue()).hexdigest()
            if file_hash not in processed_hashes:
                file_path = self.save_file(file)
                loader = PyPDFLoader(file_path)
                new_docs.extend(loader.load())
                processed_hashes.add(file_hash)
        
        if new_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(new_docs)
            
            if os.path.exists(self.vector_store_path):
                vectordb = FAISS.load_local(self.vector_store_path, self.embedding_model, allow_dangerous_deserialization=True)
                vectordb.add_documents(splits)
            else:
                vectordb = FAISS.from_documents(splits, self.embedding_model)
            
            vectordb.save_local(self.vector_store_path)
            with open(self.processed_hashes_path, 'w') as f:
                f.write('\n'.join(processed_hashes))

    def get_qa_chain(self):
        """Create conversation chain with persistent vector store"""
        vectordb = FAISS.load_local(self.vector_store_path, self.embedding_model, allow_dangerous_deserialization=True)
        
        retriever = vectordb.as_retriever(
            search_type='mmr',
            search_kwargs={'k': 2, 'fetch_k': 4}
        )

        memory = ConversationBufferMemory(
            memory_key='chat_history',
            output_key='answer',
            return_messages=True
        )

        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=False
        )

    @utils.enable_chat_history
    def main(self):
        # Document upload section
        uploaded_files = st.sidebar.file_uploader(
            label='Upload new PDF documents',
            type=['pdf'],
            accept_multiple_files=True
        )

        # Process new documents if any
        if uploaded_files:
            self.update_vector_store(uploaded_files)
            st.sidebar.success(f"Processed {len(uploaded_files)} new documents")

        # Check for existing knowledge base
        if not os.path.exists(self.vector_store_path):
            st.error("No documents in knowledge base. Please upload initial documents!")
            return

        # Chat interface
        user_query = st.chat_input(placeholder="Ask about VJCET policies, academics, or procedures...")
        if user_query:
            qa_chain = self.get_qa_chain()
            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                result = qa_chain.invoke(
                    {"question": user_query},
                    {"callbacks": [st_cb]}
                )
                response = result["answer"]
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Display references
                for idx, doc in enumerate(result['source_documents'], 1):
                    filename = os.path.basename(doc.metadata['source'])
                    page_num = doc.metadata['page']
                    with st.popover(f"📖 Reference {idx}: {filename} (Page {page_num})"):
                        st.markdown(f"**Excerpt from page {page_num}:**")
                        st.caption(doc.page_content)

if __name__ == "__main__":
    obj = PersistentDocChatbot()
    obj.main()