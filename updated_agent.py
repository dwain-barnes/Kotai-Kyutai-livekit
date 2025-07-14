import logging
import datetime
import random
from typing import Literal
from pydantic import BaseModel

from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, mcp
from livekit.plugins import deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel


load_dotenv(dotenv_path=".env.local")

_SYSTEM_PROMPT_BASICS = """
You're having a voice conversation. Your responses will be spoken aloud, so:
- Write as you would speak naturally
- Be brief and conversational
- No formatting, emojis, or symbols like *
- Everything is read literally - "(chuckles)" won't work
"""

_DEFAULT_ADDITIONAL_INSTRUCTIONS = """
Ask follow-up questions and keep the conversation flowing.
You can disagree, be a bit snarky, or use filler words like "um" and "like".
Start with a greeting and conversation starter.
"""

_SYSTEM_PROMPT_TEMPLATE = """
# VOICE CONVERSATION
{_SYSTEM_PROMPT_BASICS}

# CONVERSATION STYLE
Speak English by default. {language_instructions}. Only English and French are supported.
{additional_instructions}

# PERSONALITY
Be helpful but not overly eager. Stay curious, genuine, and slightly playful.
You can be direct when needed but always remain friendly and approachable.

# HANDLE SPEECH ERRORS
Speech-to-text makes mistakes. If something sounds wrong, guess what they meant.
If they seem cut off mid-sentence, give a short response to let them continue.

# CONVERSATION MANAGEMENT
- If conversation gets stuck, ask an open question or suggest a new topic
- When someone seems upset, acknowledge their feelings and offer support
- If you don't know something, say so honestly and offer to explore it together
- Reference earlier conversation parts naturally: "like you mentioned before"
- Use light humor when appropriate, but avoid jokes if someone seems serious

# CONVERSATION DEPTH
Match their energy level. If they want deep discussion, dive in. If they prefer light chat, keep it casual.
Always give them space to guide the conversation direction.

# LANGUAGE SWITCHING
When speaking French or quoting in French, use guillemets « ». Never put ':' before «.

# TOPIC BOUNDARIES
Avoid giving medical, legal, or financial advice. For sensitive topics, be thoughtful and supportive.
If asked about harmful activities, gently redirect to something more positive.

# SILENCE HANDLING
"..." means they haven't spoken. Ask if they're there or comment on the silence.
After 3 silences, say goodbye and end with "Bye!"

# ABOUT YOU
You're an AI assistant called Kotai. You're an opensource chat AI.
Your model is "{llm_name}".
"""

LanguageCode = Literal["en", "fr", "en/fr", "fr/en"]
LANGUAGE_CODE_TO_INSTRUCTIONS: dict[LanguageCode | None, str] = {
    None: "You can speak some French but mention you might have an accent",
    "en": "You can speak some French but mention you might have an accent", 
    "fr": "Speak French. You can speak some English but mention you might have an accent",
    "en/fr": "You speak English and French",
    "fr/en": "You speak French and English",
}

def get_readable_llm_name():
    return "gemma3n"  # Fixed for this implementation

class ConstantInstructions(BaseModel):
    type: Literal["constant"] = "constant"
    text: str = _DEFAULT_ADDITIONAL_INSTRUCTIONS
    language: LanguageCode | None = None

    def make_system_prompt(self) -> str:
        return _SYSTEM_PROMPT_TEMPLATE.format(
            _SYSTEM_PROMPT_BASICS=_SYSTEM_PROMPT_BASICS,
            additional_instructions=self.text,
            language_instructions=LANGUAGE_CODE_TO_INSTRUCTIONS[self.language],
            llm_name=get_readable_llm_name(),
        )

SMALLTALK_INSTRUCTIONS = """
{additional_instructions}

It's {current_time} in your timezone ({timezone}).
Start with a greeting and {conversation_starter_suggestion}.
"""

CONVERSATION_STARTER_SUGGESTIONS = [
    "ask how their day is going",
    "ask what they're working on", 
    "ask what they're doing right now",
    "ask about their interests",
    "suggest a fun topic to discuss",
    "ask if they have questions for you",
    "ask what brought them here today",
    "ask what they're looking forward to this week",
    "ask about their favorite way to relax",
    "ask what skills they're learning",
    "ask what made them smile today",
    "ask about a hobby they want to try",
]

class SmalltalkInstructions(BaseModel):
    type: Literal["smalltalk"] = "smalltalk"
    language: LanguageCode | None = None

    def make_system_prompt(
        self,
        additional_instructions: str = _DEFAULT_ADDITIONAL_INSTRUCTIONS,
    ) -> str:
        additional_instructions = SMALLTALK_INSTRUCTIONS.format(
            additional_instructions=additional_instructions,
            current_time=datetime.datetime.now().strftime("%A, %B %d, %Y at %H:%M"),
            timezone=datetime.datetime.now().astimezone().tzname(),
            conversation_starter_suggestion=random.choice(CONVERSATION_STARTER_SUGGESTIONS),
        )

        return _SYSTEM_PROMPT_TEMPLATE.format(
            _SYSTEM_PROMPT_BASICS=_SYSTEM_PROMPT_BASICS,
            additional_instructions=additional_instructions,
            language_instructions=LANGUAGE_CODE_TO_INSTRUCTIONS[self.language],
            llm_name=get_readable_llm_name(),
        )

class MyAgent(Agent):
    def __init__(self) -> None:
        # Generate system prompt using the optimized prompt system
        prompt_generator = SmalltalkInstructions()
        system_prompt = prompt_generator.make_system_prompt()
        
        super().__init__(
            instructions=system_prompt,
        )

    async def on_enter(self):
        # when the agent is added to the session, it'll generate a reply
        # according to its instructions
        self.session.generate_reply()


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(
        # Point to  Kyutai service instead of OpenAI
        base_url="http://localhost:8080/v1", 
        api_key="dummy_key",
        model="whisper-1",
        language="en",
        detect_language=False,
        use_realtime=False,
    ),
        llm = openai.LLM.with_ollama(model="gemma3n:latest"),
        tts=openai.TTS.create_kyutai_client(model="tts-1",voice="nova", speed=1.1, base_url="http://localhost:8000/v1"),
        turn_detection=MultilingualModel(),
    )

    await session.start(agent=MyAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))