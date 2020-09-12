
import streamlit as st
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords  
from nltk import word_tokenize    
from nltk.stem import SnowballStemmer  
from string import punctuation
import re
import spacy
#need to switch to es_core_news_md pacy model. es_core_news_lg too large for Heroku.
import es_core_news_md
from nltk import FreqDist
from lexical_diversity import lex_div as ld
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix
from langdetect import detect
from langdetect import detect_langs

#### extract news with url ####

def extract_news(url):
    with st.spinner("Detectando..."):
        from newspaper import Article
        import tldextract
        
        article = Article(url)
        
        try:
            article.download()
            
        except:
            st.error('**El formato introducido no es correcto.** Introduce unicamente la URL de un periódico.')
            st.write('**¡Prueba con otra!**')
            st.image('./error_darth_vader.png', use_column_width = True, width = None)
        
        article.download()
        article.parse()
        ext = tldextract.extract(url)
        newspaper = ext.domain
        image_url = article.top_image
        
        headline = article.title
        text = article.text
        
        if article.authors == []:
            author = []
        else:
            author = article.authors
            
        return headline, text, author, newspaper, image_url

@st.cache(show_spinner = False)
def get_nsyllables(text):
    from syltippy import syllabize
    
    text = text.replace(r"*URL*", "url")
    text = re.sub(r'\d+', '', text)
    text = re.sub('\n', '', text)
    text = re.sub(r'[^ \nA-Za-z0-9ÁÉÍÓÚÑáéíóúñ/]+', '', text)
    
    n_syllables = len(syllabize(text)[0])
    
    return n_syllables


#### text features ####

@st.cache(show_spinner = False)
def get_news_features(headline, text):
    
    nlp = es_core_news_md.load()

    ## headline ##
    headline = re.sub(r"http\S+", "", headline)
    headline = re.sub(r"http", "", headline)
    headline = re.sub(r"@\S+", "", headline)
    headline = re.sub("\n", " ", headline)
    headline = re.sub(r"(?<!\n)\n(?!\n)", " ", headline)
    headline = headline.replace(r"*NUMBER*", "número")
    headline = headline.replace(r"*PHONE*", "número")
    headline = headline.replace(r"*EMAIL*", "email")
    headline = headline.replace(r"*URL*", "url")
    headline_lower = headline.lower()
    doc_h = nlp(headline_lower)

    list_tokens_h = []
    list_tags_h = []

    for sentence_h in doc_h.sents:
        for token in sentence_h:
            list_tokens_h.append(token.text)

    fdist_h = FreqDist(list_tokens_h)
    syllables_h = get_nsyllables(headline)
    words_h = len(list_tokens_h)

    # headline complexity features
    avg_word_size_h = round(sum(len(word) for word in list_tokens_h) / words_h, 2)
    avg_syllables_word_h = round(syllables_h / words_h, 2)
    unique_words_h = round((len(fdist_h.hapaxes()) / words_h) * 100, 2)
    mltd_h = round(ld.mtld(list_tokens_h), 2)
    ttr_h = round(ld.ttr(list_tokens_h) * 100, 2)

    ## text content##     
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"http", "", text)
    text = re.sub("\n", " ", text)
    text = text.replace(r"*NUMBER*", "número")
    text = text.replace(r"*PHONE*", "número")
    text = text.replace(r"*EMAIL*", "email")
    text = text.replace(r"*URL*", "url")

    # to later calculate upper case letters ratio
    alph = list(filter(str.isalpha, text))
    text_lower = text.lower()
    doc = nlp(text_lower)

    list_tokens = []
    list_pos = []
    list_tag = []
    list_entities = []
    sents = 0

    for entity in doc.ents:
        list_entities.append(entity.label_)

    for sentence in doc.sents:
        sents += 1
        for token in sentence:
            list_tokens.append(token.text)
            list_pos.append(token.pos_)
            list_tag.append(token.tag_)

    # Calculate entities, pos, tag, freq, syllables, words and quotes
    entities = len(list_entities)
    n_pos = nltk.Counter(list_pos)
    n_tag = nltk.Counter(list_tag)
    fdist = FreqDist(list_tokens)
    syllables = get_nsyllables(text)
    words = len(list_tokens)
    quotes = n_tag['PUNCT__PunctType=Quot']

    # complexity features
    avg_word_sentence = round(words / sents, 2)
    avg_word_size = round(sum(len(word) for word in list_tokens) / words, 2)
    avg_syllables_word = round(syllables / words, 2)
    unique_words = round((len(fdist.hapaxes()) / words) * 100, 2)
    ttr = round(ld.ttr(list_tokens) * 100, 2)

    # readability spanish test
    huerta_score = round(206.84 - (60 * avg_syllables_word) - (1.02 * avg_word_sentence), 2)
    szigriszt_score = round(206.835 - ((62.3 * syllables) / words) - (words / sents), 2)

    # stylometric features
    mltd = round(ld.mtld(list_tokens), 2)
    upper_case_ratio = round(sum(map(str.isupper, alph)) / len(alph) * 100, 2)
    entity_ratio = round((entities / words) * 100, 2)
    quotes_ratio = round((quotes / words) * 100, 2)
    propn_ratio = round((n_pos['PROPN'] / words) * 100 , 2)
    noun_ratio = round((n_pos['NOUN'] / words) * 100, 2) 
    pron_ratio = round((n_pos['PRON'] / words) * 100, 2)
    adp_ratio = round((n_pos['ADP'] / words) * 100, 2)
    det_ratio = round((n_pos['DET'] / words) * 100, 2)
    punct_ratio = round((n_pos['PUNCT'] / words) * 100, 2)
    verb_ratio = round((n_pos['VERB'] / words) * 100, 2)
    adv_ratio = round((n_pos['ADV'] / words) * 100, 2)
    sym_ratio = round((n_tag['SYM'] / words) * 100, 2)

    # create df_features
    df_features = pd.DataFrame({'text': text_lower, 'headline':headline_lower, 'words_h': words_h, 'word_size_h': [avg_word_size_h],
                                'avg_syllables_word_h': [avg_syllables_word_h],'unique_words_h': [unique_words_h], 
                                'ttr_h': ttr_h, 'mltd_h': [mltd_h], 'sents': sents, 'words': words,
                                'avg_words_sent': [avg_word_sentence], 'avg_word_size': [avg_word_size], 
                                'avg_syllables_word': avg_syllables_word, 'unique_words': [unique_words], 
                                'ttr': [ttr], 'huerta_score': [huerta_score], 'szigriszt_score': [szigriszt_score],
                                'mltd': [mltd], 'upper_case_ratio': [upper_case_ratio], 'entity_ratio': [entity_ratio],
                                'quotes': quotes, 'quotes_ratio': [quotes_ratio], 'propn_ratio': [propn_ratio], 
                                'noun_ratio': [noun_ratio], 'pron_ratio': [pron_ratio], 'adp_ratio': [adp_ratio],
                                'det_ratio': [det_ratio], 'punct_ratio': [punct_ratio], 'verb_ratio': [verb_ratio],
                                'adv_ratio': [adv_ratio], 'sym_ratio': [sym_ratio]})
    
    return df_features  

#### TF-IDF Transformation ####

#Stopword list to use
spanish_stopwords = stopwords.words('spanish')

#Spanish stemmer:
stemmer = SnowballStemmer('spanish')

@st.cache(show_spinner = False)
def stem_tokens(tokens, stemmer):  
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#Punctuation to remove
non_words = list(punctuation)

#Adding spanish punctuation
non_words.extend(['¿', '¡', '‘', '’', '“', '”'])  
non_words.extend(map(str, range(10)))

@st.cache(show_spinner = False)
def tokenize(text):  
    #Remove punctuation
    text = ''.join([c for c in text if c not in non_words])
    #Tokenize
    tokens =  word_tokenize(text)

    #Stem
    try:
        stems = stem_tokens(tokens, stemmer)
    except Exception as e:
        print(e)
        print(text)
        stems = ['']
    return stems


#### predictions ####

@st.cache(show_spinner = False)
def get_predictions(pickle_file_model, pickle_file_transformer, df_features):
    with st.spinner("Detectando..."):
        import pickle
        model = pickle.load(open(pickle_file_model, 'rb'))
        tfidf_vectorizer = pickle.load(open(pickle_file_transformer, 'rb'))
        
        
        numeric_features = ['words_h', 'word_size_h', 'avg_syllables_word_h', 'unique_words_h', 'ttr_h', 'mltd_h', 'sents',
                            'words', 'avg_words_sent', 'avg_word_size', 'avg_syllables_word', 'unique_words', 'ttr', 'mltd', 
                            'huerta_score', 'szigriszt_score','upper_case_ratio', 'entity_ratio', 'quotes', 'quotes_ratio',
                            'propn_ratio', 'noun_ratio', 'adp_ratio', 'det_ratio', 'punct_ratio', 'pron_ratio', 'verb_ratio', 
                            'adv_ratio', 'sym_ratio']

        
        #TF-IDF vectorization
        text_predict_vectorized = tfidf_vectorizer.transform(df_features['text'])
        X_predict = hstack([csr_matrix(df_features[numeric_features].values), text_predict_vectorized[0:]])

        # prediction
        prediction = (model.predict(X_predict)[0])
        prob_fake = (model.predict_proba(X_predict)[0][0])*100
        prob_real = (model.predict_proba(X_predict)[0][1])*100
    
    return prob_fake, prob_real

#### streamlit configuration ####


# load pickle files
pickle_file_model = './fake_news_predictorv4.pkl'
pickle_file_transformer = './tfidf_vectorizer.pkl'

# page configuration
page_title = 'Fake News Detector'
layout = 'wide'
initial_sidebar_state = 'expanded'

# display title and description
st.title("Detector de")
st.image('./wordcloud_fakenews.png', use_column_width = True, width = None, output_format = 'auto')

# text input for headline and new's content
try:
    url = st.text_input("Pega el enlace de una noticia")
except ValueError:
    st.error('Por favor introduce un enlace únicamente')
    st.image('./error_darth_vader.png', use_column_width = True, width = None)


## run functions##
if (url != ""):
    
    headline, text, author, newspaper, image_url = extract_news(url)       
    
    if detect(text) == 'es' and len(detect_langs(text)) == 1:
        df_features = get_news_features(headline, text)
        
        prob_fake, prob_real = get_predictions(pickle_file, df_features)

        if prob_fake >= 65:
            st.error('¡¡Esta noticia es **FALSA**!! :heavy_multiplication_x: \nCon una probabilidad del %d%%.' % int(prob_fake))

        elif (65 >= prob_fake >= 35):
            st.warning('¡Esta noticia es **ENGAÑOSA**! :exclamation: \nTiene una probabilidad de %d%% de ser verdadera.' % int(prob_real))

        else:
            st.success('Esta noticia es **VERDADERA** :white_check_mark: \nCon una probabilidad del %d%%.' % int(prob_real))

        st.title(headline)
        st.write(newspaper)
        st.image(image_url, use_column_width = True, width = None)
        if author == []:
            st.write('Autor no encontrado')
        else:
            st.write('Autor: ', author[0])
        st.write('Noticia: ', text)
        
    else:
        st.error('¡Esta noticia **no está en español** o tiene mucho contenido en otro idioma!')
        st.write('**¡Prueba con otra!**')
        st.image('./error_darth_vader.png', use_column_width = True, width = None)
        
