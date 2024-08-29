# This is a skeleton for the chatbot. Feel free to make changes as you see fit.
import google.generativeai as genai
from gtts import gTTS
import threading
import pygame
from random import randint
import customtkinter as tk
import json
import csv


my_secret = 'AIzaSyAobsmPY4a-fQenatXg47Ft3IU4Za39nWA' # it is not advised to add your API key directly here.
genai.configure(api_key=my_secret)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
chat = model.start_chat()
pygame.init()
pygame.mixer.init()

def colorRGB(red, green, blue):
    if red > 256 or green > 256 or blue > 256:
        raise ValueError("This is an 8bit colors scheme, max value is 255") #I modified the code from chatGPT to prevent you from entering incorrect color codes
    return f'#{red:02x}{green:02x}{blue:02x}'

def initializeAI():
    """Call this function to initialize the AI chat with a starting prompt.
    It will send Gemini the initializing prompt and the data gathered from your research
    team
    """
    file_path = 'prompt.txt'
    prompt = "Instruction:\n"
    try:
        with open(file_path, 'r') as file:
            prompt += file.read() + '\n\n'
    except Exception as e:
        print("Error:", e)
    file_paths = ['facilities.csv', 'pharmacy.csv']
    for index, path in enumerate(file_paths):
        if index == 0:
            prompt += "Medical facilities info in csv format: The labels are first:"
        else:
            prompt += "\n\nPharmacy Info in csv format. The labels are first:"
        try:
            with open(path, 'r') as csvfile:
                reader = list(csv.reader(csvfile))
                for row in reader:
                    prompt += "\n".join(row)
        except Exception as e:
            print("Error:", e)
    askGemini(prompt)



def askGemini(question):
  """Send a question to the Gemini AI and return the response."""
  response = chat.send_message(question)
  reply = response.text
  try:
      # Extract JSON from response
      start = reply.find('{')
      end = reply.rfind('}') + 1
      if start != -1 and end != -1:
          aiDict = json.loads(reply[start:end])
          return aiDict
      else:
          return {"response": "I'm here to assist with your inquiries. Could you please rephrase that?", "quit": False}
  except Exception as e:
      return {"response": "Something went wrong. Could you please ask again?", "quit": False}

def send_message(user_message):
    "Pass this function in the appropriate place."
    if charCount["count"] != 0:
        return
    if user_message.strip(): 
        # Get response from Gemini
        aiResponse = askGemini(user_message)
        bot_response = aiResponse.get('response', "Sorry, something went wrong.") + "\n"
        thread = threading.Thread(target=lambda: loadAndPlay(bot_response))
        thread.start() # these two lines will prevent it from pausing the code. I suggest you look into multithreading.
        buttonText['qb1'] = aiResponse.get('predictiveText1', buttonText['qb1']) # Excellent use of dictionaries great job!
        buttonText['qb2'] = aiResponse.get('predictiveText2', buttonText['qb2'])
        quickButton.configure(text=buttonText['qb1'])
        quickButton2.configure(text=buttonText['qb2'])
        messages.append(aiResponse.get('name', 'user') + ":\n" + user_message + "\n")
        textBox.configure(state="normal")
        for text in messages:
            textBox.insert(tk.END, text)
            textBox.see(tk.END) # this will allow the code to scroll down as you type
        slowType(textBox, "AI-den:\n" + bot_response + "\n")
        messages.append("AI-den:\n" + bot_response + "\n")

def slowType(textWidget, finalMessage):
    textWidget.insert(tk.END, finalMessage[charCount["count"]])
    charCount["count"] += 1
    if charCount['count'] == len(finalMessage):
        textWidget.configure(state="disabled")
        charCount["count"] = 0
        return
    textWidget.see(tk.END)
    root.after(ms=randint(0, 50), func=lambda: slowType(textWidget, finalMessage))

def onEnter(event):
    user_message = promptBox.get("1.0", tk.END)
    promptBox.delete(1.0, tk.END)
    send_message(user_message)


def press(buttonName):
    if buttonName == 'db':
        return(send_message(buttonText[buttonName]))
    promptBox.delete(1.0, tk.END)
    text = buttonText[buttonName].replace("\n", "")
    promptBox.insert(1.0, text)

def loadAndPlay(text):
    #This function allows you to play back the text as speech.
    #You need to appropriated add it where its needed
    soundFile = gTTS(text=text, lang='en', slow=False)
    soundFile.save("response.mp3")
    sound = pygame.mixer.Sound("response.mp3")
    sound.play()

initializeAI()

buttonText = {
    'qb1': "I have trouble sleeping. What natural \n productscan help me sleep better?",
    'qb2': "A dog just bit me. Can you suggest \na facility I could get treated at?",
    'db' : "The chat bot is being presented to a group of investors. Can you give a comprehensive explanation of its capabilities?"
}
# Define and configure window
root = tk.CTk()
root.title("AIden")
root.configure(fg_color=colorRGB(10, 10, 40))
scale = 1.5
resolution = (root.winfo_screenwidth(), root.winfo_screenheight())

# Create a left frame for helper and quich use.
leftFrame = tk.CTkFrame(root, width=180*scale, height=360*scale, fg_color=colorRGB(10, 10, 40))
nameLabel = tk.CTkLabel(leftFrame, text="AI-den", text_color="white", font=("Lexon",20, "bold"))
demoButton = tk.CTkButton(
    leftFrame,
    width=170*scale,
    height=30*scale,
    fg_color=colorRGB(255, 173, 140),
    text="Demo AI-den",
    text_color=colorRGB(40, 40, 40),
    command=lambda: press('db')
)
quickLabel = tk.CTkLabel(leftFrame, text="Try these out", text_color="white", font=("Arial",16, "bold"))

quickButton = tk.CTkButton(
   leftFrame,
   width=170*scale,
   height=90*scale,
   fg_color=colorRGB(137, 7, 230),
   text=buttonText["qb1"],
   text_color="white",
   font=("Arial",14),
   command=lambda: press('qb1')
)

quickButton2 = tk.CTkButton(
   leftFrame,
   width=170*scale,
   height=90*scale,
   fg_color=colorRGB(137, 7, 230),
   text=buttonText['qb2'],
   text_color="white",
   font=("Arial",14),
   command=lambda: press('qb2')
)
rightFrame = tk.CTkFrame(root, width=460*scale, height=360*scale, fg_color="white", corner_radius=12)
textBox = tk.CTkTextbox(
    rightFrame,
    width=460*scale,
    height= 285*scale,
    fg_color="white",
    wrap="word",
    #border_width=1,
    #border_color=colorRGB(230, 230, 230),
    corner_radius=0,
)
promptBox = tk.CTkTextbox(
    rightFrame,
    width=450*scale,
    height=65*scale,
    fg_color=colorRGB(240, 240, 240),
    wrap = "word",
    corner_radius=15,
    border_width=2,
    border_color=colorRGB(220, 220, 220)
)
sendButton = tk.CTkButton(
    rightFrame,
    width=10*scale,
    height=10*scale,
    text="⬆",
    fg_color=colorRGB(100, 100, 100),
    command=lambda: onEnter("") # lambda allows you to pass in your parameters so this will fix the error.
)
textBox.configure(state="disabled")
leftFrame.grid(row=0, column=0)
nameLabel.place(x=50*scale, y=20*scale)
demoButton.place(x=10*scale, y=60*scale)
quickLabel.place(x=40*scale, y=140*scale)
quickButton.place(x=10*scale, y=170*scale)
quickButton2.place(x=10*scale, y=270*scale)
rightFrame.grid(row=0, column=1, pady=10*scale, padx=10*scale)
textBox.place(x=0,y=0)
promptBox.place(x=5*scale, y=290*scale)
sendButton.place(x=425*scale, y=312*scale)

messages = []
charCount = {'count': 0}

promptBox.bind("<Return>", onEnter)

root.mainloop()