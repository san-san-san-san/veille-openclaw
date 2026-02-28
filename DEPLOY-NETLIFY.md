# 🚀 Déploiement Netlify + GitHub Actions

## 🎯 Architecture

```
GitHub Actions (9h chaque matin)
        ↓
Scraping Twitter/Reddit/HN
        ↓
Commit veille-latest.json vers GitHub
        ↓
Netlify détecte le commit
        ↓
Déploiement automatique du dashboard
```

**Résultat :** Site web mis à jour automatiquement tous les jours à 9h !

---

## 📦 ÉTAPE 1 : Créer un repo GitHub

### **1.1. Créer le repo**

Va sur https://github.com/new

**Remplir :**
- Repository name : `veille-openclaw`
- Description : `Veille quotidienne OpenClaw & Claude Code`
- Public ou Private (au choix)
- ✅ Cocher "Add README"

**Créer le repository**

### **1.2. Cloner et pousser les fichiers**

**Sur ton Mac mini, ouvre Terminal :**

```bash
cd /Users/darksan/.openclaw/workspaces/boss/veille-openclaw

# Initialiser Git
git init
git add .
git commit -m "🎉 Initial commit - Veille OpenClaw"

# Ajouter remote (remplace TON_USERNAME)
git remote add origin https://github.com/TON_USERNAME/veille-openclaw.git

# Push
git branch -M main
git push -u origin main
```

**✅ Fichiers sur GitHub**

---

## 🔧 ÉTAPE 2 : Configurer GitHub Actions

### **2.1. Activer GitHub Actions**

Les fichiers sont déjà créés (`.github/workflows/daily-scrape.yml`)

**Sur GitHub :**
1. Va sur ton repo
2. Onglet **"Actions"**
3. Tu devrais voir le workflow **"Veille Quotidienne OpenClaw"**
4. Active-le si demandé

### **2.2. Donner permissions d'écriture**

**Sur GitHub :**
1. **Settings** (onglet du repo)
2. **Actions** → **General** (menu gauche)
3. Scroll jusqu'à **"Workflow permissions"**
4. Sélectionne **"Read and write permissions"**
5. **Save**

**✅ GitHub Actions peut maintenant commit les résultats**

### **2.3. Test manuel**

**Sur GitHub :**
1. Onglet **Actions**
2. Sélectionne le workflow **"Veille Quotidienne OpenClaw"**
3. **Run workflow** (bouton à droite)
4. **Run workflow** (confirmer)

**Attendre 2-3 min...**

**Résultat attendu :**
- ✅ Workflow terminé avec succès
- ✅ Nouveau commit avec `veille-YYYY-MM-DD.json`

---

## 🌐 ÉTAPE 3 : Déployer sur Netlify

### **3.1. Créer compte Netlify**

Va sur https://app.netlify.com/signup

**Connecte-toi avec GitHub** (recommandé)

### **3.2. Nouveau site depuis GitHub**

**Sur Netlify :**
1. **Add new site** → **Import an existing project**
2. **Deploy with GitHub**
3. Autorise Netlify à accéder à tes repos
4. Sélectionne **veille-openclaw**

### **3.3. Configurer le build**

**Build settings :**
- **Build command** : (laisser vide)
- **Publish directory** : `.` (point)
- **Branch to deploy** : `main`

**Deploy site**

### **3.4. Attendre le déploiement**

Netlify va :
1. Cloner ton repo
2. Déployer `dashboard.html`
3. Te donner une URL

**URL exemple :** `https://veille-openclaw-abc123.netlify.app`

**✅ Site en ligne !**

---

## 🎨 ÉTAPE 4 : Personnaliser l'URL (optionnel)

**Sur Netlify :**
1. **Site settings** → **Domain management**
2. **Options** → **Edit site name**
3. Change en : `veille-openclaw` (ou autre nom dispo)

**Nouvelle URL :** `https://veille-openclaw.netlify.app`

---

## 🔄 ÉTAPE 5 : Tester l'automation complète

### **5.1. Forcer un scraping manuel**

**Sur GitHub :**
1. Actions → Veille Quotidienne OpenClaw
2. **Run workflow**

### **5.2. Attendre le déploiement Netlify**

Netlify détecte automatiquement le nouveau commit et redéploie.

**Attendre 1-2 min**

### **5.3. Vérifier le site**

Va sur ton URL Netlify : `https://veille-openclaw.netlify.app`

**Tu dois voir :**
- ✅ Dashboard avec nouvelles données
- ✅ Stats mises à jour
- ✅ Tweets, Reddit, HN

---

## ⏰ AUTOMATION QUOTIDIENNE

**C'est déjà configuré !**

**Tous les jours à 9h (heure Paris) :**
1. GitHub Actions lance le scraping
2. Collecte tweets, Reddit, HN
3. Commit `veille-latest.json`
4. Netlify redéploie automatiquement
5. **Site mis à jour avec nouvelles données !**

**Tu n'as RIEN à faire, c'est 100% automatique ! 🎉**

---

## 📊 Monitoring

### **Voir les exécutions**

**Sur GitHub :**
- Onglet **Actions**
- Tu vois toutes les exécutions quotidiennes
- Clique sur une pour voir les logs

### **Voir les déploiements Netlify**

**Sur Netlify :**
- Onglet **Deploys**
- Liste de tous les déploiements
- Clique pour voir les logs

---

## 🔧 Modifier l'heure du scraping

**Édite `.github/workflows/daily-scrape.yml` :**

```yaml
schedule:
  - cron: '0 8 * * *'  # 9h Paris = 8h UTC
```

**Changer l'heure :**
- 8h Paris = `0 7 * * *`
- 10h Paris = `0 9 * * *`
- 12h Paris = `0 11 * * *`

**Commit et push** pour appliquer.

---

## 🐛 Dépannage

### **Problème : GitHub Actions échoue**

**Vérifier :**
1. Permissions d'écriture activées (Settings → Actions)
2. Fichier `requirements.txt` présent
3. Logs dans Actions (cliquer sur l'exécution)

### **Problème : Netlify ne déploie pas**

**Vérifier :**
1. Repo bien connecté à Netlify
2. Branch `main` sélectionnée
3. Nouveau commit bien poussé sur GitHub

### **Problème : Dashboard vide**

**Vérifier :**
1. Fichier `veille-latest.json` bien créé
2. Format JSON valide
3. Console navigateur (F12) pour erreurs

---

## ✅ Checklist finale

- [ ] Repo GitHub créé
- [ ] Fichiers poussés sur GitHub
- [ ] GitHub Actions activé avec permissions
- [ ] Test manuel workflow réussi
- [ ] Compte Netlify créé
- [ ] Site déployé depuis GitHub
- [ ] URL personnalisée (optionnel)
- [ ] Test complet : scraping → commit → déploiement
- [ ] Automation quotidienne vérifiée

---

## 🎯 Résultat final

**URL publique :** `https://ton-site.netlify.app`

**Mis à jour automatiquement :**
- Tous les jours à 9h
- Scraping Twitter/Reddit/HN
- Déploiement immédiat
- 100% automatique
- 0€ de coût

**C'EST TOUT ! 🚀**

---

**Créé le :** 2026-02-28
**Par :** Boss Agent 👑
