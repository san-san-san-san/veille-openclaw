#!/usr/bin/env python3
"""
Veille Twitter - Version améliorée avec multiples sources
Utilise plusieurs méthodes pour garantir des résultats
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re

# Configuration
KEYWORDS = [
    "openclaw",
    "claude code",
    "anthropic claude",
    "OpenClaw"
]

def search_twitter_syndication(keyword, max_tweets=15):
    """
    Méthode 1 : Twitter Syndication API (publique, pas d'auth)
    Plus fiable que Nitter
    """
    tweets = []
    
    try:
        # Encode keyword
        encoded_keyword = requests.utils.quote(keyword)
        
        # Twitter embed search (API publique)
        url = f"https://cdn.syndication.twimg.com/srv/timeline-profile/screen-name/search?q={encoded_keyword}&count={max_tweets}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://twitter.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for tweet_data in data.get('tweets', {}).values():
                try:
                    tweet = {
                        'username': '@' + tweet_data.get('user', {}).get('screen_name', 'unknown'),
                        'content': tweet_data.get('text', ''),
                        'date': tweet_data.get('created_at', 'Récent'),
                        'likes': tweet_data.get('favorite_count', 0),
                        'retweets': tweet_data.get('retweet_count', 0),
                        'keyword': keyword,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'twitter_syndication'
                    }
                    tweets.append(tweet)
                except Exception as e:
                    continue
            
            print(f"✅ Syndication API: {len(tweets)} tweets pour '{keyword}'")
    
    except Exception as e:
        print(f"⚠️  Syndication API échouée: {e}")
    
    return tweets

def search_nitter_fallback(keyword, max_tweets=15):
    """
    Méthode 2 : Nitter (instances multiples)
    """
    nitter_instances = [
        "https://nitter.poast.org",
        "https://nitter.privacydev.net",
        "https://nitter.net",
        "https://nitter.unixfox.eu"
    ]
    
    tweets = []
    
    for instance in nitter_instances:
        try:
            search_url = f"{instance}/search?f=tweets&q={keyword.replace(' ', '%20')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                tweet_containers = soup.select('.timeline-item')
                
                for container in tweet_containers[:max_tweets]:
                    try:
                        username_elem = container.select_one('.username')
                        content_elem = container.select_one('.tweet-content')
                        date_elem = container.select_one('.tweet-date a')
                        
                        if username_elem and content_elem:
                            tweet = {
                                'username': username_elem.text.strip(),
                                'content': content_elem.get_text(strip=True),
                                'date': date_elem.get('title', 'Récent') if date_elem else 'Récent',
                                'keyword': keyword,
                                'timestamp': datetime.now().isoformat(),
                                'source': f'nitter_{instance.split("//")[1].split(".")[0]}'
                            }
                            tweets.append(tweet)
                    except:
                        continue
                
                if tweets:
                    print(f"✅ Nitter ({instance}): {len(tweets)} tweets pour '{keyword}'")
                    break
        
        except Exception as e:
            print(f"⚠️  {instance} échoué: {e}")
            continue
        
        time.sleep(random.uniform(1, 2))
    
    return tweets

def search_twitter_via_google(keyword, max_results=10):
    """
    Méthode 3 : Google Search "site:twitter.com"
    Récupère les tweets indexés par Google
    """
    tweets = []
    
    try:
        google_query = f"site:twitter.com {keyword}"
        google_url = f"https://www.google.com/search?q={requests.utils.quote(google_query)}&num={max_results}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(google_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse résultats Google
            search_results = soup.select('.g')
            
            for result in search_results[:max_results]:
                try:
                    link_elem = result.select_one('a')
                    snippet_elem = result.select_one('.VwiC3b')
                    
                    if link_elem and snippet_elem:
                        url = link_elem.get('href', '')
                        
                        # Vérifier que c'est bien un tweet
                        if 'twitter.com/' in url and '/status/' in url:
                            # Extraire username depuis URL
                            username_match = re.search(r'twitter\.com/([^/]+)/', url)
                            username = '@' + username_match.group(1) if username_match else '@unknown'
                            
                            tweet = {
                                'username': username,
                                'content': snippet_elem.get_text(strip=True),
                                'date': 'Via Google',
                                'url': url,
                                'keyword': keyword,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'google_twitter'
                            }
                            tweets.append(tweet)
                except:
                    continue
            
            print(f"✅ Google Twitter: {len(tweets)} tweets pour '{keyword}'")
    
    except Exception as e:
        print(f"⚠️  Google Twitter échoué: {e}")
    
    return tweets

def scrape_twitter_all_methods(keyword):
    """
    Utilise TOUTES les méthodes et combine les résultats
    """
    print(f"\n🔍 Recherche Twitter: '{keyword}'")
    
    all_tweets = []
    
    # Méthode 1 : Syndication API (prioritaire)
    tweets_syndication = search_twitter_syndication(keyword, max_tweets=10)
    all_tweets.extend(tweets_syndication)
    time.sleep(random.uniform(2, 4))
    
    # Méthode 2 : Nitter (si Syndication a échoué ou peu de résultats)
    if len(all_tweets) < 5:
        tweets_nitter = search_nitter_fallback(keyword, max_tweets=10)
        all_tweets.extend(tweets_nitter)
        time.sleep(random.uniform(2, 4))
    
    # Méthode 3 : Google (complément)
    if len(all_tweets) < 8:
        tweets_google = search_twitter_via_google(keyword, max_results=5)
        all_tweets.extend(tweets_google)
    
    # Dédupliquer (par contenu)
    seen_contents = set()
    unique_tweets = []
    
    for tweet in all_tweets:
        content_key = tweet['content'][:100]  # Premiers 100 chars
        if content_key not in seen_contents:
            seen_contents.add(content_key)
            unique_tweets.append(tweet)
    
    print(f"   ✅ Total: {len(unique_tweets)} tweets uniques")
    
    return unique_tweets

def scrape_reddit(keyword, max_posts=10):
    """Scrape Reddit (inchangé)"""
    posts = []
    
    try:
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
    """Scrape Hacker News (inchangé)"""
    items = []
    
    try:
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
    print("🔍 VEILLE QUOTIDIENNE - OpenClaw & Claude Code v2")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*60)
    
    all_data = {
        'date': datetime.now().isoformat(),
        'twitter': [],
        'reddit': [],
        'hackernews': []
    }
    
    # Twitter (méthodes multiples)
    print("\n🐦 TWITTER (méthodes multiples)")
    for keyword in KEYWORDS:
        tweets = scrape_twitter_all_methods(keyword)
        all_data['twitter'].extend(tweets)
        time.sleep(random.uniform(3, 6))
    
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
