#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Twitter via RSS Feeds (Nitter)
Veille OpenClaw & Claude Code
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

# Load accounts from config file
def load_accounts_config():
    """Load Twitter accounts from twitter-accounts.json"""
    try:
        with open('twitter-accounts.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            accounts = [acc['username'] for acc in config.get('accounts', [])]
            keywords = config.get('keywords', [])
            return accounts, keywords
    except FileNotFoundError:
        print("⚠️ twitter-accounts.json not found, using defaults")
        return ["bcherny", "anthropic"], ["openclaw", "claude", "code", "ai", "llm"]
    except Exception as e:
        print(f"⚠️ Error loading config: {e}, using defaults")
        return ["bcherny", "anthropic"], ["openclaw", "claude", "code", "ai", "llm"]

# Load from config file
TWITTER_ACCOUNTS, KEYWORDS = load_accounts_config()

# Multiple Nitter instances
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.net",
    "https://nitter.privacydev.net",
]

def scrape_twitter_rss(username, nitter_instance, max_tweets=20):
    """Scrape Twitter account via Nitter RSS"""
    tweets = []
    
    try:
        # Nitter RSS URL
        rss_url = f"{nitter_instance}/{username}/rss"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(rss_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  ⚠️ Nitter returned status {response.status_code}")
            return tweets
        
        # Parse RSS XML
        soup = BeautifulSoup(response.text, 'xml')
        
        # Find all items (tweets)
        items = soup.find_all('item')
        
        print(f"  Found {len(items)} tweets in RSS")
        
        for item in items[:max_tweets]:
            try:
                # Extract title (tweet content)
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Extract description (full tweet with media)
                desc_elem = item.find('description')
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                # Extract link
                link_elem = item.find('link')
                link = link_elem.get_text(strip=True) if link_elem else ''
                
                # Extract pub date
                pubdate_elem = item.find('pubDate')
                pubdate = pubdate_elem.get_text(strip=True) if pubdate_elem else datetime.now().isoformat()
                
                # Combine title and description for content
                content = f"{title}\n{description}".strip()
                
                # Clean HTML tags from content
                content = re.sub(r'<[^>]+>', '', content)
                
                if content and len(content) > 10:
                    tweets.append({
                        'username': username,
                        'content': content[:500],  # Limit content length
                        'date': pubdate,
                        'url': link.replace(nitter_instance, 'https://twitter.com'),
                        'source': 'rss'
                    })
            
            except Exception as e:
                print(f"  Error parsing tweet: {e}")
                continue
        
        print(f"  ✓ Extracted {len(tweets)} tweets from @{username}")
        
    except Exception as e:
        print(f"  ❌ RSS fetch error for @{username}: {e}")
    
    return tweets

def scrape_account_multi_instance(username):
    """Try multiple Nitter instances for an account"""
    
    for instance in NITTER_INSTANCES:
        print(f"  → Trying {instance}...")
        tweets = scrape_twitter_rss(username, instance)
        
        if tweets:
            return tweets
        
        time.sleep(1)  # Rate limiting between instances
    
    return []

def generate_ai_summary(tweets):
    """Génère un résumé IA en français via Google Gemini"""
    
    import os
    
    # Check for Google API key (Gemini)
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("⚠️ GOOGLE_API_KEY not found - skipping AI summary")
        return {
            'summary': 'Résumé IA non disponible (clé API manquante)',
            'key_points': [],
            'trends': []
        }
    
    # Prepare context
    tweets_text = "\n\n".join([
        f"@{tweet['username']}: {tweet['content'][:300]}"
        for tweet in tweets[:15]
    ])
    
    if not tweets_text.strip():
        return {
            'summary': 'Aucun tweet trouvé pour générer un résumé.',
            'key_points': [],
            'trends': []
        }
    
    prompt = f"""Analyse ces tweets et génère un résumé en français.

Tweets récents:
{tweets_text}

Fournis un résumé structuré en français avec:
1. Un résumé général (2-3 phrases)
2. 3-5 points clés
3. 2-4 tendances ou sujets principaux

Format JSON strict (ne retourne QUE le JSON):
{{
  "summary": "résumé général...",
  "key_points": ["point 1", "point 2", "point 3"],
  "trends": ["tendance 1", "tendance 2"]
}}
"""
    
    try:
        # Google Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 1024,
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                summary_data = json.loads(json_match.group())
                print("✓ AI summary generated (Gemini)")
                return summary_data
            else:
                return {
                    'summary': content[:500],
                    'key_points': [],
                    'trends': []
                }
        else:
            print(f"⚠️ Gemini API error: {response.status_code}")
            print(f"Response: {response.text}")
            return {
                'summary': f'Erreur API Gemini (code {response.status_code})',
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
    print("🔍 VEILLE TWITTER RSS - COMPTES SPÉCIFIQUES")
    print("=" * 60)
    
    all_tweets = []
    
    # Scrape each Twitter account
    for username in TWITTER_ACCOUNTS:
        print(f"\n📡 Fetching RSS for @{username}...")
        tweets = scrape_account_multi_instance(username)
        all_tweets.extend(tweets)
        time.sleep(2)  # Rate limiting between accounts
    
    # Deduplication by URL
    seen_urls = set()
    unique_tweets = []
    
    for tweet in all_tweets:
        url = tweet.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_tweets.append(tweet)
    
    print(f"\n📊 Total unique tweets: {len(unique_tweets)}")
    
    # Sort by date (most recent first)
    try:
        from dateutil import parser
        unique_tweets.sort(key=lambda t: parser.parse(t.get('date', '')), reverse=True)
        print("✓ Tweets sorted by date (most recent first)")
    except:
        # If dateutil not available, keep original order
        pass
    
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
            'accounts': len(TWITTER_ACCOUNTS)
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
    print(f"Comptes surveillés: {', '.join(['@' + u for u in TWITTER_ACCOUNTS])}")
    print(f"Tweets trouvés: {len(unique_tweets)}")
    
    if unique_tweets:
        print(f"\nDernier tweet:")
        latest = unique_tweets[0]
        print(f"  @{latest['username']}: {latest['content'][:100]}...")
    
    print(f"\nRésumé IA: {summary.get('summary', 'N/A')[:100]}...")
    print("=" * 60)

if __name__ == "__main__":
    main()
