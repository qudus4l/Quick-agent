import asyncio
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    config = DeepgramClientOptions(options={"keepalive": "true"})
    deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"), config)
    
    dg_connection = deepgram.listen.asynclive.v("1")
    print("Listening... (speak something)")
    
    async def on_message(result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if sentence.strip():
            print(f"Heard: {sentence}")
    
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    
    options = LiveOptions(
        model="nova-2",
        punctuate=True,
        language="en-US",
        encoding="linear16",
        channels=1,
        sample_rate=16000,
    )
    
    await dg_connection.start(options)
    
    microphone = Microphone(dg_connection.send)
    microphone.start()
    
    # Keep the connection open for 10 seconds
    await asyncio.sleep(10)
    
    microphone.finish()
    await dg_connection.finish()

if __name__ == "__main__":
    asyncio.run(main()) 