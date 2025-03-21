import asyncio
from dotenv import load_dotenv
import shutil
import subprocess
import requests
import time
import os
import random
import sqlite3
import datetime
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

class AppointmentDatabase:
    def __init__(self, db_path="appointments.db"):
        self.db_path = db_path
        self._create_tables_if_not_exist()
    
    def _create_tables_if_not_exist(self):
        """Create the appointments table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create appointments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            notes TEXT,
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_appointment(self, name, appointment_time, notes="", phone_number=None):
        """Save an appointment to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO appointments (name, appointment_time, notes, phone_number) VALUES (?, ?, ?, ?)",
            (name, appointment_time, notes, phone_number)
        )
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return appointment_id
    
    def get_all_appointments(self):
        """Retrieve all appointments from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM appointments ORDER BY created_at DESC")
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return appointments
    
    def get_appointment_by_id(self, appointment_id):
        """Retrieve a specific appointment by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        appointment = cursor.fetchone()
        
        conn.close()
        return dict(appointment) if appointment else None
    
    def get_appointments_by_name(self, name):
        """Retrieve appointments for a specific customer by name."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM appointments WHERE name LIKE ? ORDER BY created_at DESC", (f"%{name}%",))
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return appointments
    
    def get_appointments_by_date(self, date_str):
        """Retrieve appointments for a specific date."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # This assumes appointment_time contains the date in some format
        # You might need to adjust the LIKE pattern based on your actual date format
        cursor.execute("SELECT * FROM appointments WHERE appointment_time LIKE ? ORDER BY appointment_time", (f"%{date_str}%",))
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return appointments

    def get_upcoming_appointments_for_name(self, name):
        """Retrieve upcoming appointments for a specific customer by name."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM appointments WHERE name LIKE ? ORDER BY created_at DESC", (f"%{name}%",))
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return appointments

class BusinessDataManager:
    def __init__(self):
        self.faqs = {
            "business_hours": "We're open Monday through Friday, 9 AM to 5 PM.",
            "location": "We're located at 123 Business Street, Suite 100.",
            "services": "We offer consulting, training, and support services.",
            "pricing": "Our pricing varies based on the service package. Would you like me to provide more details about specific services?",
            "contact": "You can reach us at (555) 123-4567 or email us at info@business.com."
        }
        
        self.available_appointments = {
            "Monday": ["10:00", "11:00", "14:00", "15:00"],
            "Tuesday": ["09:00", "10:00", "13:00", "14:00"],
            "Wednesday": ["11:00", "12:00", "15:00", "16:00"],
            "Thursday": ["09:00", "10:00", "14:00", "15:00"],
            "Friday": ["10:00", "11:00", "13:00", "14:00"]
        }

    def get_faq_answer(self, question):
        # Convert question to lowercase for better matching
        question = question.lower()
        
        # Check for keywords in the question
        for key, answer in self.faqs.items():
            if key in question:
                return answer
        
        return "I apologize, but I don't have specific information about that. Would you like me to connect you with someone who can help?"

    def get_available_slots(self, day=None):
        if day and day in self.available_appointments:
            return f"Available slots for {day} are: {', '.join(self.available_appointments[day])}"
        return "I can help you check available appointment slots. Which day would you prefer?"

    def book_appointment(self, day, time):
        if day in self.available_appointments and time in self.available_appointments[day]:
            self.available_appointments[day].remove(time)
            return f"Great! I've booked your appointment for {day} at {time}. Is there anything else you need?"
        return "I apologize, but that time slot is not available. Would you like to see other available times?"

class LanguageModelProcessor:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4-turbo-preview", 
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        system_prompt = """
        You are a highly empathetic and professional front desk assistant. You have access to the following information:
        
        Business Hours: Monday through Friday, 9 AM to 5 PM
        Location: 123 Business Street, Suite 100
        Services: Consulting, training, and support services
        Contact: (555) 123-4567, info@business.com
        
        Available appointment slots:
        Monday: 10:00, 11:00, 14:00, 15:00
        Tuesday: 09:00, 10:00, 13:00, 14:00
        Wednesday: 11:00, 12:00, 15:00, 16:00
        Thursday: 09:00, 10:00, 14:00, 15:00
        Friday: 10:00, 11:00, 13:00, 14:00
        
        Important:
        - Maintain natural conversation flow
        - Remember personal details shared by the caller
        - Show appropriate concern for urgent situations
        - Process appointment requests intelligently using context
        - Respond with empathy and human-like understanding
        - Keep responses concise but warm and professional (less than 20 words)
        
        When booking appointments:
        1. Naturally collect the caller's full name, confirming spelling if unclear
        2. Get the preferred appointment time
        3. Ask if they'd like to leave any notes or special requests
        4. Confirm all details before ending the conversation
        5. If any information is missing, ask naturally without being pushy
        
        When a user asks about their existing appointments:
        - Respond with "CHECK_APPOINTMENTS: [Name]" where [Name] is the name they provided
        
        When processing outbound reminder calls (when message starts with "OUTBOUND_REMINDER_CALL:"):
        1. Be aware that you initiated this call to remind them about an upcoming appointment
        2. Listen to their response about keeping, rescheduling, or cancelling the appointment
        3. If they want to CANCEL the appointment, respond with "CANCEL_APPOINTMENT: [Name]"
        4. If they want to RESCHEDULE, collect the new preferred time and respond with "RESCHEDULE_APPOINTMENT: [Name]|[New Time]"
        5. If they CONFIRM the appointment, thank them and respond with "APPOINTMENT_CONFIRMED: [Name]"
        6. Be helpful and understanding regardless of their choice
        
        When the conversation is complete and all necessary information is gathered for a new appointment, respond with:
        "APPOINTMENT_BOOKED: [Full Name]|[Appointment Time]|[Notes]"
        
        If the conversation should end, respond with:
        "CONVERSATION_ENDED"
        """
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    def process(self, text):
        start_time = time.time()
        response = self.conversation.invoke({"text": text})
        end_time = time.time()
        
        elapsed_time = int((end_time - start_time) * 1000)
        print(f"LLM ({elapsed_time}ms): {response['text']}")
        return response['text']

class TextToSpeech:
    # Set your Deepgram API Key and desired voice model
    DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    MODEL_NAME = "aura-luna-en"  # Example model name, change as needed

    def __init__(self):
        self.is_speaking = False

    @staticmethod
    def is_installed(lib_name: str) -> bool:
        lib = shutil.which(lib_name)
        return lib is not None

    def check_dependencies(self):
        if not self.is_installed("ffplay"):
            raise ValueError("ffplay not found, necessary to stream audio.")

    def speak(self, text):
        tts_start_time = time.time()
        print(f"\nTTS Started: {tts_start_time}")
        print("Speaking: True")
        self.is_speaking = True
        
        self.check_dependencies()

        DEEPGRAM_URL = "https://api.deepgram.com/v1/speak"
        params = {
            "model": self.MODEL_NAME,
            "encoding": "linear16",
            "sample_rate": 24000,  # Changed to integer
            "voice": self.MODEL_NAME  # Added voice parameter
        }
        
        headers = {
            "Authorization": f"Token {self.DG_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }

        try:
            player_command = ["ffplay", "-autoexit", "-", "-nodisp"]
            player_process = subprocess.Popen(
                player_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            start_time = time.time()
            first_byte_time = None

            with requests.post(DEEPGRAM_URL, params=params, stream=True, headers=headers, json=payload) as r:
                if r.status_code != 200:
                    print(f"\nError: Deepgram API returned status code {r.status_code}")
                    print(f"Response: {r.text}")
                    return

                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        if first_byte_time is None:
                            first_byte_time = time.time()
                            ttfb = int((first_byte_time - start_time)*1000)
                            print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")
                        player_process.stdin.write(chunk)
                        player_process.stdin.flush()

            if player_process.stdin:
                player_process.stdin.close()
            player_process.wait()
        finally:
            self.is_speaking = False
            print("Speaking: False")

class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()

async def get_transcript(callback):
    transcription_complete = asyncio.Event()  # Event to signal transcription completion

    try:
        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient("", config)

        dg_connection = deepgram.listen.asynclive.v("1")
        print ("Listening...")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                # This is the final part of the current sentence
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                # Check if the full_sentence is not empty before printing
                if len(full_sentence.strip()) > 0:
                    full_sentence = full_sentence.strip()
                    print(f"Human: {full_sentence}")
                    callback(full_sentence)  # Call the callback with the full_sentence
                    transcript_collector.reset()
                    transcription_complete.set()  # Signal to stop transcription and exit

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=300,
            smart_format=True,
        )

        await dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)
        microphone.start()

        await transcription_complete.wait()  # Wait for the transcription to complete instead of looping indefinitely

        # Wait for the microphone to close
        microphone.finish()

        # Indicate that we've finished
        await dg_connection.finish()

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

class ConversationManager:
    def __init__(self):
        self.transcription_response = ""
        self.llm = LanguageModelProcessor()
        self.is_first_interaction = True
        self.appointment_data = None
        self.db = AppointmentDatabase()
        self.conversation_active = True

    async def main(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence

        while self.conversation_active:
            if self.is_first_interaction:
                greeting = self.llm.process("START_CONVERSATION")
                tts = TextToSpeech()
                tts.speak(greeting)
                self.is_first_interaction = False
            else:
                await get_transcript(handle_full_sentence)
                
                llm_response = self.llm.process(self.transcription_response)
                
                # Check if the user is asking about their appointments
                if "CHECK_APPOINTMENTS:" in llm_response:
                    name = llm_response.split("CHECK_APPOINTMENTS:")[1].strip()
                    appointments = self.db.get_appointments_by_name(name)
                    
                    if appointments:
                        # Format appointments for speech
                        if len(appointments) == 1:
                            appt = appointments[0]
                            appointment_info = f"I found one appointment for {name}. You're scheduled for {appt['appointment_time']}."
                            if appt['notes']:
                                appointment_info += f" Notes: {appt['notes']}."
                        else:
                            appointment_info = f"I found {len(appointments)} appointments for {name}. "
                            for i, appt in enumerate(appointments[:3]):  # Limit to first 3 to keep response manageable
                                appointment_info += f"Appointment {i+1}: {appt['appointment_time']}. "
                            if len(appointments) > 3:
                                appointment_info += f"And {len(appointments) - 3} more. "
                        
                        # Speak the appointment information
                        tts = TextToSpeech()
                        tts.speak(appointment_info)
                        
                        # Also print the appointments to console
                        print("\nFound Appointments:")
                        for appt in appointments:
                            print(f"Name: {appt['name']}")
                            print(f"Time: {appt['appointment_time']}")
                            print(f"Notes: {appt['notes']}")
                            print(f"Created: {appt['created_at']}")
                            print("-" * 40)
                    else:
                        # No appointments found
                        no_appointments_msg = f"I couldn't find any appointments for {name}. Would you like to schedule one now?"
                        tts = TextToSpeech()
                        tts.speak(no_appointments_msg)
                
                # Check if the conversation should end
                elif "CONVERSATION_ENDED" in llm_response:
                    farewell = "Thank you for calling. Have a great day!"
                    tts = TextToSpeech()
                    tts.speak(farewell)
                    self.conversation_active = False
                    
                # Check if an appointment was booked
                elif "APPOINTMENT_BOOKED:" in llm_response:
                    # Extract appointment data
                    appointment_info = llm_response.split("APPOINTMENT_BOOKED:")[1].strip()
                    name, time, notes = appointment_info.split("|")
                    self.appointment_data = {
                        "name": name,
                        "time": time,
                        "notes": notes
                    }
                    
                    # Get a phone number (you might want to implement a way to collect this from the user)
                    phone_number = "Unknown"  # Default value
                    
                    # Save appointment to database with phone number
                    appointment_id = self.db.save_appointment(name, time, notes, phone_number)
                    
                    print("\nAppointment Details:")
                    print(f"Name: {name}")
                    print(f"Time: {time}")
                    print(f"Notes: {notes}")
                    print(f"Phone: {phone_number}")
                    print(f"Appointment ID: {appointment_id}")
                    print(f"Saved to database: {self.db.db_path}")
                    
                    # Confirm to the user that the appointment was saved
                    confirmation = f"Thank you {name.split()[0]}. Your appointment for {time} has been confirmed and saved. Is there anything else I can help you with today?"
                    tts = TextToSpeech()
                    tts.speak(confirmation)
                    
                    # Don't break here - continue the conversation
                else:
                    tts = TextToSpeech()
                    tts.speak(llm_response)

                self.transcription_response = ""

def list_appointments(filter_type=None, filter_value=None):
    """Utility function to list appointments from the database."""
    db = AppointmentDatabase()
    
    if filter_type == "id":
        appointment = db.get_appointment_by_id(filter_value)
        if appointment:
            appointments = [appointment]
        else:
            appointments = []
    elif filter_type == "name":
        appointments = db.get_appointments_by_name(filter_value)
    elif filter_type == "date":
        appointments = db.get_appointments_by_date(filter_value)
    else:
        appointments = db.get_all_appointments()
    
    if not appointments:
        print("No appointments found.")
        return
    
    print(f"\nFound {len(appointments)} appointment(s):")
    for appt in appointments:
        print(f"ID: {appt['id']}")
        print(f"Name: {appt['name']}")
        print(f"Time: {appt['appointment_time']}")
        print(f"Notes: {appt['notes']}")
        print(f"Created: {appt['created_at']}")
        print("-" * 40)

if __name__ == "__main__":
    # Check for command line arguments to list appointments
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            # Handle listing appointments
            if len(sys.argv) > 3:
                list_appointments(sys.argv[2], sys.argv[3])
            else:
                list_appointments()
        else:
            print("Unknown command. Available commands: list")
    else:
        # Run the normal conversation flow
        manager = ConversationManager()
        asyncio.run(manager.main())