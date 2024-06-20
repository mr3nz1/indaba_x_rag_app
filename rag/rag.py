import os
from langchain_openai import ChatOpenAI, OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.chains.question_answering import load_qa_chain

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


# initialize openAI llm
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=100,
    timeout=None,
    max_retries=2,
    api_key=OPENAI_API_KEY,
)


def translateKinyToEng(llmInstructions, prompt):
    kiny_to_eng_message = [
        (
            "system",
            llmInstructions,
        ),
        (
            "human",
            prompt,
        ),
    ]

    # translate from kiny to english
    kiny_to_eng_res = llm.invoke(kiny_to_eng_message)

    return kiny_to_eng_res


def getDocs():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of rag.py
    pdf_path = os.path.join(base_dir, "../pdfs/contracts_partial_summary.pdf")

    # Ensure the path is normalized
    pdf_path = os.path.normpath(pdf_path)

    # load and split pdf docs
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=150, length_function=len
    )

    docs = text_splitter.split_documents(pages)
    return docs


def createAndStoreEmbeddings(docs):
    # create embeddings
    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())

    # save local store locally
    vector_store.save_local("indaba_rag_app")

    # get local store
    persisted_vectorstore = FAISS.load_local(
        "indaba_rag_app",
        OpenAIEmbeddings(),
        allow_dangerous_deserialization=True,
    )

    return vector_store


def searchLocalStore(store, kinyToEngText):
    # search local store
    queried_docs = store.similarity_search(kinyToEngText.content, k=2)

    # translate query kiny to eng
    chain = load_qa_chain(OpenAI(), chain_type="stuff")

    response = chain.invoke(
        input={
            "context": "Rwanda",
            "input_documents": queried_docs,
            "question": f"Base youself only on the provided docs, and only give the answer. {kinyToEngText.content}",
        },
    )

    return response


def translateEngToKiny(embedding, machineBehavior):
    # translate to kinyarwanda once again
    eng_to_kiny_message = [
        (
            "system",
            machineBehavior,
        ),
        ("human", embedding["output_text"]),
    ]

    eng_to_kiny_res = llm.invoke(eng_to_kiny_message)

    return eng_to_kiny_res
