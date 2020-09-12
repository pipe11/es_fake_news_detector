<p align="center">
  <img src="https://github.com/pipe11/TFM_fake_news_detector/blob/master/imgs/wordcloud_fakenews.png">
</p>

# FAKE NEWS DETECTOR

This is the repository for the resulting **Front-end Web Application** for heroku server service hosting. This is the result of the **Fake News Detector Project**, and the main repository of this project is **[here](https://github.com/pipe11/TFM_fake_news_detector)**.

After the server deployment, the **Web Application** is online and workin. **[¡Try it!](https://es-fake-news-detector.herokuapp.com/)**

## Guide for the app deployment

We decided to lauch our Web Application with the **[Heroku](https://dashboard.heroku.com/)** hosting services, it is a **platform as a service (PaaS)** that enables developers to build, run, and operate applications entirely in the cloud. We followed the [heroku's guide](https://devcenter.heroku.com/articles/getting-started-with-python) to deploy our app.

**[1. Create a Heroku Account](https://signup.heroku.com/signup/dc)** which it allows you to syncronize your GitHub repository where you have stored your files.

**[2. Install Heroku CLI on Git](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)**. This step is note necessary but I recommend the usage of the Heorku CLI for deploy your server properly and check if there are errors.

**3. Files needed on your repor**: You must have all the following files stored on the repository you are syncronizing with Heroku:
- **Requirements.txt** with all the **packages needed** and their **versions**, this file lists the app dependencies to install all the packages on the server, e.g on my case:
```
pandas==1.1.1
numpy==1.19.1
streamlit==0.65.2
nltk==3.5
regex==2020.7.14
lexical-diversity==0.1.1
newspaper3k==0.2.8
tldextract==2.2.3
syltippy==1.0
scikit-learn==0.23.1
xgboost==1.1.1
spacy==2.3.2
https://github.com/explosion/spacy-models/releases/download/es_core_news_md-2.3.1/es_core_news_md-2.3.1.tar.gz#egg=es_core_news_md==2.3.1
```

-**NLTK.text**, In our case, as we are using some modules of the **NLTK package**, we need another .txt file for these packages, e.g. on our case:
```
stopwords
punkt
```

- **Procfile**, a text file in the root directory of your application, to explicitly declare what command should be executed to start your app, e.g. on my case:
```
web: sh setup.sh && streamlit run fake_news_detector_app.py
```

- **setup.sh**, this text file creates a config.toml with the server configuration, e.g. on my case:
```
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

- **Python script**: A Python script with all the code necessary tu run the app, e.g. on my cas: **fake_news_detector_app.py**

- **Additional files**: If you want you can add as many images as you want for your **front-end**, if you are using **data or pickle models** you must store it on your repository too.

**4. Deploy Heroku Server**: On my case I used the **Heroku CLI** and the following commands to create my app:
- ```heroku create <<app name>> --region eu```
- ```heroku git:remote -a <<app name>>```
- ```git push heroku master```
After this manual deploy, you can enable **automatic deploys** at the heroku control panel of your app. This enables automatic deployments every time you **update your repository** with new data and files.

The final result of this guide and my whole project is the following app: **[es-fake-news-detector]**((https://es-fake-news-detector.herokuapp.com/)

## User considerations

- You must **paste the URL** of the newspaper article for the app work properly, **not the content of the text**.
- This app only works on articles written in **Spanish language**, any attempt with other language will result into an error.
- Don't use it with **premium newspaper articles**. If you are pasting an URL of a **premium newspaper article**, the classification is not going to work properly as it only scrapes a short fragment of the article
