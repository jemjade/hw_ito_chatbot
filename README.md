# Hanwha General Insurance chatbot Project

## 개발환경 구성 방법
### 소스코드 및 라이브러리 설치

1. 리파지토리 클론:
    ```sh
    git clone https://github.com/jemjade/hw_ito_chatbot.git
    cd hw_ito_chatbot
    ```

2. 파이선 가상환경 생성 및 활성화:
    ```sh
    # python 설치되어 있지 않은 경우
    pyenv install 3.11
    
    # Python 3.11.13을 기반으로 hw_ito_env라는 이름의 **가상환경(virtualenv)**을 새로 만듭니다.
    pyenv virtualenv 3.11.13 hw_ito_env

    # 현재 디렉토리(프로젝트 폴더)에 대해 hw_ito_env 환경을 로컬 기본 Python 버전/환경으로 지정합니다.
    pyenv local hw_ito_env
    ```

3. 의존성 라이브러리 설치:
    ```sh
    pip install -r requirements.txt
    ```

### Ollama 설치 및 실행
```
brew install ollama
brew install --cask ollama-app
# ollama app 실행
ollama --version
ollama run qwen2.5:3b
# CLI 환경에서 모델 응답 정상동작 확인
```

### 데이터셋 준비
1. 시스템 별 담당자 리스트.csv 파일을 받아서 emnbInfoList.csv로 이름 변경
2. 업무시스템별 정보.csv 파일을 받아서 SysInfoList.csv 로 이름 변경
3. 프로젝트 루트 디렉토리에 위치

### Streamlit 실행

1. Run the Streamlit application:
    ```sh
    streamlit run chat.py
    ```

2. http://localhost:8501 접속

3. `테스트 화면` 탭에 접근하여 아무거나 질문

> 별도 llm.py 테스트 방법
> python llm.py

## Overview

This repository contains a project that utilizes LangChain and Streamlit to build a Retrieval Augmented Generation (RAG) application. The primary focus of this application is to provide insights and answers based on the Hanhwa G/I. By leveraging advanced NLP techniques, this application enhances its responses using a combination of chat history and few-shot learning templates.

## Features

- **LangChain Integration**: Utilizes LangChain to manage and interact with language models effectively.
- **Streamlit Interface**: A user-friendly web interface created with Streamlit for seamless interaction.
- **Retrieval Augmented Generation (RAG)**: Combines retrieval-based techniques with generative models to produce accurate and context-aware answers.
- **Knowledge Base**: Focuses on the South Korean Income Tax Law (소득세법) as the primary knowledge base.
- **Chat History**: Maintains a history of user interactions to provide contextually relevant answers.
- **Few-Shot Learning Templates**: Enhances the model's responses by using predefined templates for better accuracy and consistency.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/jasonkang14/inflearn-streamlit.git
    cd inflearn-streamlit
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit application:
    ```sh
    streamlit run chat.py
    ```

2. Open your web browser and navigate to the displayed local URL to interact with the application.

## Project Structure

- `chat.py`: Main application script that runs the Streamlit interface.
- `llm.py`: Contains utility functions for handling the knowledge base and model interactions.
- `config.py`: File with few-shot learning templates used to generate answers.

## How It Works

1. **Data Retrieval**: The application retrieves relevant sections of the South Korean Income Tax Law based on user queries.
2. **Contextual Processing**: Utilizes chat history to maintain context across multiple interactions.
3. **Template-Based Generation**: Applies few-shot learning templates to enhance the accuracy and relevance of the generated answers.
4. **User Interface**: Provides an intuitive web interface through Streamlit for users to interact with the application seamlessly.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue to discuss improvements, bug fixes, or new features.

## Acknowledgments

- [LangChain](https://langchain.com/)
- [Streamlit](https://streamlit.io/)
- All contributors and users of the project.

---

Feel free to modify and enhance this README to better fit your project's specifics and any additional information you may want to provide.

streamlit run chat.py