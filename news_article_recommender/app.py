import subprocess
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from fetch_news import fetch_and_update_news  # Your function

app = Flask(__name__)

# Initialize variables
df = None
tfidf_matrix = None
cos_sim = None

# Function to load data and update vectors
def update_recommendation_data():
    global df, tfidf_matrix, cos_sim
    fetch_and_update_news()
    df = pd.read_excel("static/News recommendation dataset (2).xlsx")
    df.columns = df.columns.str.strip()
    df['combined'] = df['headlines'].astype(str) + ". " + df['description'].astype(str)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['combined'])
    cos_sim = cosine_similarity(tfidf_matrix)

# Call once on startup
update_recommendation_data()

# Start background scheduler once
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_recommendation_data, trigger="interval", minutes=10)
scheduler.start()

# Recommendation logic
def recommend_articles(title, top_n=5):
    if title not in df['headlines'].values:
        return [("Error", "Title not found.", "#")]
    idx = df[df['headlines'] == title].index[0]
    sim_scores = list(enumerate(cos_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return [(df.iloc[i[0]]['headlines'], df.iloc[i[0]]['description'], df.iloc[i[0]]['link']) for i in sim_scores]

# Routes
@app.route('/')
def home():
    titles = df['headlines'].tolist()
    return render_template("index.html", titles=titles)

@app.route('/recommend', methods=['POST'])
def recommend():
    title = request.form['title']
    recommendations = recommend_articles(title)
    return render_template("result.html", title=title, recommendations=recommendations)

@app.route('/fetch-news')
def fetch_news():
    subprocess.run(["python", "fetch_news.py"])
    return '<h2 style="color:white;text-align:center;margin-top:50px;">✅ Live news fetched successfully!<br><br><a href="/" style="color:lime;">⬅ Back to Home</a></h2>'

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
