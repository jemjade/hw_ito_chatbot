# Hanwha General Insurance chatbot Project

## 설치방법

1. Clone the repository:
    ```sh
    git clone https://github.com/jemjade/hw_ito_chatbot.git
    cd hw_ito_chatbot
    ```

2. Create and activate a virtual environment:
    ```sh
    # python 설치되어 있지 않은 경우
    pyenv install 3.11
    
    # Python 3.11.13을 기반으로 hw_ito_env라는 이름의 **가상환경(virtualenv)**을 새로 만듭니다.
    pyenv virtualenv 3.11.13 hw_ito_env

    # 현재 디렉토리(프로젝트 폴더)에 대해 hw_ito_env 환경을 로컬 기본 Python 버전/환경으로 지정합니다.
    pyenv local hw_ito_env
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

2. http://localhost:8501 접속


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