# **Smart Learning Assistant**
The Smart Learning Assistant uses AI to support students with visual, hearing, and cognitive impairments through tools like text-to-speech, speech-to-text, and content simplification.
It offers personalized, accessible learning experiences that adapt to individual needs.
This assistant promotes independent learning and bridges educational gaps for disabled students.

# **Features**

**1.Input Options**

•	Text input via Streamlit text box

•	Voice input via microphone (speech_recognition + webrtc)

**2.Processing**

•	Input sent to Groq API (llama3-70b-8192)

•	Model generates accessible, simplified, or creative responses

**3.Output Options**

•	Text displayed on screen

•	Voice feedback through pyttsx3

# **How to use**
**STEP 1: PREPARE YOUR COMPUTER**

• Ensure you have Python 3.10 or newer installed.

• Confirm that your system has a working microphone and speakers/headphones for voice interaction.

• Create a dedicated folder on your computer to house your project files.

**STEP 2: CREATE AND ACTIVATE A VIRTUAL ENVIRONMENT**

• Open your command line interface (Terminal or Command Prompt).

• Navigate to your project folder.

• Create a virtual environment to isolate project dependencies.

• Activate the virtual environment before installing any packages.

**STEP 3: INSTALL REQUIRED SOFTWARE PACKAGES**

• Install all necessary Python libraries required by your project, such as:

• The web app framework

• Speech recognition and processing tools

• AI client libraries

• Audio handling packages

**STEP 4: CONFIGURE THE AI ACCESS KEY**

• Register or log in to your AI service provider (Groq).

• Retrieve your unique API key.

• Make sure this key is updated in your project’s configuration to enable
communication with the AI backend.

**STEP 5: ORGANIZE AND SAVE YOUR PROJECT FILES**

• Place your application code and resources, including the main application script, inside your project folder.

• Ensure all dependencies and configurations are correctly linked and saved.

STEP 6: LAUNCH THE APPLICATION

• Run the application using the appropriate command via your terminal with the virtual environment activated.

• This command will start a local web server and present you with a link,usually
`http://localhost:8501`, to open your app in the browser.

**STEP 7: ACCESS AND USE THE APPLICATION**

• Open the provided local web address in a modern web browser.

• You will see a sleek, clean interface that follows a light theme, with a lot of whitespace and large, elegant typography for headings.

• Select the accessibility mode you need:

• Voice interaction for visual impairment with audio input/output

• Text input for hearing impairment

• Simplified content for cognitive impairment

• Interactive riddles combining multiple accessibility supports

**STEP 8: HANDLE PERMISSIONS AND SETTINGS**

• Allow your browser to access your microphone when prompted, necessary for voice-based features.

• Adjust your device volume and microphone settings for best interaction results.

**STEP 9 : TROUBLESHOOT IF NEEDED**

• If voice features don’t respond, verify microphone permissions and hardware settings.

• If AI responses don’t appear, confirm your API key is correct and that your device has internet access.

• Look at the terminal/command prompt logs for error messages to guide troubleshooting.

# **Technical Detail**
This application is bulit using:

•	Frontend: Streamlit (Python-based web app framework)

•	Backend: Python

•	AI Model: Groq API using llama3-70b-8192

•	Speech Recognition: speech_recognition (Google Web Speech API)

•	Text-to-Speech (TTS): pyttsx3 (offline engine)

•	Audio Streaming: streamlit-webrtc, av, numpy

# **Browsing compatability**

**1.Cross-Browser Support:**

The web application is built using Streamlit, which ensures compatibility with all modern web browsers including:

•	Google Chrome

•	Microsoft Edge

•	Mozilla Firefox

•	Safari (latest versions)

**2.Responsive Design:**

The assistant UI is responsive and adapts well to different screen sizes, including:

•	Desktop

•	Tablets

•	Mobile devices

# **License**

This project is for personal use only.

