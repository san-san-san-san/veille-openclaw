# 🚀 Lancer le serveur avec bouton scraping

## 🎯 Mode serveur (recommandé)

**Le serveur Flask permet :**
- ✅ Dashboard web accessible
- ✅ Bouton "Lancer Scraping" fonctionnel
- ✅ API pour scraping à la demande
- ✅ Statut en temps réel

---

## 📦 Installation

```bash
cd /Users/darksan/.openclaw/workspaces/boss/veille-openclaw
pip3 install -r requirements.txt
```

---

## 🚀 Lancer le serveur

```bash
python3 server.py
```

**Résultat :**
```
🚀 Serveur lancé sur http://localhost:8080
📊 Dashboard: http://localhost:8080
```

---

## 🌐 Accéder au dashboard

**Sur Mac :**
```
http://localhost:8080
```

**Depuis iPhone (même WiFi) :**
```
http://192.168.1.173:8080
```

---

## 🎮 Utilisation

### **Boutons disponibles :**

**🔄 Rafraîchir**
- Recharge les données depuis `veille-latest.json`
- Instantané

**🚀 Lancer Scraping**
- Déclenche un scraping complet
- Twitter + Reddit + Hacker News
- Durée : 1-2 minutes
- Dashboard se met à jour automatiquement après

---

## 🔧 Statuts possibles

**⏳ Scraping en cours...**
- Le scraping est actif
- Attendre 1-2 min

**✅ Scraping lancé ! Rafraîchir dans 1-2 min.**
- Scraping terminé avec succès
- Dashboard se rafraîchit auto dans 60s

**❌ Erreur**
- Problème pendant le scraping
- Vérifier les logs

---

## 🛑 Arrêter le serveur

**Dans le Terminal où il tourne :**
```
CTRL + C
```

---

## 🔥 Lancer en arrière-plan

**Pour que le serveur tourne H24 :**

```bash
nohup python3 server.py > server.log 2>&1 &
```

**Arrêter :**
```bash
pkill -f server.py
```

**Voir les logs :**
```bash
tail -f server.log
```

---

## 📊 API Endpoints

**GET /**
- Dashboard HTML

**GET /veille-latest.json**
- Dernières données JSON

**POST /api/scrape**
- Déclencher scraping manuel
- Retour : `{status: 'success', message: '...'}`

**GET /api/status**
- Statut scraping actuel
- Retour : `{running: bool, last_run: string, error: string}`

---

## 💡 Mode local (sans serveur)

**Si tu préfères utiliser sans serveur :**

```bash
# Scraping manuel
python3 scraper-twitter-v2.py

# Ouvrir dashboard (fichier local)
open dashboard.html
```

**Dans ce mode :**
- ✅ Dashboard fonctionne
- ✅ Rafraîchir fonctionne
- ❌ Bouton "Lancer Scraping" ne marche pas (normal)

---

## ✅ Checklist

- [ ] Dépendances installées (`pip3 install -r requirements.txt`)
- [ ] Serveur lancé (`python3 server.py`)
- [ ] Dashboard accessible (http://localhost:8080)
- [ ] Bouton "Lancer Scraping" fonctionne
- [ ] Scraping manuel réussi
- [ ] Dashboard se met à jour

---

**Créé le :** 2026-02-28
**Par :** Boss Agent 👑
