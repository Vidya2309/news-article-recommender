import requests
import pandas as pd

API_KEY = ' https://newsapi.org.'  # Replace with your actual key
NEWS_URL = 'https://newsapi.org/v2/top-headlines'
PARAMS = {
    'country': 'in',  # You can change country code
    'pageSize': 10,
    'apiKey': API_KEY
}

def fetch_and_update_news(file_path='static/News recommendation dataset (2).xlsx'):
    response = requests.get(NEWS_URL, params=PARAMS)
    articles = response.json().get('articles', [])

    data = []
    for article in articles:
        headline = article.get('title', 'No Title')
        desc = article.get('description', 'No Description')
        link = article.get('url', '#')
        source = article.get('source', {}).get('name', 'Unknown')
        data.append({'headlines': headline, 'description': desc, 'link': link, 'newspaper': source, 'catagories': 'Real-time'})

    df_new = pd.DataFrame(data)
    
    try:
        df_old = pd.read_excel(file_path)
        df_combined = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset='headlines')
        df_combined.to_excel(file_path, index=False)
        print("✅ News updated successfully!")
    except Exception as e:
        print("❌ Error updating news:", e)

# Optional: Run this file manually to fetch latest news
if __name__ == "__main__":
    fetch_and_update_news()
