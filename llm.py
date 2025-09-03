import os
import platform
import shutil
import subprocess
import time
from typing import Any, Dict, List

import ollama
import pandas as pd
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import CharacterTextSplitter


class LLMConfig:
    MODEL = "qwen2.5:3b"
    FILE_PATH1 = "emnbInfoList.csv"
    FILE_PATH2 = "SysInfoList.csv"
    EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    TEST_SESSION_ID = "cli_test"
    CHROMA_DB_PATH = "./chroma"
    CHROMA_COLLECTION_NAME = "docNew"


# ollama 실행 파일 경로 탐지 (PATH 문제 대비)
system = platform.system()
if system == "Windows":
    OLLAMA_BIN = shutil.which("ollama") or os.path.join(
        os.path.expanduser("~"), "AppData", "Local", "Ollama", "ollama.exe"
    )
else:  # macOS and Linux
    OLLAMA_BIN = shutil.which("ollama") or "/usr/local/bin/ollama"

# 세션별 대화 기록 저장소
SESSION_STORE = {}


class SingletonChatOllama:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonChatOllama, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.model = LLMConfig.MODEL
        self.chat_model = ChatOllama(model=self.model)
        self._initialized = True

    def get_model(self):
        return self.chat_model


def _get_llm():
    return SingletonChatOllama().get_model()


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ChatMessageHistory()
    return SESSION_STORE[session_id]


def _ensure_ollama_running():
    """
    Ollama 서버가 실행 중인지 확인하고, 실행 중이 아닐 경우 서버를 시작합니다.
    서버에 연결을 시도하고, 실패하면 예외를 발생시킵니다.
    """
    try:
        return ollama.list()
    except Exception:
        ollama_bin = shutil.which("ollama")
        if ollama_bin is None:
            raise RuntimeError(
                "Ollama 바이너리를 찾을 수 없습니다. https://ollama.com/download 에서 설치하세요."
            )
        subprocess.Popen(
            [ollama_bin, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        for _ in range(20):
            try:
                return ollama.list()
            except Exception:
                time.sleep(0.5)
        raise RuntimeError(
            "Ollama 서버에 연결할 수 없습니다. 수동으로 실행 여부를 확인하세요."
        )


def _safe_pull(model: str) -> bool:
    """
    Ollama로부터 지정된 모델을 안전하게 다운로드(pull)합니다.
    성공하면 True, 실패하면 False를 반환합니다.
    """
    try:
        res = ollama.pull(model=model)
        return getattr(res, "completed", True)
    except Exception as e:
        print(str(e))
        return False


def _check_installed_models() -> List[str]:
    """
    로컬에 설치된 Ollama 모델 목록을 확인하고, 모델 이름의 정렬된 리스트를 반환합니다.
    """
    local_list: ollama.ListResponse = ollama.list()
    models: List[Dict[str, Any]] = local_list.model_dump().get("models", [])
    return sorted([md.get("model") for md in models if isinstance(md, dict)])


def check_server_and_list_models(models_to_test: List[str]):
    """
    Ollama 서버 상태를 확인하고, 테스트에 필요한 모델들이 설치되어 있는지 확인합니다.
    설치되지 않은 모델이 있으면 다운로드합니다.
    """
    _ensure_ollama_running()
    try:
        installed = _check_installed_models()
        for model in models_to_test:
            tag_model = model if ":" in model else f"{model}:latest"
            if tag_model not in installed:
                print(f"모델 {tag_model}이(가) 없어 다운로드합니다...")
                _safe_pull(tag_model)
    except Exception as e:
        print("Ollama 서버 연결 실패:", e)


def _get_documents(file_name: str, file_name2: str):
    
    loader1 = CSVLoader(file_name,encoding="UTF-8")
    documents1 = loader1.load()
    loader2 = CSVLoader(file_name2,encoding="UTF-8")
    documents2 = loader2.load()
    documents = documents1+documents2

    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=300, chunk_overlap=0)
    document_list = text_splitter.split_documents(documents)


    
    return document_list


def _get_retriever():
    """
    RAG (Retrieval-Augmented Generation) 체인을 위한 리트리버를 구성하고 반환합니다.
    1. CSV 파일로부터 문서들을 로드합니다.
    2. HuggingFace 임베딩 모델을 사용하여 문서들을 벡터로 변환하고 ChromaDB에 저장합니다.
    3. 저장된 벡터 데이터베이스를 기반으로 리트리버(retriever)를 생성합니다.
    """
    _all_docs: List[Document] = _get_documents(LLMConfig.FILE_PATH1, LLMConfig.FILE_PATH2)

    embedding = HuggingFaceEmbeddings(model_name=LLMConfig.EMBEDDING_MODEL)
    database = Chroma.from_documents(
        documents=_all_docs,
        embedding=embedding,
        collection_name=LLMConfig.CHROMA_COLLECTION_NAME,
        persist_directory=LLMConfig.CHROMA_DB_PATH,
    )
    retriever = database.as_retriever(search_kwargs={"k": 4})
    return retriever


def get_history_retriever():
    llm = _get_llm()
    retriever = _get_retriever()

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever

import exm_answer
answer_examples = exm_answer.answer_examples

def get_rag_chain():
    llm = _get_llm()
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
    system_prompt = (
        "당신은 주어진 문서에 기반하여 사용자의 질문에 답변하는 챗봇입니다."
        "주어진 문서는 시스템 담당자 목록입니다. 사용자가 담당자나 연락처를 찾을 수 있도록 도와주세요."
        "문서에서 답변을 찾을 수 없다면, '정보를 찾을 수 없습니다.'라고 답변해주세요."
        "답변은 2-3 문장으로 간결하게 해주세요."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = get_history_retriever()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain2 = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain2,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick("answer")

    return conversational_rag_chain


def get_ai_response(rag_chain2, user_message, session_id="default_session"):
    ai_response = rag_chain2.invoke(  # stream
        {"input": user_message},
        config={"configurable": {"session_id": session_id}},
    )
    return ai_response if ai_response else "응답이 없습니다."


if __name__ == "__main__":

 
    # Ollama 서버 및 모델 준비 상태 확인
    check_server_and_list_models([LLMConfig.MODEL])
    # RAG 체인 생성
    rag_chain2 = get_rag_chain()

    # 첫 번째 질문
    question1_1 = "그룹웨어에서 메일이 보내지지 않아 누구에게 문의해야해? 연락처 알려줘"
    print(f"질문: {question1_1}")
    response1_1 = get_ai_response(
        rag_chain2, question1_1, session_id=LLMConfig.TEST_SESSION_ID
    )
    print(f"답변: {response1_1}")

    # 두 번째 질문 (대화 이어가기)
    question_2_1 = "그 사람의 이메일 주소도 알려줘"
    print(f"\n질문: {question_2_1}")
    response_2_1 = get_ai_response(
        rag_chain2, question_2_1, session_id=LLMConfig.TEST_SESSION_ID
    )
    print(f"답변: {response_2_1}")