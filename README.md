# 🔍 Veille OpenClaw & Claude Code

Dashboard de veille quotidienne automatique sur OpenClaw et Claude Code.

## 🎯 Fonctionnalités

- ✅ Scraping Twitter (via Nitter)
- ✅ Scraping Reddit
- ✅ Scraping Hacker News
- ✅ Dashboard web moderne
- ✅ Mise à jour automatique quotidienne
- ✅ Interface 100% français
- ✅ Auto-refresh toutes les 5 min

---

## 🚀 Installation (5 min)

### 1. Installer les dépendances

```bash
cd /Users/darksan/.openclaw/workspaces/boss/veille-openclaw
pip3 install -r requirements.txt
```

### 2. Premier scraping (test)

```bash
python3 scraper-twitter.py
```

**Résultat :** Fichier `veille-latest.json` créé

### 3. Ouvrir le dashboard

**Méthode A : Fichier local**
```bash
open dashboard.html
```

**Méthode B : Serveur local**
```bash
python3 -m http.server 8080
```

Puis ouvre : `http://localhost:8080/dashboard.html`

---

## ⚙️ Automation quotidienne

### Option 1 : Cron manuel

**Éditer crontab :**
```bash
crontab -e
```

**Ajouter cette ligne (tous les jours à 9h) :**
```
0 9 * * * cd /Users/darksan/.openclaw/workspaces/boss/veille-openclaw && python3 scraper-twitter.py >> scraper.log 2>&1
```

### Option 2 : Via OpenClaw (recommandé)

**Dis-moi sur Telegram :**
```
Active la veille OpenClaw quotidienne à 9h
```

Je vais créer un cron job qui lance le scraping tous les jours.

---

## 📊 Résultat

**Le dashboard affiche :**
- 🐦 **Tweets** sur OpenClaw & Claude Code
- 🔴 **Posts Reddit** (r/AI, r/ChatGPT, etc.)
- 🟠 **Discussions Hacker News**

**Statistiques :**
- Nombre de tweets/posts trouvés
- Dernière mise à jour
- Filtrage par keyword

---

## 🔧 Configuration

**Modifier les mots-clés (dans `scraper-twitter.py`) :**

```python
KEYWORDS = [
    "openclaw",
    "claude code",
    "@anthropic claude code",
    "OpenClaw AI"
]
```

**Ajouter d'autres keywords :**
- "anthropic agents"
- "claude desktop"
- "AI automation"
- etc.

---

## 📁 Fichiers créés

- `scraper-twitter.py` - Script de scraping
- `dashboard.html` - Interface web
- `veille-latest.json` - Derniers résultats
- `veille-YYYY-MM-DD.json` - Historique quotidien

---

## 🎨 Personnalisation

**Changer les couleurs du dashboard :**

Édite `dashboard.html`, lignes 15-16 :
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Remplace par tes couleurs préférées !

---

## 📱 Accès mobile

**Pour accéder depuis ton téléphone :**

1. Lance le serveur local :
```bash
python3 -m http.server 8080
```

2. Trouve l'IP du Mac mini :
```bash
ipconfig getifaddr en0
```

3. Sur iPhone, va sur :
```
http://192.168.1.173:8080/dashboard.html
```

---

## 🔄 Commandes utiles

**Scraping manuel :**
```bash
python3 scraper-twitter.py
```

**Voir les logs :**
```bash
tail -f scraper.log
```

**Effacer l'historique :**
```bash
rm veille-*.json
```

**Relancer le scraping toutes les heures (test) :**
```bash
while true; do python3 scraper-twitter.py; sleep 3600; done
```

---

## ✅ Checklist

- [ ] Dépendances installées (`pip3 install -r requirements.txt`)
- [ ] Premier scraping réussi (`veille-latest.json` existe)
- [ ] Dashboard accessible (localhost ou IP)
- [ ] Cron quotidien activé (ou OpenClaw job)
- [ ] Keywords configurés selon tes besoins

---

## 🎯 Prochaines améliorations possibles

- [ ] Intégration GitHub (issues, discussions, releases)
- [ ] Discord (serveur OpenClaw officiel)
- [ ] YouTube (vidéos tutoriels)
- [ ] Newsletter (compilation hebdo)
- [ ] Notifications Telegram (nouveaux tweets importants)
- [ ] Analyse sentiment (positif/négatif)
- [ ] Détection tendances (topics qui montent)

**Dis-moi si tu veux que j'ajoute une de ces features !**

---

**Créé le :** 2026-02-28
**Par :** Boss Agent 👑
