import streamlit as st
from transformers import pipeline
import PyPDF2
from pdfminer.high_level import extract_text
import re
from pydub import AudioSegment
import textwrap
from fpdf import FPDF
from gtts import gTTS
import os
absolute_path = os.path.dirname(os.path.abspath(__file__))
from transformers import pipeline
import io
from deep_translator import GoogleTranslator
import time 
from streamlit.web.server.server import Server
from streamlit.runtime.scriptrunner import add_script_run_ctx


epoch_time = int(time.time())

def gen_conv_text(english_text ,target_lang = 'en'):
    print('converting text to ',target_lang)
    english_text = english_text.split('\n')
    fi =''
    for i in english_text:
        translated = GoogleTranslator(source='en', target=target_lang).translate(i) 
        fi = fi + translated + '\n'
    return fi
import sqlite3
import hashlib

# Connect to the database or create it if it doesn't exist
conn = sqlite3.connect('users.db')

# Create a cursor object to interact with the database
c = conn.cursor()

# Create the users table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
''')

# Commit the changes to the database
conn.commit()

def hash_password(password):
    """Hash a password using the SHA-256 algorithm"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def add_user(username, password, role):
    """Add a new user to the database"""
    hashed_password = hash_password(password)
    c.execute('INSERT INTO users (email, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
    conn.commit()

def get_user(username):
    """Get a user from the database by username"""
    c.execute('SELECT * FROM users WHERE email = ?', (username,))
    return c.fetchone()

def authenticate_user(username, password):
    """Authenticate a user by username and password"""
    user = get_user(username)
    if user is None:
        return False
    hashed_password = hash_password(password)
    return user[2] == hashed_password

def authorize_user(username, role):
    """Check if a user has the specified role"""
    user = get_user(username)
    if user is None:
        return False
    return user[3] == role

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


class SessionState:
    def __init__(self):
        self.username = None
        self.password = None
        self.logged_in = False


def show_login_page(session_st):
    # Create a login form
    with st.form(key="login_form"):
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")
    
    # Check if the login form was submitted
    if submit_button:
        if authenticate_user(username, password):
            show_dashboard_page(session_st)
        # # Check the credentials against a hardcoded username and password
        # if username == "myusername" and password == "mypassword":
        #     session_st.username = username
        #     session_st.password = password
        #     session_st.logged_in = True
        #     st.success("Logged in!")
        #     st.experimental_set_query_params(logged_in=True)
        #     st.session_state['logged_in'] = True
        # else:
        #     st.error("Incorrect username or password")

def show_signup_page(session_st):
    # Create a signup form
    with st.form(key="signup_form"):
        st.header("Signup")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button(label="Signup")
    
    # Check if the signup form was submitted
    if submit_button:
        # Check if the passwords match
        if password != confirm_password:
            st.error("Passwords do not match")
        elif get_user(username) is not None:
            st.error("A user with that username already exists please sign in")
        else:
            session_st.username = username
            session_st.password = password
            session_st.logged_in = True
            st.success("Signed up and logged in!")
            add_user(username, password, 'user')

session_st = SessionState()


def read_pdf(file_in_bytes):
    output = io.BytesIO()
    output.write(file_in_bytes)
    output.seek(0)
    # sample_pdf = open(file_in_bytes, mode='rb')
    pdfdoc = PyPDF2.PdfReader(output)
    return pdfdoc


def gen_audio_of_text(text ,auio_file_number = 0 ,lang='en'):
    print('generating audio of text')
    tts = gTTS(text=text, lang=lang, slow=False )
    audio = f'{absolute_path}/audio/audio_{auio_file_number}.mp3'
    tts.save(audio)
    song = AudioSegment.from_file_using_temporary_files(audio,format='mp3')
    song = song +16
    song = song.speedup(playback_speed=1.26)
    return audio
# This function tweak the text before saving in the pdf
def prep_b4_save(text):
  text = re.sub('Gods', 'God\'s', text)
  text = re.sub('yours', 'your\'s', text)
  text = re.sub('dont', 'don\'t', text)
  text = re.sub('doesnt', 'doesn\'t', text)
  text = re.sub('isnt', 'isn\'t', text)
  text = re.sub('havent', 'haven\'t', text)
  text = re.sub('hasnt', 'hasn\'t', text)
  text = re.sub('wouldnt', 'wouldn\'t', text)
  text = re.sub('theyre', 'they\'re', text)
  text = re.sub('youve', 'you\'ve', text)
  text = re.sub('arent', 'aren\'t', text)
  text = re.sub('youre', 'you\'re', text)
  text = re.sub('cant', 'can\'t', text)
  text = re.sub('whore', 'who\'re', text)
  text = re.sub('whos', 'who\'s', text)
  text = re.sub('whatre', 'what\'re', text)
  text = re.sub('whats', 'what\'s', text)
  text = re.sub('hadnt', 'hadn\'t', text)
  text = re.sub('didnt', 'didn\'t', text)
  text = re.sub('couldnt', 'couldn\'t', text)
  text = re.sub('theyll', 'they\'ll', text)
  text = re.sub('youd', 'you\'d', text)
  return text


# This function convert the text into the pdf and save it at the specified location
def text_to_pdf(text, filename):
    a4_width_mm = 200
    pt_to_mm = 0.35
    fontsize_pt = 11
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')
    print("PDF of summary Saved!!")

# This function split a huge corpus of text into small chunks or portions
def text_chunking(new_text):
  max_chunk = 500
  new_text = new_text.replace('.', '.<eos>')
  new_text = new_text.replace('?', '?<eos>')
  new_text = new_text.replace('!', '!<eos>')

  sentences = new_text.split('<eos>')
  current_chunk = 0 
  chunks = []
  for sentence in sentences:
      if len(chunks) == current_chunk + 1: 
          if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
              chunks[current_chunk].extend(sentence.split(' '))
          else:
              current_chunk += 1
              chunks.append(sentence.split(' '))
      else:
          # print(current_chunk)
          chunks.append(sentence.split(' '))

  for chunk_id in range(len(chunks)):
    chunks[chunk_id] = ' '.join(chunks[chunk_id])
  print("Total chunks of text are: ", len(chunks))
  return chunks


# This function takes in all the chunks, find the summary of each chunk and return all the summaries of chunks in list form. 
def model_summary(chunks):
  print("Summarizing the text. Please wait .......")
  all_summaries = []
  count = 0
  for chunk in chunks:
    print("Summarizing Chunk NO: ", count + 1)
    res = summarizer(chunk, max_length=3000, min_length=0, do_sample=False)
    all_summaries +=res
    count +=1
  return all_summaries



def find_summary(pdfdoc):
  #raw_text = extract_text(pdf_path)
    all_text = ''
  
    for i in range(len(pdfdoc.pages)):
        try:
            current_page = pdfdoc.pages[i]
            print("===================")
            print("Content on page:" + str(i + 1))
            print("===================")
      # final_text += str(summarizer(current_page.extract_text(), max_length=500, min_length=30, do_sample=True))

      #print(raw_text)  # Extract text from the path of pdf given
            chunks = text_chunking(current_page.extract_text())   # chunk the large text into small parts so it can be supplied to the model
            all_summaries = model_summary(chunks) # passing the chunks to the model for the summarization
            joined_summary = ' '.join([summ['summary_text'] for summ in all_summaries])  # combine all chunks of summaries to single
            txt_to_save = (joined_summary.encode('latin1','ignore')).decode("latin1")  # This ignore the "aphostrope" which is little problematic
            txt_to_save_prep = prep_b4_save(txt_to_save)
            all_text += txt_to_save_prep
            all_text += '\n'
    #   spl = pdf_path.split('/') # Splitting the path based on "/" to get the name of the book or pdf
    #   file_name = spl[-1][:-4]+f"{i}_summary.pdf" # Summary is added at the end i.e book name is the_alchemist so it becomes -> the_alchemist_summary.pdf etc. 
    #   text_to_pdf(txt_to_save_prep, file_name)
        except Exception as e:
            print(e)
            pass
    # spl = pdf_path.split('/') # Splitting the path based on "/" to get the name of the book or pdf
    file_name = "summary.pdf" # Summary is added at the end i.e book name is the_alchemist so it becomes -> the_alchemist_summary.pdf etc. 
    text_to_pdf(all_text, file_name)
    return all_text
def show_dashboard_page(session_st):
    # # Check if the user is logged in
    # query_params = st.experimental_get_query_params()
    # print(st.session_state['logged_in'] , query_params.get("logged_in", False))
    # if not st.session_state['logged_in'] and not query_params.get("logged_in"):
    #     # Redirect to the login page if not logged in
    #     st.experimental_set_query_params(logged_in=False)
    #     show_login_page(session_st)
    # else:
        # Get the query parameters
    query_params = st.experimental_get_query_params()
    if True:
        with st.form(key="upload-form"):
            st.title("Text Summarizer")
            st.write("Upload Your reserch papers below")

            # Create a file uploader
            uploaded_file = st.file_uploader("Choose a file")

            options = ["English", "Hindi", "Telugu","Tamil"]

            # Create a multiselect dropdown with the options
            selected_options = st.selectbox("Select options", options)
            lang_keys = {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta"}
        # Show the selected options
            submit_button = st.form_submit_button(label="Generate Summary")
        # Check if a file was uploaded
        if uploaded_file is not None and submit_button:
            # st.write("File contents:")
            # st.write(file_contents)
            st.write("Summary of the file is generating. Please wait .......")
            # Read the contents of the file
            file_contents = uploaded_file.read()
            pdfdoc = read_pdf(file_contents)
            alltxt = find_summary(pdfdoc)
            st.write("Summary of the file is generated. Please download the file .......")
            if alltxt is not None:
                st.download_button(
                    label="Download txt file",
                    data=alltxt.encode('utf-8'),
                    file_name="summary1.txt",
                    mime="text/plain",
                )
                fes = gen_conv_text(alltxt,lang_keys[selected_options])
                ad_path = gen_audio_of_text(fes,epoch_time,lang_keys[selected_options])
                audio_file = open(ad_path, "rb").read()

                # Play the audio file
                st.audio(audio_file, format="audio/mp3")

                # Create a download button for the audio file
                st.download_button(
                    label="Download audio file",
                    data=audio_file,
                    file_name="my_audio_file.mp3",
                    mime="audio/mp3"
                )
    else:
            # Redirect to the login page if no query parameter is set
        st.experimental_set_query_params(logged_in=False)


# query_params = st.experimental_get_query_params()
# print(query_params ,session_st.logged_in)
# if 'logged_in' not in st.session_state:
#     st.session_state['logged_in'] = False
#     show_login_page(session_st)
# else:
# # Create a menu with options for login and signup
#     menu = ["Home", "Login", "Signup"]
#     # Show a different menu if the user is logged in
#     if session_st.logged_in:
#         menu = ["Home", "Dashboard", "Logout"]
#     choice = st.sidebar.selectbox("Select a page", menu)

#     # Show the appropriate page based on the user's choice
#     if choice == "Home":
#         show_dashboard_page(session_st)
#     elif choice == "Login":
#         show_login_page(session_st)
#     elif choice == "Signup":
#         show_signup_page(session_st)
#     elif choice == "Dashboard":
#         show_dashboard_page(session_st)
#     elif choice == "Logout":
#         session_st.logged_in = False
#         st.success("Logged out!")
#     st.session_state['logged_in'] = True

def main():
    show_dashboard_page(session_st)
    

    # if session_st.logged_in and choice == "Home":
    #     pass
        # st.title("Text Summarizer")
        # st.write("Upload Your reserch papers below")

        # # Create a file uploader
        # uploaded_file = st.file_uploader("Choose a file")

        # options = ["English", "Hindi", "Telugu","Tamil"]

        # # Create a multiselect dropdown with the options
        # selected_options = st.multiselect("Select options", options)

        # # Show the selected options

        # # Check if a file was uploaded
        # if uploaded_file is not None:
        #     # st.write("File contents:")
        #     # st.write(file_contents)
        #     st.write("Summary of the file is generating. Please wait .......")
        #     # Read the contents of the file
        #     file_contents = uploaded_file.read()
        #     pdfdoc = read_pdf(file_contents)
        #     alltxt = find_summary(pdfdoc)
        #     st.write("Summary of the file is generated. Please download the file .......")
        #     if alltxt is not None:
        #         st.download_button(
        #             label="Download txt file",
        #             data=alltxt.encode('utf-8'),
        #             file_name="summary1.txt",
        #             mime="text/plain",
        #         )
        #         ad_path = gen_audio_of_text(alltxt)
        #         audio_file = open(ad_path, "rb").read()

        #         # Play the audio file
        #         st.audio(audio_file, format="audio/mp3")

        #         # Create a download button for the audio file
        #         st.download_button(
        #             label="Download audio file",
        #             data=audio_file,
        #             file_name="my_audio_file.mp3",
        #             mime="audio/mp3"
        #         )
            # Do something with the file contents
        


        
    
    # Add some text to the app
    # st.write("Welcome to my app!")
    
    # # Add a sidebar with some options
    # options = ["Option 1", "Option 2", "Option 3"]
    # selected_option = st.sidebar.selectbox("Select an option", options)
    
    # # Show some data based on the selected option
    # if selected_option == "Option 1":
    #     st.write("You selected Option 1")
    # elif selected_option == "Option 2":
    #     st.write("You selected Option 2")
    # else:
    #     st.write("You selected Option 3")
        
if __name__ == '__main__':
    main()