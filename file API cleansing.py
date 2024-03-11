#API
from flask import Flask, jsonify
import re
import sqlite3

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from


# Install Libraries/Packages
import re
import pandas as pd
import string

#text
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


# Time
import time
import datetime
from datetime import datetime

# NLTK
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
nltk.download('punkt')
from nltk.corpus import stopwords



#### flask
app = Flask(__name__)




# Remove special text using regex
def remove_text_special(text):
    # Remove non-ascii characters from the string
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    # Replace 2+ dots with space
    text = re.sub(r'\.{2,}', ' ', text)
    # Remove newline
    text = text.replace("\\n", "")
    # Remove hashtags
    text = re.sub(r'#', '', text)
    # Remove single character
    text = re.sub(r"\b[a-zA-Z]\b", "", text)
    # Remove number
    text = re.sub('[0-9]+', '', text)
    # Remove url
    text = re.sub(r"http\S+", "", text)
    # Strip space, " and ' from tweet
    text = text.strip(' "\'')
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove url uncomplete
    text = text.replace("http://", " ").replace("https://", " ")
    # Remove punctuation
    text = text.translate(str.maketrans("","",string.punctuation))
  
    return text

# Remove the word 'USER'
def remove_user(df, column_name):
    df[column_name] = df[column_name].str.replace(r'USER', '', regex=True)
    return df[column_name]

# Remove the word 'RT'
def remove_RT(df, column_name):
    df[column_name] = df[column_name].str.replace(r'RT', '', regex=True)
    return df[column_name]

# Lowercase the letters
def lowercase_letters(df, column_name):
    df[column_name] = df[column_name].str.lower()
    return df[column_name]

# Remove abusive words
def remove_abusive_words(df, column_name):
    # Load abusive words from the CSV file
    abusive_words_df = pd.read_csv('abusive.csv', encoding='latin-1')
    abusive_words = abusive_words_df['ABUSIVE'].tolist()

    # Convert specified column to string type
    df[column_name] = df[column_name].astype(str)

    # Replace or remove abusive words from the DataFrame
    for word in abusive_words:
        df[column_name] = df[column_name].str.replace(word, '')

    return df[column_name]

# Remove stopwords
def remove_stopwords(df, column_name):
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    
    df[column_name] = df[column_name].apply(lambda x: " ".join(stopword.remove(x) for x in x.split()))
    return df[column_name]

# Tokenizing
def word_tokenize_wrapper(text):
    if isinstance(text, str):
        return word_tokenize(text)
    else:
        return text

# Convert slang words
    # Read slang vocabulary dictionary
convert_slang_word = pd.read_csv("new_kamusalay.csv", encoding='latin-1')

    # Create a variable in the form of a dictionary that will store the results of convert slang word function
convert_slang_word_dict = {}

for index, row in convert_slang_word.iterrows():
    if row[0] not in convert_slang_word_dict:
        convert_slang_word_dict[row[0]] = row[1]

    # Function for convert slang word
def convert_slang_word_term(document):
    if isinstance(document, float):
        return document
    else:
        return [convert_slang_word_dict[term] if term in convert_slang_word_dict else term for term in document]
    
# Stemming
def stemming_process(df, column_name):
    # Record the start time
    start_time = datetime.now()

    # create stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    # stemming process
    df[column_name] = df[column_name].apply(lambda x: stemmer.stem(' '.join(x)) if isinstance(x, list) else stemmer.stem(x))
    return df[column_name]

    # Record the end time
    end_time = datetime.now()

    # Print the duration
    duration = end_time - start_time
    print("Stemming process took:", duration)



###swager
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Challenge Gold Ardhini'),
    # 'version': LazyString(lambda: '1.0.0'),
    # 'description': LazyString(lambda: 'Dokumentasi API'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)



###body api
@swag_from("./docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'data': "Hello World"
    }
    return jsonify(json_response)



@swag_from(".docs/text_processing.yml", methods=['POST'])
@app.route('/input_teks', methods=['POST'])
def input_teks():
    data = request.form.get('text')
    data_uper = remove_text_special(data)

    json_response = {
        'output': data_uper
    }
    return jsonify(json_response)


@swag_from("./docs/text_processing_file1.yml", methods=['POST'])
@app.route('/text-processing-file1', methods=['POST'])
def text_processing_file():
    # Get the uploaded file
    file = request.files.getlist('file')[0]

    # Read the uploaded CSV file into a DataFrame
    df_data = pd.read_csv(file, encoding='Latin-1')



    # Cleanse the texts using the remove_text_special function
    df_data['Tweet_cleaned'] = df_data['Tweet'].apply(remove_text_special)
    
    df_data['Tweet_cleaned'] = remove_RT(df_data, 'Tweet_cleaned')
    
    df_data['Tweet_cleaned'] = remove_user(df_data, 'Tweet_cleaned')
    
    df_data['Tweet_cleaned'] = lowercase_letters(df_data, 'Tweet_cleaned')
    
    df_data['Tweet_cleaned'] = remove_abusive_words(df_data,'Tweet_cleaned')
    
    df_data['Tweet_cleaned'] = remove_stopwords(df_data,'Tweet_cleaned')
    
    df_data['Tweet_cleaned'] = df_data['Tweet_cleaned'].apply(word_tokenize_wrapper)
    
    df_data['Tweet_cleaned'] = df_data['Tweet_cleaned'].apply(convert_slang_word_term)
    
    df_data['Tweet_cleaned'] = stemming_process(df_data, 'Tweet_cleaned')

    df_data.dropna(subset=['Tweet_cleaned'], inplace = True)
    
     # Save the cleaned dataframe to SQLite3
    conn = sqlite3.connect('cleansing.db')
    df_data.to_sql(name='Tweets', con=conn, if_exists='replace', index=False)
    
    # Close database
    conn.close()
    
    # Extract the 'Tweet' column from the DataFrame
    texts = df_data['Tweet_cleaned'].tolist()
    
    # Construct the JSON response
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': texts,
    }

    # Convert the JSON response to a Flask response object
    response_data = jsonify(json_response)

    # Return the response
    return response_data




##running api
if __name__ == '__main__':
   app.run()






