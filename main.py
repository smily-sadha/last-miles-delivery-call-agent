"""
Last-Mile Delivery Outbound Voice Agent
Silence-based recording + Deepgram STT + Deepgram TTS
"""

import os
import asyncio
from dotenv import load_dotenv

from memory.memory import ConversationMemory
from audio.recorder import SilenceRecorder
from audio.playback import AudioPlayer
from stt.deepgram_stt import DeepgramSTT
from tts.deepgram_tts import DeepgramTTS

from last_mile_delivery.agent import LastMileDeliveryAgent
from last_mile_delivery.data import get_order_by_phone


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise RuntimeError("DEEPGRAM_API_KEY not set")


# --------------------------------------------------
# VOICE AGENT
# --------------------------------------------------

class LastMileDeliveryVoiceAgent:
    def __init__(self, customer_phone: str):
        # Lookup order by phone number
        order = get_order_by_phone(customer_phone)
        if not order:
            raise RuntimeError("No order found for this phone number")

        self.order = order

        # Memory
        self.memory = ConversationMemory()
        self.memory.start_session(f"order_{order['order_id']}")

        # Core agent
        self.agent = LastMileDeliveryAgent(
            memory=self.memory,
            order=order
        )

        # Audio components
        self.recorder = SilenceRecorder(
            start_timeout_ms=5000,
            silence_threshold=350.0,
            silence_duration_ms=900,
            max_record_ms=10000,
        )

        self.stt = DeepgramSTT(DEEPGRAM_API_KEY)
        self.tts = DeepgramTTS(DEEPGRAM_API_KEY)
        self.player = AudioPlayer(sample_rate=24000)

        self.no_response_count = 0

    # --------------------------------------------------

    async def speak(self, text: str):
        print(f"\n🤖 AGENT: {text}")
        audio = self.tts.synthesize(text)
        self.player.play(audio)

    # --------------------------------------------------

    async def listen_and_transcribe(self) -> str:
        audio_bytes = self.recorder.record()

        print("🧠 Transcribing user speech...")
        transcript = self.stt.transcribe(audio_bytes).strip()

        if transcript:
            print(f"📝 STT RESULT: {transcript}")
        else:
            print("📝 STT RESULT: <empty>")

        return transcript

    # --------------------------------------------------

    async def run(self):
        print("=" * 60)
        print("🚚 Last-Mile Delivery Voice Agent (Outbound)")
        print("=" * 60)

        # Initial outbound greeting
        await self.speak(
            f"Hello, am I speaking with {self.order['customer_name']}?"
        )

        # Conversation loop
        while True:
            user_text = await self.listen_and_transcribe()

            # ------------------------
            # NO RESPONSE HANDLING
            # ------------------------
            if not user_text:
                self.no_response_count += 1

                if self.no_response_count == 1:
                    await self.speak("Hello, can you hear me?")
                    continue

                if self.no_response_count == 2:
                    await self.speak(
                        "It seems now is not a good time. "
                        "We will try again later."
                    )
                    break

                break

            # ------------------------
            # USER SPOKE
            # ------------------------
            self.no_response_count = 0
            print(f"\n👤 HUMAN: {user_text}")

            response = self.agent.handle_input(user_text)
            await self.speak(response)

            # Stop if agent closed the conversation
            if self.agent.state.name == "CLOSE":
                break


# --------------------------------------------------
# ENTRYPOINT
# --------------------------------------------------

if __name__ == "__main__":
    try:
        # Simulate outbound dialer providing phone number
        CUSTOMER_PHONE = "9876543210"

        asyncio.run(
            LastMileDeliveryVoiceAgent(CUSTOMER_PHONE).run()
        )

    except KeyboardInterrupt:
        print("\n👋 Call ended.")
