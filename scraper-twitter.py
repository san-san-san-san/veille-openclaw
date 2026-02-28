#!/usr/bin/env python3
"""
Veille Twitter - OpenClaw & Claude Code
Scrape les derniers tweets et discussions
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

# Configuration
KEYWORDS = [
    "openclaw",
    "claude code",
    "@anthropic claude code",
    "OpenClaw AI"
]

NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net"
]

def scrape_twitter(keyword, max_tweets=20):
    """Scrape Twitter via Nitter (instances publiques)"""
    
    tweets = []
    
    for instance in NITTER_INSTANCES:
        try:
            # Recherche sur Nitter
            search_url = f"{instance}/search?f=tweets&q={keyword.replace(' ', '%20')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse tweets
                tweet_elements = soup.find_all('div', class_='timeline-item')
                
                for tweet_elem in tweet_elements[:max_tweets]:
                    try:
                        # Extraire infos tweet
                        username = tweet_elem.find('a', class_='username')
                        content = tweet_elem.find('div', class_='tweet-content')
                        date = tweet_elem.find('span', class_='tweet-date')
                        
                        if username and content:
                            tweet = {
                                'username': username.text.strip(),
                                'content': content.text.strip(),
                                'date': date.text.strip() if date else 'Récent',
                                'keyword': keyword,
                                'timestamp': datetime.now().isoformat()
                            }
                            tweets.append(tweet)
                    except:
                        continue
                
                # Si on a trouvé des tweets, pas besoin d'essayer d'autres instances
                if tweets:
                    print(f"✅ {len(tweets)} tweets trouvés pour '{keyword}' sur {instance}")
                    break
            
        except Exception as e:
            print(f"⚠️  {instance} échoué: {e}")
            continue
        
        # Pause entre instances
        time.sleep(random.uniform(1, 3))
    
    return tweets

def scrape_reddit(keyword, max_posts=10):
    """Scrape Reddit pour discussions"""
    
    posts = []
    
    try:
        # Reddit JSON API (publique)
        search_url = f"https://www.reddit.com/search.json?q={keyword.replace(' ', '%20')}&sort=new&limit={max_posts}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                
                posts.append({
                    'title': post_data.get('title', ''),
                    'subreddit': post_data.get('subreddit', ''),
                    'author': post_data.get('author', ''),
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'score': post_data.get('score', 0),
                    'comments': post_data.get('num_comments', 0),
                    'created': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    'keyword': keyword
                })
            
            print(f"✅ {len(posts)} posts Reddit trouvés pour '{keyword}'")
    
    except Exception as e:
        print(f"❌ Reddit scraping échoué: {e}")
    
    return posts

def scrape_hackernews(keyword, max_items=10):
    """Scrape Hacker News"""
    
    items = []
    
    try:
        # HN Algolia API
        search_url = f"https://hn.algolia.com/api/v1/search?query={keyword.replace(' ', '%20')}&tags=story&hitsPerPage={max_items}"
        
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for hit in data.get('hits', []):
                items.append({
                    'title': hit.get('title', ''),
                    'author': hit.get('author', ''),
                    'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                    'points': hit.get('points', 0),
                    'comments': hit.get('num_comments', 0),
                    'created': hit.get('created_at', ''),
                    'keyword': keyword
                })
            
            print(f"✅ {len(items)} items Hacker News trouvés pour '{keyword}'")
    
    except Exception as e:
        print(f"❌ HN scraping échoué: {e}")
    
    return items

def run_daily_scrape():
    """Exécute la veille quotidienne complète"""
    
    print("="*60)
    print("🔍 VEILLE QUOTIDIENNE - OpenClaw & Claude Code")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*60)
    
    all_data = {
        'date': datetime.now().isoformat(),
        'twitter': [],
        'reddit': [],
        'hackernews': []
    }
    
    # Twitter
    print("\n🐦 TWITTER")
    for keyword in KEYWORDS:
        print(f"\n   Recherche: {keyword}")
        tweets = scrape_twitter(keyword, max_tweets=10)
        all_data['twitter'].extend(tweets)
        time.sleep(random.uniform(2, 5))
    
    # Reddit
    print("\n\n🔴 REDDIT")
    for keyword in KEYWORDS:
        print(f"\n   Recherche: {keyword}")
        posts = scrape_reddit(keyword, max_posts=5)
        all_data['reddit'].extend(posts)
        time.sleep(random.uniform(2, 4))
    
    # Hacker News
    print("\n\n🟠 HACKER NEWS")
    for keyword in KEYWORDS:
        print(f"\n   Recherche: {keyword}")
        items = scrape_hackernews(keyword, max_items=5)
        all_data['hackernews'].extend(items)
        time.sleep(random.uniform(2, 4))
    
    # Sauvegarder résultats
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'veille-{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # Sauvegarder aussi comme "latest"
    with open('veille-latest.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n\n" + "="*60)
    print("✅ VEILLE TERMINÉE")
    print("="*60)
    print(f"🐦 Twitter: {len(all_data['twitter'])} tweets")
    print(f"🔴 Reddit: {len(all_data['reddit'])} posts")
    print(f"🟠 HN: {len(all_data['hackernews'])} items")
    print(f"💾 Sauvegardé: {filename}")
    print("="*60)

if __name__ == "__main__":
    run_daily_scrape()
