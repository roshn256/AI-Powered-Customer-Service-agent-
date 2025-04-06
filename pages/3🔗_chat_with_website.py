import os
import json
import shutil
import time
import utils
import requests
import traceback
import validators
import streamlit as st
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from streaming import StreamHandler

import PyPDF2
import docx2txt

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

st.set_page_config(page_title="Chat with Websites & Docs", page_icon="🤖")
st.header('AI Powered Customer Service Agent')
st.write('Chat with both website content and uploaded documents')

class ChatAssistant:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        self.embedding_model = utils.configure_embedding_model()
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.load_sources()

    def load_sources(self):
        if os.path.exists("sources.json"):
            with open("sources.json", "r") as f:
                st.session_state["sources"] = json.load(f)

    def save_sources(self):
        with open("sources.json", "w") as f:
            json.dump(st.session_state.get("sources", []), f)

    def is_same_domain(self, base_url, check_url):
        base_domain = urlparse(base_url).netloc
        check_domain = urlparse(check_url).netloc
        return base_domain == check_domain

    def crawl_website(self, base_url, max_pages=20, delay=1.0):
        urls_to_visit = [base_url]
        collected_urls = []
        self.visited_urls.clear()
        max_retries = 2

        while urls_to_visit and len(collected_urls) < max_pages:
            current_url = urls_to_visit.pop(0)
            if current_url in self.visited_urls:
                continue
            
            retries = 0
            success = False
            while retries <= max_retries and not success:
                try:
                    response = self.session.get(current_url, timeout=20)
                    if response.status_code == 200:
                        success = True
                        time.sleep(delay)
                    else:
                        st.sidebar.warning(f"HTTP {response.status_code} at {current_url}")
                        break
                except Exception as e:
                    if retries == max_retries:
                        st.sidebar.error(f"Failed to fetch {current_url} after {max_retries} retries: {str(e)}")
                        break
                    retries += 1
                    time.sleep(delay * retries)

            if not success:
                continue

            if 'text/html' not in response.headers.get('Content-Type', ''):
                st.sidebar.warning(f"Skipping non-HTML content at {current_url}")
                continue

            self.visited_urls.add(current_url)
            collected_urls.append(current_url)
            st.sidebar.info(f"🌐 Crawling: {current_url}")

            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href'].split('#')[0].split('?')[0].strip()
                    if href and not href.startswith(('mailto:', 'tel:', 'javascript:')):
                        full_url = urljoin(current_url, href)
                        if (validators.url(full_url) and 
                            self.is_same_domain(base_url, full_url) and 
                            full_url not in self.visited_urls and 
                            full_url not in urls_to_visit):
                            urls_to_visit.append(full_url)
            except Exception as e:
                st.sidebar.error(f"Error parsing {current_url}: {str(e)}")

        return collected_urls

    def scrape_page(self, url):
        try:
            proxy_url = f"https://r.jina.ai/{url}"
            response = self.session.get(proxy_url, timeout=25)
            response.raise_for_status()
            
            if len(response.text) < 500:
                st.warning(f"Page {url} contains minimal content - may not be useful")
                
            return response.text
        except requests.exceptions.HTTPError as e:
            st.error(f"Proxy error ({e.response.status_code}) for {url}")
        except Exception as e:
            st.error(f"Failed to scrape {url}: {str(e)}")
        return None

    def process_document(self, file):
        try:
            if file.type == "application/pdf":
                text = []
                pdf = PyPDF2.PdfReader(file)
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if not page_text.strip():
                        st.warning(f"Page {i+1} in {file.name} appears empty")
                    text.append(page_text)
                return "\n".join(text)
            elif file.type == "text/plain":
                return file.read().decode("utf-8")
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return docx2txt.process(file)
            return None
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            return None

    def handle_file_upload(self, uploaded_files):
        if not uploaded_files:
            return

        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        total_files = len(uploaded_files)

        vectordb = Chroma(
            persist_directory="chroma_store",
            embedding_function=self.embedding_model
        )

        for i, file in enumerate(uploaded_files):
            status_text.text(f"📄 Processing {i+1}/{total_files}: {file.name}")
            progress_bar.progress((i+1)/total_files)

            content = self.process_document(file)
            if not content:
                continue

            doc = Document(
                page_content=content,
                metadata={"source": f"📄 {file.name}"}
            )

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=300
            )
            splits = text_splitter.split_documents([doc])
            
            try:
                vectordb.add_documents(splits)
                vectordb.persist()
                st.session_state.sources.append(f"📄 {file.name}")
                st.sidebar.success(f"✅ Processed: {file.name}")
            except Exception as e:
                st.sidebar.error(f"❌ Error adding {file.name}: {str(e)}")

        progress_bar.empty()
        status_text.success("🎉 All files processed!")
        self.save_sources()

    def setup_vectordb(self):
        try:
            return Chroma(
                persist_directory="chroma_store",
                embedding_function=self.embedding_model
            )
        except Exception as e:
            st.error(f"VectorDB error: {str(e)}")
            return None

    def setup_qa_chain(self):
        vectordb = self.setup_vectordb()
        if not vectordb:
            return None

        retriever = vectordb.as_retriever(
            search_type='mmr',
            search_kwargs={
                'k': 5,
                'fetch_k': 15,
                'lambda_mult': 0.75
            }
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
            verbose=True
        )

    @utils.enable_chat_history
    def main(self):
        if "sources" not in st.session_state:
            st.session_state["sources"] = []

        with st.sidebar:
            st.header("Data Management Panel")
            
            # Website Input Section
            st.subheader("Website Input")
            web_url = st.text_area(
                "Enter website URLs (one per line):",
                height=100,
                placeholder="https://example.com\nhttps://another-site.org",
                help="Enter base URLs of websites to crawl"
            )
            
            # Crawler Settings
            st.subheader("Crawler Settings")
            col1, col2 = st.columns(2)
            with col1:
                max_pages = st.number_input("Max Pages", 5, 100, 20)
            with col2:
                crawl_delay = st.number_input("Delay (sec)", 0.5, 5.0, 1.0)
            
            if st.button("🌐 Add Websites", help="Start website crawling process"):
                self.handle_website_input(web_url, max_pages, crawl_delay)

            # Document Upload Section
            st.subheader("Document Upload")
            uploaded_files = st.file_uploader(
                "Drag and drop or click to upload files",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                help="Upload PDF, DOCX, or TXT files",
                label_visibility="visible"
            )
            if uploaded_files:
                st.info(f"📁 {len(uploaded_files)} files ready for processing")
            
            if st.button("📁 Process Documents", help="Process uploaded documents"):
                self.handle_file_upload(uploaded_files)

            # Data Management
            st.subheader("System Controls")
            if st.button("🗑️ Clear All Data", type="primary", help="Wipe all stored data"):
                self.clear_all_data()

        # Main Chat Interface
        qa_chain = self.setup_qa_chain()
        if not qa_chain:
            st.error("No data loaded! Please add websites or documents first.")
            st.stop()

        user_query = st.chat_input(placeholder="Ask about website content or documents...")
        if user_query:
            utils.display_msg(user_query, 'user')
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                try:
                    result = qa_chain.invoke(
                        {"question": user_query},
                        {"callbacks": [st_cb]}
                    )
                    response = result["answer"]
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

                    with st.expander("📚 View Sources"):
                        for idx, doc in enumerate(result['source_documents'], 1):
                            source = doc.metadata['source']
                            if source.startswith("📄"):
                                st.markdown(f"**Document {idx}:** {source[2:]}")
                            else:
                                st.markdown(f"**Website {idx}:** [{source}]({source})")
                            st.caption(doc.page_content[:400] + "...")
                            
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    traceback.print_exc()

    def handle_website_input(self, input_urls, max_pages, crawl_delay):
        urls = [url.strip() for url in input_urls.split('\n') if url.strip()]
        new_urls = []
        
        for url in urls:
            if not validators.url(url):
                st.error(f"Invalid URL: {url}")
                continue
                
            if url in st.session_state.get("sources", []):
                st.warning(f"Already exists: {url}")
                continue
                
            if self.process_website(url, max_pages, crawl_delay):
                new_urls.append(url)
                st.session_state.sources.append(url)

        if new_urls:
            st.success(f"Added {len(new_urls)} new websites!")
            self.save_sources()

    def process_website(self, url, max_pages, crawl_delay):
        subpages = self.crawl_website(url, max_pages, crawl_delay)
        if not subpages:
            st.error(f"No pages found at {url}")
            return False

        vectordb = Chroma(
            persist_directory="chroma_store",
            embedding_function=self.embedding_model
        )

        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        total_pages = len(subpages)

        for i, page_url in enumerate(subpages):
            status_text.text(f"🌐 Processing page {i+1}/{total_pages}")
            progress_bar.progress((i+1)/total_pages)
            
            content = self.scrape_page(page_url)
            if not content:
                continue
                
            doc = Document(
                page_content=content,
                metadata={"source": page_url}
            )
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=300
            )
            splits = text_splitter.split_documents([doc])
            
            try:
                vectordb.add_documents(splits)
                vectordb.persist()
            except Exception as e:
                st.error(f"Error adding {page_url}: {str(e)}")

        progress_bar.empty()
        status_text.success(f"✅ Finished processing {url}")
        return True

    def clear_all_data(self):
        st.session_state["sources"] = []
        if os.path.exists("chroma_store"):
            shutil.rmtree("chroma_store")
        if os.path.exists("sources.json"):
            os.remove("sources.json")
        st.rerun()

if __name__ == "__main__":
    assistant = ChatAssistant()
    assistant.main()