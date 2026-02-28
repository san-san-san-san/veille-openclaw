# 🔐 Configuration GitHub Secrets (pour résumés IA)

## 🎯 Pourquoi ?

Le scraper utilise **Claude** pour générer des résumés intelligents.  
Il a besoin de ta **clé API Anthropic** pour fonctionner.

---

## 🔑 ÉTAPE 1 : Récupérer ta clé API

**Tu as déjà une clé API Anthropic (OpenClaw l'utilise).**

### **Méthode A : Depuis le fichier OpenClaw**

```bash
cat ~/.openclaw/credentials/anthropic-default.json
```

**Copie la valeur de** `"apiKey"` ou `"key"`

**Exemple :**
```json
{
  "apiKey": "sk-ant-api03-xxxxx..."
}
```

→ **Copie :** `sk-ant-api03-xxxxx...`

### **Méthode B : Depuis Anthropic Console**

1. Va sur https://console.anthropic.com/settings/keys
2. Copie une clé existante  
   OU  
3. **Create Key** (nouveau)

---

## 🔒 ÉTAPE 2 : Ajouter le secret sur GitHub

**Sur ton repo GitHub :**

1. **Settings** (onglet)
2. **Secrets and variables** → **Actions** (menu gauche)
3. **New repository secret** (bouton)

**Remplir :**
- **Name :** `ANTHROPIC_API_KEY`
- **Secret :** Colle ta clé API (ex: `sk-ant-api03-xxx...`)

**Add secret**

✅ **Secret configuré !**

---

## ✅ VÉRIFICATION

**Le workflow GitHub Actions va maintenant :**

1. Scraper Twitter/Reddit/HN
2. Envoyer les données à Claude
3. Générer un résumé intelligent
4. Sauvegarder avec résumé dans `veille-latest.json`
5. Dashboard affiche la section "Résumé & Insights"

---

## 🧪 TEST

**Teste le workflow :**

1. GitHub → **Actions**
2. **Veille Quotidienne OpenClaw**
3. **Run workflow**

**Attendre 2-3 min**

**Vérifier :**
- ✅ Workflow réussi
- ✅ Fichier `veille-latest.json` mis à jour
- ✅ Section `"summary"` présente dans le JSON
- ✅ Dashboard affiche "Résumé & Insights"

---

## 🆓 COÛT

**Claude Sonnet 3.5 :**
- ~0.01$ par résumé
- 1 résumé/jour = **~0.30$/mois**
- 🎁 Anthropic offre 5$ de crédit gratuit

**Tu peux faire ~500 résumés gratuits !**

---

## ⚠️ Si pas de clé API

**Sans clé API Anthropic :**
- ✅ Scraping fonctionne
- ✅ Dashboard affiche tweets/reddit/HN
- ❌ Pas de section "Résumé & Insights"

**Le scraper affichera :**
```
⚠️  Pas de clé API Anthropic - résumé désactivé
```

**Résumé dans JSON :**
```json
{
  "summary": "Configuration API requise pour générer des résumés.",
  "key_points": [],
  "trends": []
}
```

---

## 🔧 En local

**Pour tester en local (Mac mini) :**

```bash
export ANTHROPIC_API_KEY="ta-clé-ici"
python3 scraper-twitter-v3.py
```

**Ou OpenClaw le détecte automatiquement** depuis `~/.openclaw/credentials/anthropic-default.json`

---

✅ **C'EST TOUT !**

Une fois le secret GitHub configuré, les résumés IA seront générés automatiquement tous les jours ! 🤖
