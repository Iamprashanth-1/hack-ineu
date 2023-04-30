
# Inueron Hackathon

This is Prashanth Reddy Worked on below problem statement.

Multi-Language Audio Summarization of Research Papers
 
The proposed project aims to develop a system for summarising research papers and converting the summaries into multilingual audio. The system will leverage natural language processing (NLP) and text-to-speech (TTS) technologies to generate concise summaries of research papers in multiple languages, which will then be converted into audio files for easy consumption by non-native speakers and people with visual impairments. This system has the potential to improve accessibility to research papers and make scientific information more widely available and easily understandable to people around the world.

## Approach :

- Step-1: Used Pre-exsiting model developed by facebook (https://huggingface.co/facebook/bart-large-cnn)

- Step-2: Used Transfomers to load the model.

- Step-3: created Simple UI using Streamlit which takes file as an input(PDF file) and language of choice

- Step-3: processing an input PDF file by splitting it into smaller chunks, which are then fed into a summarization model. The model generates a summary based on each chunk, and the individual summaries are combined to form a final summary of the PDF file.

- Step-4: Once the summary is generated, the program uses the deep_translator library to translate the text into the user's selected language. The program then uses the gTTs library to convert the translated text into speech

- Step-5: Allowing users to download both summarized and audio file



## Installation

Install the project dependencies with pip

```bash
  pip install -r requirements.txt
  
```
    
## Project Flow

![flow](https://github.com/Iamprashanth-1/hack-ineu/blob/master/images/arch.png)

