# Analyseur de Phrases IA avec LangChain Runnables

Mini-projet d'analyse de phrases utilisant Streamlit, Groq API et les patterns LangChain modernes (Runnables, Parallel Runnables, Output Parsers).

## 🌟 Caractéristiques

- **Analyse de sentiment** : Détecte si une phrase est POSITIVE, NÉGATIVE ou NEUTRE
- **Extraction du sujet principal** : Identifie le sujet principal en 1-3 mots
- **Question de suivi** : Génère une question pertinente pour approfondir
- **Métadonnées** : Calcul automatique via Parallel Runnables (longueur, nombre de mots, ponctuation)

## 🏗️ Architecture (Notebook 24 Pattern)

Le projet utilise les patterns modernes de LangChain :

```python
# Préparation des données
prep_for_template = RunnableLambda(lambda text: {"text": text})

# Chaîne principale avec LCEL
chain = prep_for_template | PROMPT_TEMPLATE | llm | json_parser

# Exécution parallèle
parallel_chain = RunnableParallel(
    main_analysis=chain,
    metadata=RunnableLambda(lambda text: {...})
)
```

### Composants utilisés

- **RunnableLambda** : Transforme des fonctions en composants réutilisables
- **RunnableParallel** : Exécute plusieurs tâches en parallèle
- **ChatPromptTemplate** : Templates de prompts structurés
- **JsonOutputParser** : Parse automatiquement les réponses JSON
- **LCEL (Pipe Operator)** : Chaîne les composants avec `|`

## 🚀 Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/molkabenc/langchain--system.git
cd langchain--system
```

2. Installer les dépendances :
```bash
pip install -r requirements
```

3. Lancer l'application :
```bash
streamlit run app.py
```

## 🔑 Configuration

1. Obtenez une clé API gratuite sur [console.groq.com](https://console.groq.com)
2. Entrez la clé dans le champ de la barre latérale
3. Analysez vos phrases !

## 📝 Exemples

```
"Je suis très satisfait de cette collaboration fructueuse."
→ Sentiment: POSITIF
→ Sujet: Collaboration
→ Question: Quels sont les bénéfices attendus de cette collaboration ?

"Le service client nécessite des améliorations significatives."
→ Sentiment: NÉGATIF
→ Sujet: Service client
→ Question: Quelles améliorations spécifiques sont nécessaires ?

"La réunion est prévue pour demain à 10h."
→ Sentiment: NEUTRE
→ Sujet: Réunion
→ Question: Quel est l'ordre du jour de la réunion ?
```

## 🔧 Technologies

- **Streamlit** : Interface utilisateur
- **LangChain** : Framework pour les applications LLM
- **Groq API** : Modèle LLM (llama-3.1-8b-instant)
- **Python 3.8+** : Langage de programmation

## 📚 Documentation

- Voir [REFACTORING.md](REFACTORING.md) pour les détails de l'implémentation
- [LangChain LCEL](https://python.langchain.com/docs/expression_language/)
- [LangChain Runnables](https://python.langchain.com/docs/expression_language/primitives/runnables)

## 🧪 Tests

Exécuter les tests de structure des chaînes :
```bash
python3 test_chains.py
```

## 📄 Licence

MIT