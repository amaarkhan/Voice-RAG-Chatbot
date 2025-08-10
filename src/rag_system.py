import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
import tempfile
from pathlib import Path
import shutil
import pickle
import google.generativeai as genai

class RAGSystem:
    def __init__(self, google_api_key, persist_directory="./chroma_db"):
        self.google_api_key = google_api_key
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.documents = []
        
        # Configure Google AI
        genai.configure(api_key=google_api_key)
        
        # Initialize embeddings
        self.setup_embeddings()
        
        # Always start with fresh vectorstore
        self.setup_fresh_vectorstore()
        
        # Initialize QA chain
        self.setup_qa_chain()
    
    def setup_embeddings(self):
        """Initialize HuggingFace embeddings"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            st.success("✅ Embeddings model loaded successfully")
        except Exception as e:
            st.error(f"❌ Error loading embeddings: {e}")
            raise
    
    def setup_vectorstore(self):
        """Initialize or load existing Chroma vectorstore"""
        try:
            if os.path.exists(self.persist_directory):
                # Load existing vectorstore
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                try:
                    count = self.vectorstore._collection.count()
                    st.info(f"📚 Loaded existing knowledge base with {count} documents")
                except:
                    st.info("📚 Loaded existing knowledge base")
            else:
                # Create new vectorstore
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                st.info("🆕 Created new knowledge base")
        except Exception as e:
            st.error(f"❌ Error setting up vectorstore: {e}")
            raise
    
    def setup_fresh_vectorstore(self):
        """Always create a fresh vectorstore without loading existing data"""
        try:
            # Remove existing directory if it exists
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
            
            # Create new vectorstore
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            st.info("🆕 Created fresh knowledge base")
        except Exception as e:
            st.error(f"❌ Error setting up fresh vectorstore: {e}")
            raise
    
    def setup_qa_chain(self):
        """Initialize the QA chain with Google Gemini"""
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.7,
                google_api_key=self.google_api_key,
                max_output_tokens=512
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True
            )
            st.success("✅ QA chain initialized successfully with Google Gemini")
        except Exception as e:
            st.error(f"❌ Error setting up QA chain: {e}")
            raise
    
    def load_document(self, file_path, file_type):
        """
        Load a document based on its type
        
        Args:
            file_path: Path to the document
            file_type: Type of document (pdf, txt, docx)
            
        Returns:
            list: List of loaded documents
        """
        try:
            if file_type.lower() == 'pdf':
                loader = PyPDFLoader(file_path)
            elif file_type.lower() == 'txt':
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_type.lower() in ['docx', 'doc']:
                loader = UnstructuredWordDocumentLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            documents = loader.load()
            return documents
            
        except Exception as e:
            st.error(f"❌ Error loading document {file_path}: {e}")
            return []
    
    def process_documents(self, uploaded_files):
        """
        Process uploaded files and add them to the vectorstore
        
        Args:
            uploaded_files: List of uploaded Streamlit files
            
        Returns:
            int: Number of documents successfully processed
        """
        processed_count = 0
        
        # Text splitter for chunking documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        for uploaded_file in uploaded_files:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
                
                # Determine file type
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                # Load document
                documents = self.load_document(temp_file_path, file_extension)
                
                if documents:
                    # Split documents into chunks
                    texts = text_splitter.split_documents(documents)
                    
                    # Add metadata
                    for text in texts:
                        text.metadata['source'] = uploaded_file.name
                        text.metadata['file_type'] = file_extension
                    
                    # Add to vectorstore
                    self.vectorstore.add_documents(texts)
                    self.documents.extend(texts)
                    
                    processed_count += 1
                    st.success(f"✅ Processed: {uploaded_file.name} ({len(texts)} chunks)")
                
                # Clean up temporary file
                os.unlink(temp_file_path)
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {e}")
        
        if processed_count > 0:
            # Documents are automatically persisted in newer Chroma versions
            st.success(f"🎉 Successfully processed {processed_count} documents!")
        
        return processed_count
    
    def add_text_document(self, text_content, document_name="Manual Entry"):
        """
        Add text content directly to the knowledge base
        
        Args:
            text_content: Raw text content
            document_name: Name for the document
            
        Returns:
            bool: Success status
        """
        try:
            # Text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            # Create document object
            from langchain.schema import Document
            doc = Document(
                page_content=text_content,
                metadata={
                    'source': document_name,
                    'file_type': 'text'
                }
            )
            
            # Split into chunks
            texts = text_splitter.split_documents([doc])
            
            # Add to vectorstore
            self.vectorstore.add_documents(texts)
            self.documents.extend(texts)
            
            # Documents are automatically persisted in newer Chroma versions
            
            st.success(f"✅ Added text document: {document_name}")
            return True
            
        except Exception as e:
            st.error(f"❌ Error adding text document: {e}")
            return False
    
    def query_knowledge_base(self, question):
        """
        Query the knowledge base with a question
        
        Args:
            question: User's question
            
        Returns:
            dict: Response with answer and source documents
        """
        try:
            if not self.qa_chain:
                return {
                    "answer": "❌ QA system not initialized. Please check your Google API key.",
                    "source_documents": []
                }
            
            if self.vectorstore._collection.count() == 0:
                return {
                    "answer": "📚 No documents in knowledge base. Please upload some documents first.",
                    "source_documents": []
                }
            
            # Query the knowledge base
            response = self.qa_chain.invoke({"query": question})
            
            return {
                "answer": response["result"],
                "source_documents": response.get("source_documents", [])
            }
            
        except Exception as e:
            st.error(f"❌ Error querying knowledge base: {e}")
            return {
                "answer": f"❌ Error processing your question: {str(e)}",
                "source_documents": []
            }
    
    def get_knowledge_base_stats(self):
        """Get statistics about the knowledge base"""
        try:
            if not self.vectorstore:
                return {"total_documents": 0, "sources": []}
            
            total_docs = self.vectorstore._collection.count()
            
            # Get unique sources
            sources = set()
            for doc in self.documents:
                if 'source' in doc.metadata:
                    sources.add(doc.metadata['source'])
            
            return {
                "total_documents": total_docs,
                "sources": list(sources)
            }
            
        except Exception as e:
            st.error(f"❌ Error getting stats: {e}")
            return {"total_documents": 0, "sources": []}
    
    def clear_knowledge_base(self):
        """Clear all documents from the knowledge base"""
        try:
            # Clear documents list first
            self.documents = []
            
            # Close current vectorstore connection to release file locks
            if self.vectorstore:
                try:
                    # Try to close the connection properly
                    if hasattr(self.vectorstore, '_client'):
                        self.vectorstore._client.reset()
                    self.vectorstore = None
                except:
                    pass  # Ignore errors when closing
            
            # Wait a moment for files to be released
            import time
            time.sleep(1)
            
            # Try to remove the directory
            try:
                if os.path.exists(self.persist_directory):
                    shutil.rmtree(self.persist_directory)
                    st.success("🗑️ Knowledge base directory cleared")
            except PermissionError:
                # If we can't delete, just recreate a fresh vectorstore
                st.warning("⚠️ Could not delete old files, creating fresh database")
            
            # Always create a fresh vectorstore
            self.setup_fresh_vectorstore()
            
            st.success("✅ Knowledge base cleared successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error clearing knowledge base: {e}")
            # Try to at least create a fresh vectorstore
            try:
                self.setup_fresh_vectorstore()
                st.info("🔄 Created new knowledge base")
            except:
                pass
            return False
