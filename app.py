# # import Settings from llama_index.core
# from llama_index.core import Settings

# # import Ollama from llama_index.llms.ollama
# from llama_index.llms.ollama import Ollama

# # import FastEmbedEmbedding from llama_index.embeddings.fastembed
# from llama_index.embeddings.fastembed import FastEmbedEmbedding

# # create an instance of FastEmbedEmbedding with the specified model name
# embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

# # create an instance of Ollama with the specified model and request timeout
# llama3 = Ollama(model="llama3:8b-instruct-q5_1", request_timeout=60.0)

# # set the llm and embed_model in Settings
# Settings.llm = llama3
# Settings.embed_model = embed_model

# # import glob to find all matching file paths
# import glob

# # import Path from pathlib to handle file paths
# from pathlib import Path

# # import SimpleDirectoryReader from llama_index.core
# from llama_index.core import SimpleDirectoryReader

# # initialize an empty list to store documents for summary
# docs_for_summary = []

# # loop through all pdf files in the specified directory
# for file_path in glob.glob("./documents/*.pdf"):

#     # get the file name without extension
#     file_name = Path(file_path).stem

#     # read the document using SimpleDirectoryReader
#     docs = SimpleDirectoryReader(input_files=[file_path]).load_data()

#     # set the document ID to the file name
#     docs[0].doc_id = file_name

#     # extend the docs_for_summary list with the documents
#     docs_for_summary.extend(docs)

# # import DocumentSummaryIndex from llama_index.core
# from llama_index.core import DocumentSummaryIndex

# # import SentenceSplitter from llama_index.core.node_parser
# from llama_index.core.node_parser import SentenceSplitter

# # import get_response_synthesizer from llama_index.core
# from llama_index.core import get_response_synthesizer

# # create an instance of SentenceSplitter with the specified chunk size
# splitter = SentenceSplitter(chunk_size=1024)

# # get a response synthesizer with the specified response mode and async usage
# response_synthesizer = get_response_synthesizer(
#     response_mode="tree_summarize", use_async=True
# )

# # create a DocumentSummaryIndex from the documents for summary
# doc_summary_index = DocumentSummaryIndex.from_documents(
#     docs_for_summary,
#     transformations=[splitter],
#     response_synthesizer=response_synthesizer,
#     show_progress=True,
#     streaming=True,
# )
# # import Markdown and display from IPython.display
# from IPython.display import Markdown, display

# # get the document summary for "RAGAs" from the doc_summary_index
# summary = doc_summary_index.get_document_summary("RAGAs")

# # display the summary in Markdown format
# display(Markdown(str(summary)))

# """
# The provided text appears to be a research paper or article discussing the evaluation of Retrieval-Augmented Generation (RAG) systems. The authors propose a framework for automated reference-free evaluation, introducing a dataset called WikiEval and metrics such as RAGAs to assess faithfulness, answer relevance, and context relevance.

# This text can answer questions related to the evaluation of RAG systems, such as:

# - How do the proposed metrics (RAGAs) compare to baseline methods in evaluating faithfulness, answer relevance, and context relevance?
# - What is the accuracy of the human annotators' judgments on the WikiEval dataset?
# - How do different quality dimensions (faithfulness, answer relevance, and context relevance) affect the evaluation of RAG systems?
# - Can RAGAs provide valuable insights for developers of RAG systems even in the absence of ground truth?

# The text can also be used to explore the implications of automated reference-free evaluation for natural language processing tasks.
# """

# # setup a query engine
# query_engine = doc_summary_index.as_query_engine(
#     response_mode="tree_summarize", use_async=True
# )

# # query the engine with a specific question
# response = query_engine.query("Why is automated evaluation important for RAG systems?")
# display(Markdown(str(response)))
# """
# Automated evaluation of retrieval-augmented systems is important because their implementation requires a significant amount of tuning, as the overall performance will be affected by various factors such as the retrieval model, considered corpus, language model, and prompt formulation.
# """





import os
import base64
import gc
import uuid
from pathlib import Path
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, get_response_synthesizer
from llama_index.core import DocumentSummaryIndex
from llama_index.core.node_parser import SentenceSplitter
import streamlit as st

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
    st.session_state.processing = False
    st.session_state.messages = []

session_id = st.session_state.id

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5")
llama3 = Ollama(model="llama3:8b-instruct-q5_1", request_timeout=60.0)

Settings.llm = llama3
Settings.embed_model = embed_model

# Ensure the documents directory exists
os.makedirs("./documents", exist_ok=True)

# Load existing documents from the directory
def load_existing_documents():
    for file_name in os.listdir("./documents"):
        file_path = os.path.join("./documents", file_name)
        if os.path.isfile(file_path) and file_name.endswith(".pdf"):
            st.session_state.file_cache[file_name] = file_path

def reset_app():
    st.session_state.file_cache = {}
    st.session_state.messages = []
    gc.collect()

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf" style="height:100vh; width:100%"></iframe>"""
    st.markdown(pdf_display, unsafe_allow_html=True)

def process_and_summarize_selected_doc(file_path):
    file_name = Path(file_path).stem
    docs = SimpleDirectoryReader(input_files=[file_path]).load_data()[:1]
    docs[0].doc_id = file_name

    splitter = SentenceSplitter(chunk_size=4096)

    response_synthesizer = get_response_synthesizer(
        response_mode="tree_summarize", use_async=True
    )

    doc_summary_index = DocumentSummaryIndex.from_documents(
        docs,
        transformations=[splitter],
        response_synthesizer=response_synthesizer,
        show_progress=True,
        streaming=True,
    )

    return doc_summary_index, doc_summary_index.get_document_summary(file_name)

def get_query_engine(doc_summary_index):
    return doc_summary_index.as_query_engine(
        response_mode="tree_summarize", use_async=True, streaming=True
    )

def reset_chat():
    st.session_state.messages = []
    gc.collect()

# Load existing documents when the app loads
load_existing_documents()

with st.sidebar:
    st.header("Upload your documents!")
    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")

    if uploaded_file:
        try:
            file_path = os.path.join("./documents", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            file_key = uploaded_file.name

            if file_key not in st.session_state.get("file_cache", {}):
                st.session_state.file_cache[file_key] = file_path

            st.success("File uploaded and saved successfully!")
            display_pdf(file_path)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

col1, col2 = st.columns([3, 1])

with col1:
    st.header("Documents Summarizer! 🚀")
    if st.session_state.get("file_cache"):
        with st.expander("Select Document"):
            selected_file_key = st.radio("", list(st.session_state.file_cache.keys()))
            selected_file_path = st.session_state.file_cache[selected_file_key]
    else:
        st.write("No documents uploaded yet. Please upload a document to get started.")

    if st.button("Summarize"):
        if "selected_file_path" in locals():
            st.session_state.processing = True
            with st.spinner('Processing...'):
                doc_summary_index, summary = process_and_summarize_selected_doc(selected_file_path)
            st.session_state.processing = False
            st.markdown("### Summary")
            st.write(summary)
            
            # Initialize the query engine
            query_engine = get_query_engine(doc_summary_index)
            st.session_state.query_engine = query_engine
        else:
            st.error("Please select a document to summarize.")

with col2:
    if st.button("Clear ↺"):
        reset_app()
        st.experimental_rerun()

if "query_engine" in st.session_state:
    st.header("Chat for follow up question! 💬")
    if "messages" not in st.session_state:
        reset_chat()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask something about the document ..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate stream of response with milliseconds delay
            streaming_response = st.session_state.query_engine.query(prompt)
            
            for chunk in streaming_response.response_gen:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


 # Accept user input
    if prompt := st.chat_input("Ask something about the document ..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate stream of response with milliseconds delay
            streaming_response = st.session_state.query_engine.query(prompt)
            
            for chunk in streaming_response.response_gen:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
