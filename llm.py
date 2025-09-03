import os
import platform
import shutil
import subprocess
import time
from functools import lru_cache
from typing import List

import ollama
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import CSVLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_text_splitters import CharacterTextSplitter

import exm_answer

answer_examples = exm_answer.answer_examples


class LLMConfig:
    MODEL = "qwen2.5:3b"
    FILE_PATH1 = "emnbInfoList.csv"
    FILE_PATH2 = "SysInfoList.csv"
    EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    TEST_SESSION_ID = "cli_test"
    CHROMA_DB_PATH = "./chroma"
    CHROMA_COLLECTION_NAME = "docNew"


answer_examples = exm_answer.answer_examples


# ollama 실행 파일 경로 탐지
OLLAMA_BIN = shutil.which("ollama")
if OLLAMA_BIN is None and platform.system() == "Windows":
    OLLAMA_BIN = os.path.join(
        os.path.expanduser("~"), "AppData", "Local", "Ollama", "ollama.exe"
    )
elif OLLAMA_BIN is None:
    OLLAMA_BIN = "/usr/local/bin/ollama"  # 기본 설치 경로

# 세션별 대화 기록 저장소
SESSION_STORE = {}


@lru_cache(maxsize=None)
def get_llm() -> ChatOllama:
    return ChatOllama(model=LLMConfig.MODEL)


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ChatMessageHistory()
    history = SESSION_STORE[session_id]
    # 대화 기록을 최근 4턴(사용자 질문 + AI 답변 = 8개 메시지)으로 제한
    if len(history.messages) > 8:
        history.messages = history.messages[-8:]
    return history


def _ensure_ollama_running():
    """
    Ollama 서버가 실행 중인지 확인하고, 아닐 경우 서버를 시작합니다.
    """
    try:
        ollama.list()
    except Exception:
        if not OLLAMA_BIN or not os.path.exists(OLLAMA_BIN):
            raise RuntimeError(
                "Ollama 바이너리를 찾을 수 없습니다. https://ollama.com/download 에서 설치하세요."
            )
        subprocess.Popen(
            [OLLAMA_BIN, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(20):  # 최대 10초 대기
            time.sleep(0.5)
            try:
                ollama.list()
                return
            except Exception:
                continue
        raise RuntimeError(
            "Ollama 서버에 연결할 수 없습니다. 수동으로 실행 여부를 확인하세요."
        )


def _safe_pull(model: str):
    """
    Ollama로부터 지정된 모델을 안전하게 다운로드합니다.
    """
    try:
        ollama.pull(model=model)
    except Exception as e:
        print(f"모델 {model} 다운로드 중 오류 발생: {e}")


def _get_installed_models() -> List[str]:
    """
    로컬에 설치된 Ollama 모델 목록을 반환합니다.
    """
    try:
        local_list = ollama.list()
        models = local_list.get("models", [])
        return sorted(
            [model.get("model") for model in models if isinstance(model, dict)]
        )
    except Exception as e:
        print(f"설치된 모델 목록 확인 중 오류 발생: {e}")
        return []


def check_server_and_models(required_models: List[str]):
    """
    Ollama 서버 상태와 필요한 모델 설치 여부를 확인하고, 없으면 다운로드합니다.
    """
    _ensure_ollama_running()
    installed_models = _get_installed_models()
    for model in required_models:
        tag_model = model if ":" in model else f"{model}:latest"
        if tag_model not in installed_models:
            _safe_pull(tag_model)


def _get_documents(file_name: str, file_name2: str):
    loader1 = CSVLoader(file_name, encoding="UTF-8")
    documents1 = loader1.load()
    loader2 = CSVLoader(file_name2, encoding="UTF-8")
    documents2 = loader2.load()
    documents = documents1 + documents2

    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=300, chunk_overlap=0
    )
    document_list = text_splitter.split_documents(documents)

    return document_list


@lru_cache(maxsize=None)
def _get_retriever():
    """
    RAG (Retrieval-Augmented Generation) 체인을 위한 리트리버를 구성하고 반환합니다.
    1. CSV 파일로부터 문서들을 로드합니다.
    2. HuggingFace 임베딩 모델을 사용하여 문서들을 벡터로 변환하고 ChromaDB에 저장합니다.
    3. 저장된 벡터 데이터베이스를 기반으로 리트리버(retriever)를 생성합니다.
    """
    _all_docs: List[Document] = _get_documents(
        LLMConfig.FILE_PATH1, LLMConfig.FILE_PATH2
    )

    embedding = HuggingFaceEmbeddings(model_name=LLMConfig.EMBEDDING_MODEL)
    database = Chroma.from_documents(
        documents=_all_docs,
        embedding=embedding,
        collection_name=LLMConfig.CHROMA_COLLECTION_NAME,
        persist_directory=LLMConfig.CHROMA_DB_PATH,
    )
    return database.as_retriever(search_kwargs={"k": 4})


def get_history_aware_retriever() -> create_history_aware_retriever:
    """
    대화 기록을 인지하는 리트리버를 생성합니다.
    """
    llm = get_llm()
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
    return create_history_aware_retriever(llm, retriever, contextualize_q_prompt)


def get_rag_chain() -> RunnableWithMessageHistory:
    """
    RAG 체인을 생성합니다.
    """
    llm = get_llm()
    history_aware_retriever = get_history_aware_retriever()

    example_prompt = ChatPromptTemplate.from_messages(
        [("human", "{input}"), ("ai", "{answer}")]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
    system_prompt = (
        "당신은 주어진 문서에 기반하여 사용자의 질문에 답변하는 챗봇입니다."
        "주어진 문서는 시스템 담당자 목록입니다. 사용자가 담당자나 연락처를 찾을 수 있도록 도와주세요."
        "문서에서 답변을 찾을 수 없다면, '정보를 찾을 수 없습니다.'라고 답변해주세요."
        "답변은 2-3 문장으로 한국말로 간결하게 해주세요."
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


def get_ai_response(
    rag_chain: RunnableWithMessageHistory,
    user_message,
    session_id="default_session",
    temperature: float = 0.0,
    top_p: float = 0.1,
) -> str:
    config = {
        "configurable": {
            "session_id": session_id,
            "temperature": temperature,
            "top_p": top_p,
        }
    }
    response = rag_chain.invoke({"input": user_message}, config=config)
    return response or "응답이 없습니다."


if __name__ == "__main__":

    # Ollama 서버 및 모델 준비 상태 확인
    check_server_and_models([LLMConfig.MODEL])

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
    question_2_1 = "그 분 어느 팀이야?"
    print(f"\n질문: {question_2_1}")
    response_2_1 = get_ai_response(
        rag_chain2, question_2_1, session_id=LLMConfig.TEST_SESSION_ID
    )
    print(f"답변: {response_2_1}")
