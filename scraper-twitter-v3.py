#!/usr/bin/env python3
"""
Veille Twitter v3 - Avec résumés IA
Utilise Google Search + Génère des résumés intelligents
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re
import anthropic
import os

# Configuration
KEYWORDS = [
    "openclaw",
    "claude code",
    "anthropic claude",
]

def search_google_twitter(keyword, max_results=15):
    """
    Recherche Twitter via Google (méthode la plus fiable)
    """
    tweets = []
    
    try:
        # Google search "site:twitter.com keyword"
        query = f"site:twitter.com {keyword} -filter:replies"
        google_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num={max_results}&tbs=qdr:w"  # Dernière semaine
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }
        
        response = requests.get(google_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse résultats Google
            results = soup.select('div.g, div[data-sokoban-container]')
            
            for result in results[:max_results]:
                try:
                    # Titre et lien
                    title_elem = result.select_one('h3')
                    link_elem = result.select_one('a')
                    snippet_elem = result.select_one('.VwiC3b, .yXK7lf, .MUxGbd')
                    
                    if link_elem and snippet_elem:
                        url = link_elem.get('href', '')
                        
                        # Vérifier que c'est un tweet
                        if 'twitter.com/' in url and '/status/' in url:
                            # Extraire username
                            username_match = re.search(r'twitter\.com/([^/]+)/', url)
                            username = '@' + username_match.group(1) if username_match else '@unknown'
                            
                            # Contenu
                            content = snippet_elem.get_text(strip=True)
                            
                            # Nettoyer le contenu
                            content = re.sub(r'\s+', ' ', content)
                            
                            tweet = {
                                'username': username,
                                'content': content,
                                'url': url,
                                'date': 'Cette semaine',
                                'keyword': keyword,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'google_twitter'
                            }
                            
                            tweets.append(tweet)
                
                except Exception as e:
                    continue
            
            print(f"✅ Google Twitter: {len(tweets)} tweets pour '{keyword}'")
    
    except Exception as e:
        print(f"❌ Google Twitter échoué pour '{keyword}': {e}")
    
    return tweets

def scrape_reddit(keyword, max_posts=10):
    """Scrape Reddit"""
    posts = []
    
    try:
        search_url = f"https://www.reddit.com/search.json?q={keyword.replace(' ', '%20')}&sort=new&limit={max_posts}&t=week"
        
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
                    'keyword': keyword,
                    'selftext': post_data.get('selftext', '')[:200]  # Preview
                })
            
            print(f"✅ {len(posts)} posts Reddit trouvés pour '{keyword}'")
    
    except Exception as e:
        print(f"❌ Reddit scraping échoué: {e}")
    
    return posts

def scrape_hackernews(keyword, max_items=10):
    """Scrape Hacker News"""
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

def generate_summary(all_data):
    """
    Génère un résumé intelligent avec Claude
    """
    
    try:
        # Préparer le contenu pour analyse
        content_for_analysis = []
        
        # Twitter
        for tweet in all_data['twitter'][:20]:  # Top 20
            content_for_analysis.append(f"Tweet de {tweet['username']}: {tweet['content']}")
        
        # Reddit
        for post in all_data['reddit'][:10]:  # Top 10
            content_for_analysis.append(f"Reddit r/{post['subreddit']}: {post['title']}")
        
        # HN
        for item in all_data['hackernews'][:10]:  # Top 10
            content_for_analysis.append(f"HN: {item['title']}")
        
        if not content_for_analysis:
            return {
                'summary': 'Aucune donnée à analyser.',
                'key_points': [],
                'trends': []
            }
        
        # Préparer le prompt pour Claude
        content_text = "\n".join(content_for_analysis)
        
        # Utiliser l'API Anthropic
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            # Tenter de lire depuis fichier credentials
            try:
                with open('/Users/darksan/.openclaw/credentials/anthropic-default.json', 'r') as f:
                    creds = json.load(f)
                    api_key = creds.get('apiKey') or creds.get('key')
            except:
                pass
        
        if not api_key:
            print("⚠️  Pas de clé API Anthropic - résumé désactivé")
            return {
                'summary': 'Configuration API requise pour générer des résumés.',
                'key_points': [],
                'trends': []
            }
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyse ces posts sur OpenClaw et Claude Code et génère un résumé en français.

Contenu à analyser :
{content_text}

Réponds en JSON avec cette structure :
{{
  "summary": "Résumé général en 2-3 phrases",
  "key_points": ["Point clé 1", "Point clé 2", "Point clé 3"],
  "trends": ["Tendance 1", "Tendance 2"]
}}

Sois concis et pertinent. Focus sur les nouveautés, problèmes et opportunités."""
                }
            ]
        )
        
        # Parser la réponse
        response_text = message.content[0].text
        
        # Extraire JSON (Claude peut wrapper dans ```json```)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            summary_data = json.loads(json_match.group(0))
        else:
            summary_data = json.loads(response_text)
        
        print("✅ Résumé IA généré")
        
        return summary_data
    
    except Exception as e:
        print(f"⚠️  Erreur génération résumé: {e}")
        return {
            'summary': 'Erreur lors de la génération du résumé.',
            'key_points': [],
            'trends': []
        }

def run_daily_scrape():
    """Exécute la veille quotidienne complète"""
    
    print("="*60)
    print("🔍 VEILLE QUOTIDIENNE - OpenClaw & Claude Code v3")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*60)
    
    all_data = {
        'date': datetime.now().isoformat(),
        'twitter': [],
        'reddit': [],
        'hackernews': [],
        'summary': {}
    }
    
    # Twitter (Google Search)
    print("\n🐦 TWITTER (via Google)")
    for keyword in KEYWORDS:
        print(f"\n   Recherche: {keyword}")
        tweets = search_google_twitter(keyword, max_results=10)
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
    
    # Générer résumé IA
    print("\n\n🤖 GÉNÉRATION RÉSUMÉ IA")
    all_data['summary'] = generate_summary(all_data)
    
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
    print(f"🤖 Résumé: {len(all_data['summary'].get('key_points', []))} points clés")
    print(f"💾 Sauvegardé: {filename}")
    print("="*60)

if __name__ == "__main__":
    run_daily_scrape()
