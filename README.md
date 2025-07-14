# Kotai - Local Voice Assistant with Kyutai TTS/STT and LiveKit

[![Watch the Demo](https://img.youtube.com/vi/PHFrchtDIoE/0.jpg)](https://youtu.be/PHFrchtDIoE)
## 🔊 Overview

Kotai is a fully local, zero-cost voice assistant that combines the power of Kyutai TTS/STT, LiveKit, and local LLMs to create natural conversational experiences. This project eliminates the need for cloud-based API services by integrating:

- **Kyutai TTS** for high-quality speech synthesis
- **Kyutai STT** for accurate speech-to-text conversion
- **LiveKit** for real-time voice communication
- **Ollama** for running local large language models (Gemma3n)

The result is a voice assistant with natural speech capabilities and intelligent conversation management - all running completely on your local machine.

## ✨ Features

- 🎯 **100% Local** - No API costs or cloud dependencies
- 🗣️ **Natural Speech** - High-quality voice synthesis with Kyutai TTS
- 🎙️ **Real-time Conversation** - Fluid interaction through LiveKit
- 🧠 **Local LLM Integration** - Uses Ollama to run Gemma3n locally
- 👂 **Advanced Speech Recognition** - Fast local transcription with Kyutai STT
- 🤖 **Optimized System Prompt** - Designed specifically for smaller LLMs
- 🌍 **Bilingual Support** - English and French language support
- 💬 **Conversation Management** - Handles errors, silence, and emotional intelligence

## 📋 Prerequisites

Before running Kotai, you’ll need:

- Python 3.12
- Kyutai TTS server running on `http://localhost:8000/v1`
- Kyutai STT server running on `http://localhost:8080/v1`
- Ollama installed with the Gemma3n model
- LiveKit server access

## 🚀 Installation

See youtube video

Create a `.env.local` file with your configuration:

```env
# Your LiveKit configuration
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

## 💬 Usage

1. Make sure the Kyutai TTS server is running (default: `http://localhost:8000/v1`)
1. Make sure the Kyutai STT server is running (default: `http://localhost:8080/v1`)
1. Make sure Ollama is running with the Gemma3n model loaded:
  
   ```bash
   ollama run gemma3n:latest
   ```
1. Run the voice assistant:
  
   ```bash
   python agent.py
   ```
1. Connect to the LiveKit room and start interacting with Kotai

## 🔧 How It Works

The system consists of several integrated components:

- **Speech-to-Text (STT)**: Uses Kyutai STT for local transcription
- **Language Model**: Connects to a local Ollama instance running Gemma3n
- **Text-to-Speech (TTS)**: Kyutai TTS for natural speech synthesis
- **Voice Pipeline**: Handles the flow between components via LiveKit
- **Optimized Prompt System**: Comprehensive system prompt designed for smaller LLMs

Kotai features an intelligent conversation system that:

- Handles speech transcription errors gracefully
- Manages conversation flow and silence
- Adapts to user energy levels and preferences
- Provides emotional intelligence and support

## 🔄 Customization

You can modify the `agent.py` file to:

- **Change the voice** by editing the `voice` parameter in the TTS setup
- **Modify the personality** by editing the system prompt classes
- **Adjust the LLM model** by changing the Ollama model name in `get_readable_llm_name()`
- **Configure different endpoints** for any of the services
- **Switch languages** by modifying the `LanguageCode` settings

## 📝 Code Explanation

The main workflow in `agent.py` dev:

```python
# 1) Speech-to-Text with Kyutai STT
stt=openai.STT(
    base_url="http://localhost:8080/v1",
    api_key="dummy_key",
    model="whisper-1",
    language="en",
)

# 2) Language Model from Ollama
llm = openai.LLM.with_ollama(model="gemma3n:latest")

# 3) Text-to-Speech using Kyutai TTS
tts=openai.TTS.create_kyutai_client(
    model="tts-1",
    voice="nova",
    speed=1.1,
    base_url="http://localhost:8000/v1"
)

# 4) Create Agent with optimized system prompt
class MyAgent(Agent):
    def __init__(self) -> None:
        prompt_generator = SmalltalkInstructions()
        system_prompt = prompt_generator.make_system_prompt()
        super().__init__(instructions=system_prompt)
```

## 🤖 System Prompt Features

Kotai includes a sophisticated system prompt optimized for smaller LLMs:

- **Personality**: Helpful, curious, genuine, and slightly playful
- **Conversation Management**: Handles stuck conversations, emotional support, and knowledge gaps
- **Speech Error Handling**: Gracefully manages transcription mistakes
- **Conversation Depth**: Adapts to user preferences for light or deep discussion
- **Bilingual Support**: Seamless English/French switching
- **Topic Boundaries**: Thoughtful handling of sensitive subjects

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Kyutai] for the excellent TTS and STT models
- [LiveKit]for the real-time communication platform
- [Ollama]

