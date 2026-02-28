#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Twitter via Google Search (site:twitter.com)
Veille OpenClaw & Claude Code
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

# Keywords à surveiller
KEYWORDS = [
    "openclaw",
    "claude code anthropic",
    "OpenClaw AI",
]

def scrape_twitter_google(keyword, max_results=20):
    """Scrape Twitter via Google search site:twitter.com"""
    tweets = []
    
    try:
        # Google search: site:twitter.com + keyword
        search_query = f"site:twitter.com {keyword}"
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&num=20"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  ⚠️ Google returned status {response.status_code}")
            return tweets
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search result containers
        results = soup.find_all('div', class_='g')
        
        print(f"  Found {len(results)} Google results")
        
        for result in results[:max_results]:
            try:
                # Extract link
                link_elem = result.find('a')
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
                # Only twitter.com links
                if 'twitter.com' not in url and 'x.com' not in url:
                    continue
                
                # Extract username from URL
                # Format: https://twitter.com/username/status/1234567890
                username_match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status', url)
                username = username_match.group(1) if username_match else 'Unknown'
                
                # Extract title (tweet preview from Google)
                title_elem = result.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Extract snippet (tweet content preview)
                snippet_elem = result.find('div', class_='VwiC3b') or result.find('span', class_='st')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                # Combine title and snippet for content
                content = f"{title}\n{snippet}".strip()
                
                if content and len(content) > 10:  # Filter out empty/too short
                    tweets.append({
                        'username': username,
                        'content': content,
                        'date': datetime.now().isoformat(),
                        'keyword': keyword,
                        'url': url
                    })
            
            except Exception as e:
                print(f"  Error parsing result: {e}")
                continue
        
        print(f"  ✓ Extracted {len(tweets)} tweets")
        
    except Exception as e:
        print(f"  ❌ Google search error for '{keyword}': {e}")
    
    return tweets

def generate_ai_summary(tweets):
    """Génère un résumé IA en français via Claude"""
    
    import os
    
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
        f"@{tweet['username']}: {tweet['content'][:300]}"
        for tweet in tweets[:15]  # Max 15 tweets for context
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

Format JSON strict (ne retourne QUE le JSON, rien d'autre):
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
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                summary_data = json.loads(json_match.group())
                print("✓ AI summary generated")
                return summary_data
            else:
                # Fallback: use raw text
                return {
                    'summary': content[:500],
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
    print("🔍 VEILLE TWITTER via GOOGLE - OPENCLAW & CLAUDE CODE")
    print("=" * 60)
    
    all_tweets = []
    
    # Scrape Twitter for each keyword via Google
    for keyword in KEYWORDS:
        print(f"\n🔍 Scraping Twitter (via Google) for: {keyword}")
        tweets = scrape_twitter_google(keyword)
        all_tweets.extend(tweets)
        time.sleep(3)  # Rate limiting entre keywords
    
    # Deduplication par URL
    seen_urls = set()
    unique_tweets = []
    
    for tweet in all_tweets:
        url = tweet.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
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
    if unique_tweets:
        print(f"\nPremier tweet:")
        print(f"  @{unique_tweets[0]['username']}: {unique_tweets[0]['content'][:100]}...")
    print(f"\nRésumé IA: {summary.get('summary', 'N/A')[:100]}...")
    print("=" * 60)

if __name__ == "__main__":
    main()
