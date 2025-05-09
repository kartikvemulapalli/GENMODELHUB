# 🤖🎙️ GenModelHub 🤖🎙️

**GenModelHub** is an advanced AI-powered chatbot platform that integrates multiple state-of-the-art generative models into a single, unified interface. Built on Django's robust framework, our system combines the capabilities of LLaMA-3 for text and code generation, Stable Diffusion for image creation, and gTTS for speech synthesis, enabling seamless multimodal interactions through both voice and text inputs.The platform offers comprehensive content generation features, including conversational AI interactions, programming code synthesis, creative writing (stories and poetry), language translation, text summarization, and image generation - all accessible through a simple chat interface. For data processing tasks, we incorporate Jellyfish to ensure efficient input handling and preprocessing.

[![Live Demo](https://img.shields.io/badge/Live-Visit%20GenModelHub-brightgreen?style=for-the-badge&logo=python)](https://genmodelhubgenai.pythonanywhere.com)

## 🚀 Project Highlights
- **Text Generation** using [LLaMA-3](https://llama.meta.com/)
- **Image Synthesis** using [Stable Diffusion](https://stability.ai/)
- **Voice Generation** using [gTTS (Google Text-to-Speech)](https://pypi.org/project/gTTS/)
- **Data Preprocessing** using Jellyfish-7B
- **Multimodal Chat Interface** for text, image, and audio interactions
- **Built on Django** with scalable cloud deployment options
- **Enterprise-grade reliability** (<1% error rate under load)
- **Real-time voice interaction** and **domain-specific content generation**

---

## 🛠️ Tech Stack

| Layer         | Technologies |
|---------------|--------------|
| Frontend      | HTML, CSS, JavaScript |
| Backend       | Django, Python 3.8+ |
| AI Models     | LLaMA-3, Stable Diffusion, gTTS, Jellyfish-7B |
| Database      | MongoDB |
| Deployment    | PythonAnywhere |
| Others        | Git,PyTest |

---

## 📦 Features

- 🔒 Secure User Authentication (JWT/OAuth)
- 🗣️ Voice Assistant (STT and TTS)
- 🤖 AI Chatbot (Contextual, Multi-turn Conversations)
- 🖼️ Text-to-Image Generator
- 📜 Story, Poem, and Code Generation
- 🎙️ Text-to-Audio Synthesis
- 🌎 Language Translation
- 📊 Text Summarization
- 🧹 Data Preprocessing (via Jellyfish-7B)
- 📈 Real-time Monitoring and Logging

---

## 🏗️ Project Architecture

- **Frontend:** Django Templates + JavaScript 
- **Backend:** Django Views and REST APIs
- **Model Integration:** Hugging Face APIs, Together.AI 
- **Database:** MongoDB (for users, history, and logs)
- **Deployment:** cloud hosting.

---

## 📸 Screenshots

| Dashboard                                                                                | AI Models Page                                                                           | Chatbot                                                                                  | Image Generator |
|:---------:                                                                               |:--------------:                                                                          |:-------:                                                                                 |:---------------:|
| ![image](https://github.com/user-attachments/assets/3d33a1f2-c995-4fd9-b830-b41f401913ed)| ![image](https://github.com/user-attachments/assets/3130fbf6-d8b9-491a-9132-8ca72a86d8fd)| ![image](https://github.com/user-attachments/assets/95a7c69d-d544-4124-9079-24d253d7b83f)| ![image](https://github.com/user-attachments/assets/318c66ea-f229-4bea-be77-9b8e3a6f2cd8)|

---

## 🧠 How It Works

1. User registers/logs in securely.
2. They can interact via text, upload an image, or use voice input.
3. Depending on the action:
   - LLaMA-3 generates text/code responses.
   - Stable Diffusion creates images from text.
   - gTTS converts text to voice.
4. The responses are shown dynamically on the frontend.
5. Users can save/download outputs.

---

## 🚀 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/kartikvemulapalli/GENMODELHUB.git
cd myproject

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # (for Linux/Mac)
venv\Scripts\activate     # (for Windows)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure MongoDB in settings.py

# 5. Run the server
python manage.py runserver
