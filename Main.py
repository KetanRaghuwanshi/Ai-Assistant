from Frontend.GUI import (
    GetAssistantStatus, GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen,
    TempDirectoryPath, SetMicrophoneStatus, AnswerModifier, QueryModifier, GetMicrophoneStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        with open('Data/ChatLog.json', 'r', encoding='utf-8') as file:
            if len(file.read()) < 5:
                open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8').write("")
                open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8').write(DefaultMessage)
    except FileNotFoundError:
        print("⚠️ ChatLog.json not found. Creating a new one.")
        open('Data/ChatLog.json', 'w', encoding='utf-8').write("[]")

def ReadChatLogJson():
    with open('Data/ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = "\n".join(
        f"{entry['role'].replace('User', Username).replace('assistant', Assistantname)}: {entry['content']}"
        for entry in json_data
    )

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
        if data:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(data)
    except FileNotFoundError:
        print("⚠️ Database file not found.")

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def StartImageGeneration(image_query):
    """ Starts the ImageGeneration script in a separate process. """
    try:
        # Write query to file
        with open(r"Frontend\Files\ImageGeneration.data", "w", encoding="utf-8") as file:
            file.write(f"{image_query}, True")

        # Start the image generation script
        subprocess.run(['python', r'Backend\ImageGeneration.py'], check=True, text=True, encoding="utf-8")
        print("🖼️ Image generation process started successfully.")
    except Exception as e:
        print(f"❌ Image generation failed: {e}")

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any(i for i in Decision if i.startswith("general"))
    R = any(i for i in Decision if i.startswith("realtime"))
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries and len(queries.split()) > 2:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
        else:
            print("⚠️ Incomplete image request. Skipping image generation.")

    if any(queries.startswith(func) for queries in Decision for func in Functions):
        run(Automation(list(Decision)))
        TaskExecution = True

    if ImageExecution:
        threading.Thread(target=StartImageGeneration, args=(ImageGenerationQuery,), daemon=True).start()

    if G and R or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ...")
                Answer = ChatBot(QueryModifier(Queries.replace("general ", "")))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                Answer = RealtimeSearchEngine(QueryModifier(Queries.replace("realtime ", "")))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                Answer = ChatBot(QueryModifier("Okay, Bye!"))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        else:
            if "Available ..." not in GetAssistantStatus():
                SetAssistantStatus("Available ...")
        sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()



















# from Frontend.GUI import (
#     GetAssistantStatus,
#     GraphicalUserInterface,
#     SetAssistantStatus,
#     ShowTextToScreen,
#     TempDirectoryPath,
#     SetMicrophoneStatus,
#     AnswerModifier,
#     QueryModifier,
#     GetMicrophoneStatus
# )
# from Backend.Model import FirstLayerDMM
# from Backend.RealtimeSearchEngine import RealtimeSearchEngine
# from Backend.Automation import Automation
# from Backend.SpeechToText import SpeechRecognition
# from Backend.Chatbot import ChatBot
# from Backend.TextToSpeech import TextToSpeech
# from dotenv import dotenv_values
# from asyncio import run
# from time import sleep
# import subprocess
# import threading
# import json
# import os

# # Load environment variables
# env_vars = dotenv_values(".env")
# Username = env_vars.get("Username", "User")
# Assistantname = env_vars.get("Assistantname", "Assistant")

# DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
# {Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

# subprocesses = []
# Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# def ShowDefaultChatIfNoChats():
#     try:
#         with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
#             if len(file.read().strip()) < 5:
#                 with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
#                     f.write("")
#                 with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
#                     f.write(DefaultMessage)
#     except FileNotFoundError:
#         pass  # If file doesn't exist, skip it

# def ReadChatLogJson():
#     try:
#         with open('Data/ChatLog.json', 'r', encoding='utf-8') as file:
#             data = file.read()
#             return json.loads(data) if data.strip() else []
#     except (FileNotFoundError, json.JSONDecodeError):
#         return []

# def ChatLogIntegration():
#     json_data = ReadChatLogJson()
#     formatted_chatlog = "".join(f"{entry['role']}: {entry['content']}\n" for entry in json_data)
#     formatted_chatlog = formatted_chatlog.replace("User", Username).replace("Assistant", Assistantname)
#     with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
#         file.write(AnswerModifier(formatted_chatlog))

# def ShowChatsOnGUI():
#     try:
#         with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
#             Data = file.read()
#         if Data:
#             with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
#                 file.write(Data)
#     except FileNotFoundError:
#         pass  # Ignore if files don't exist

# def InitialExecution():
#     SetMicrophoneStatus("False")
#     ShowTextToScreen("")
#     ShowDefaultChatIfNoChats()
#     ChatLogIntegration()
#     ShowChatsOnGUI()

# InitialExecution()

# def MainExecution():
#     TaskExecution = False
#     ImageExecution = False
#     ImageGenerationQuery = ""

#     SetAssistantStatus("Listening...")
#     Query = SpeechRecognition().strip()
#     ShowTextToScreen(f"{Username} : {Query}")
#     if not Query:
#         return  # Exit if the query is empty
    
#     SetAssistantStatus("Thinking...")
#     Decision = FirstLayerDMM(Query)
#     print(f"Decision: {Decision}\n")

#     G = any(i.startswith("general") for i in Decision)
#     R = any(i.startswith("realtime") for i in Decision)

#     MergedQuery = " and ".join(
#         [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
#     )

#     for queries in Decision:
#         if "generate" in queries:
#             ImageGenerationQuery = str(queries)
#             ImageExecution = True

#     if not TaskExecution:
#         for queries in Decision:
#             if any(queries.startswith(func) for func in Functions):
#                 run(Automation(list(Decision)))
#                 TaskExecution = True

#     if ImageExecution:
#         with open(r"Frontend\\Files\\ImageGeneration.data", "w") as file:
#             file.write(f"{ImageGenerationQuery}, True")
#         try:
#             p1 = subprocess.Popen(['python', r'Backend\\ImageGeneration.py'],
#                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                                   stdin=subprocess.PIPE, shell=False)
#             subprocesses.append(p1)
            
#             # Capture the output and error from the subprocess
#             stdout, stderr = p1.communicate()
#             if stderr:
#                 print(f"Error in subprocess: {stderr.decode()}")
#             if stdout:
#                 print(f"Output from subprocess: {stdout.decode()}")
#         except Exception as e:
#             print(f"Error starting ImageGeneration.py: {e}")

#     if G and R or R:
#         SetAssistantStatus("Searching...")
#         Answer = RealtimeSearchEngine(QueryModifier(MergedQuery))
#     else:
#         Answer = ""
#         for Queries in Decision:
#             if "general" in Queries:
#                 SetAssistantStatus("Thinking...")
#                 QueryFinal = Queries.replace("general ", "").strip()
#                 if QueryFinal:
#                     Answer = ChatBot(QueryModifier(QueryFinal))
#             elif "realtime" in Queries:
#                 SetAssistantStatus("Searching...")
#                 QueryFinal = Queries.replace("realtime ", "").strip()
#                 if QueryFinal:
#                     Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
#             elif "exit" in Queries:
#                 ShowTextToScreen(f"{Assistantname} : Okay, Bye!")
#                 TextToSpeech("Okay, Bye!")
#                 os._exit(1)
        
#     if Answer:
#         ShowTextToScreen(f"{Assistantname} : {Answer}")
#         SetAssistantStatus("Answering...")
#         TextToSpeech(Answer)

# def FirstThread():
#     while True:
#         if GetMicrophoneStatus() == "True":
#             MainExecution()
#         elif GetAssistantStatus() != "Available ...":
#             SetAssistantStatus("Available ...")
#         sleep(0.1)

# def SecondThread():
#     GraphicalUserInterface()

# if __name__ == "__main__":
#     threading.Thread(target=FirstThread, daemon=True).start()
#     SecondThread()







