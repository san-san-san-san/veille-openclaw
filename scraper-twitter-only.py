#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Twitter Only avec Résumé IA en Français
Veille OpenClaw & Claude Code
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time

# Keywords à surveiller
KEYWORDS = [
    "openclaw",
    "claude code",
    "@anthropic claude code",
    "OpenClaw AI"
]

# Multiple Nitter instances (fallback)
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.net",
]

def scrape_twitter_syndication(keyword, max_results=10):
    """Scrape Twitter via API Syndication publique"""
    tweets = []
    
    try:
        # Twitter Syndication API (public, pas d'auth requise)
        url = f"https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=anthropic,OpenClawAI&count=10"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data:
                if any(kw.lower() in item.get('text', '').lower() for kw in [keyword]):
                    tweets.append({
                        'username': item.get('user', {}).get('screen_name', 'Unknown'),
                        'content': item.get('text', ''),
                        'date': item.get('created_at', datetime.now().isoformat()),
                        'keyword': keyword,
                        'url': f"https://twitter.com/{item.get('user', {}).get('screen_name', '')}/status/{item.get('id_str', '')}"
                    })
        
    except Exception as e:
        print(f"Twitter Syndication API error for '{keyword}': {e}")
    
    return tweets

def scrape_twitter_nitter(keyword, max_results=10):
    """Scrape Twitter via Nitter instances"""
    tweets = []
    
    for instance in NITTER_INSTANCES:
        try:
            # Search URL
            search_url = f"{instance}/search?f=tweets&q={keyword.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find tweet containers
            tweet_containers = soup.find_all('div', class_='timeline-item')
            
            for container in tweet_containers[:max_results]:
                try:
                    # Extract username
                    username_elem = container.find('a', class_='username')
                    username = username_elem.get('title', '').lstrip('@') if username_elem else 'Unknown'
                    
                    # Extract content
                    content_elem = container.find('div', class_='tweet-content')
                    content = content_elem.get_text(strip=True) if content_elem else ''
                    
                    # Extract date
                    date_elem = container.find('span', class_='tweet-date')
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().isoformat()
                    
                    # Extract URL
                    link_elem = container.find('a', class_='tweet-link')
                    tweet_url = instance + link_elem.get('href', '') if link_elem else ''
                    
                    if content:
                        tweets.append({
                            'username': username,
                            'content': content,
                            'date': date,
                            'keyword': keyword,
                            'url': tweet_url.replace(instance, 'https://twitter.com')
                        })
                
                except Exception as e:
                    continue
            
            # Si on a trouvé des tweets, pas besoin d'essayer d'autres instances
            if tweets:
                print(f"✓ Nitter instance {instance} OK - {len(tweets)} tweets trouvés")
                break
        
        except Exception as e:
            print(f"Nitter instance {instance} failed: {e}")
            continue
    
    return tweets

def scrape_twitter_google(keyword, max_results=10):
    """Scrape Twitter via Google search (fallback)"""
    tweets = []
    
    try:
        search_query = f"site:twitter.com {keyword}"
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            results = soup.find_all('div', class_='g')
            
            for result in results[:max_results]:
                try:
                    # Extract title
                    title_elem = result.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Extract URL
                    link_elem = result.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    # Extract snippet
                    snippet_elem = result.find('div', class_='VwiC3b')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if 'twitter.com' in url and (title or snippet):
                        tweets.append({
                            'username': 'Twitter',
                            'content': f"{title}\n{snippet}",
                            'date': datetime.now().isoformat(),
                            'keyword': keyword,
                            'url': url
                        })
                
                except Exception as e:
                    continue
        
    except Exception as e:
        print(f"Google search error for '{keyword}': {e}")
    
    return tweets

def scrape_twitter_multi_source(keyword):
    """Combine multiple sources with deduplication"""
    all_tweets = []
    
    print(f"🔍 Scraping Twitter for: {keyword}")
    
    # 1. Twitter Syndication API (primary)
    print("  → Trying Twitter Syndication API...")
    tweets_api = scrape_twitter_syndication(keyword)
    all_tweets.extend(tweets_api)
    print(f"    Found {len(tweets_api)} tweets")
    
    # 2. Nitter instances (fallback)
    if len(all_tweets) < 5:
        print("  → Trying Nitter instances...")
        tweets_nitter = scrape_twitter_nitter(keyword)
        all_tweets.extend(tweets_nitter)
        print(f"    Found {len(tweets_nitter)} tweets")
    
    # 3. Google search (supplement)
    if len(all_tweets) < 3:
        print("  → Trying Google search...")
        tweets_google = scrape_twitter_google(keyword)
        all_tweets.extend(tweets_google)
        print(f"    Found {len(tweets_google)} tweets")
    
    # Deduplication by content
    seen = set()
    unique_tweets = []
    
    for tweet in all_tweets:
        content_hash = tweet['content'][:100]  # First 100 chars
        if content_hash not in seen:
            seen.add(content_hash)
            unique_tweets.append(tweet)
    
    print(f"  ✓ Total unique tweets: {len(unique_tweets)}")
    
    return unique_tweets

def generate_ai_summary(tweets):
    """Génère un résumé IA en français via Claude"""
    
    # Check for Anthropic API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY not found - skipping AI summary")
        return {
            'summary': 'Résumé IA non disponible (clé API manquante)',
            'key_points': [],
            'trends': []
        }
    
    # Prepare context
    tweets_text = "\n\n".join([
        f"@{tweet['username']}: {tweet['content']}"
        for tweet in tweets[:20]  # Max 20 tweets for context
    ])
    
    if not tweets_text.strip():
        return {
            'summary': 'Aucun tweet trouvé pour générer un résumé.',
            'key_points': [],
            'trends': []
        }
    
    prompt = f"""Analyse ces tweets sur OpenClaw et Claude Code, et génère un résumé en français.

Tweets récents:
{tweets_text}

Fournis un résumé structuré en français avec:
1. Un résumé général (2-3 phrases)
2. 3-5 points clés
3. 2-4 tendances identifiées

Format JSON attendu:
{{
  "summary": "résumé général...",
  "key_points": ["point 1", "point 2", "point 3"],
  "trends": ["tendance 1", "tendance 2"]
}}
"""
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 1024,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['content'][0]['text']
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                summary_data = json.loads(json_match.group())
                print("✓ AI summary generated")
                return summary_data
            else:
                # Fallback: use raw text
                return {
                    'summary': content,
                    'key_points': [],
                    'trends': []
                }
        else:
            print(f"⚠️ Anthropic API error: {response.status_code}")
            return {
                'summary': f'Erreur API Anthropic (code {response.status_code})',
                'key_points': [],
                'trends': []
            }
    
    except Exception as e:
        print(f"⚠️ AI summary generation failed: {e}")
        return {
            'summary': f'Erreur lors de la génération du résumé: {str(e)}',
            'key_points': [],
            'trends': []
        }

def main():
    print("=" * 60)
    print("🔍 VEILLE TWITTER ONLY - OPENCLAW & CLAUDE CODE")
    print("=" * 60)
    
    all_tweets = []
    
    # Scrape Twitter for each keyword
    for keyword in KEYWORDS:
        tweets = scrape_twitter_multi_source(keyword)
        all_tweets.extend(tweets)
        time.sleep(2)  # Rate limiting
    
    # Deduplication finale
    seen = set()
    unique_tweets = []
    
    for tweet in all_tweets:
        content_hash = tweet['content'][:100]
        if content_hash not in seen:
            seen.add(content_hash)
            unique_tweets.append(tweet)
    
    print(f"\n📊 Total unique tweets: {len(unique_tweets)}")
    
    # Generate AI summary
    print("\n🤖 Generating AI summary in French...")
    summary = generate_ai_summary(unique_tweets)
    
    # Prepare final data
    result = {
        'date': datetime.now().isoformat(),
        'twitter': unique_tweets,
        'summary': summary,
        'stats': {
            'total_tweets': len(unique_tweets),
            'keywords': len(KEYWORDS)
        }
    }
    
    # Save to file
    output_file = 'veille-latest.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Data saved to {output_file}")
    
    # Also save daily archive
    daily_file = f"veille-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Daily archive: {daily_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 RÉSUMÉ")
    print("=" * 60)
    print(f"Tweets trouvés: {len(unique_tweets)}")
    print(f"Résumé IA: {summary.get('summary', 'N/A')[:100]}...")
    print("=" * 60)

if __name__ == "__main__":
    main()
