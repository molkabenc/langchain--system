# app.py - Version finale sans erreur
import streamlit as st
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Analyseur de Phrases IA",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Analyseur de Phrases avec IA")
st.markdown("Analysez vos phrases pour obtenir : **Sentiment**, **Sujet principal** et **Question de suivi**")

# Vérification des imports
try:
    from langchain_groq import ChatGroq
    st.sidebar.success("✅ ChatGroq importé")
except ImportError:
    st.error("❌ langchain-groq non installé")
    st.code("pip install langchain-groq")
    st.stop()

# Solution simple : créer notre propre chaîne
class SimpleChain:
    """Chaîne simple pour exécuter des prompts"""
    def __init__(self, llm, prompt_template):
        self.llm = llm
        self.prompt_template = prompt_template
    
    def run(self, text):
        # Remplacer le placeholder {text} dans le template
        prompt = self.prompt_template.replace("{text}", text)
        # Appeler le modèle
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)

# Configuration API
st.sidebar.header("⚙️ Configuration API")

api_key = st.sidebar.text_input(
    "🔑 Clé API Groq",
    type="password",
    help="Obtenez une clé gratuite sur https://console.groq.com"
)

if not api_key:
    # Mode démo
    st.info("""
    ## 🎯 Bienvenue !
    
    1. **Obtenez une clé API gratuite** sur [console.groq.com](https://console.groq.com)
    2. **Collez-la** dans le champ à gauche
    3. **Analysez** vos phrases !
    
    ### Exemples à tester :
    """)
    
    examples = [
        ("😊 Positif", "Je suis très satisfait de cette collaboration fructueuse."),
        ("😔 Négatif", "La qualité du service laisse vraiment à désirer."),
        ("😐 Neutre", "La réunion est prévue pour demain à 10h.")
    ]
    
    for emoji, example in examples:
        if st.button(f"{emoji} {example[:30]}...", key=f"ex_{emoji}"):
            st.session_state.demo_text = example
            st.rerun()
    
    if 'demo_text' in st.session_state:
        st.write(f"**Exemple chargé :** {st.session_state.demo_text}")
    
    st.stop()

# Initialiser le modèle
try:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=300,
        groq_api_key=api_key,
        timeout=30
    )
    st.sidebar.success("✅ Modèle Groq initialisé")
except Exception as e:
    st.error(f"❌ Erreur : {str(e)}")
    st.stop()

# Template du prompt
PROMPT_TEMPLATE = """
Analyse cette phrase : "{text}"

Réponds UNIQUEMENT en JSON avec ce format exact :

{
  "sentiment": "POSITIF" ou "NÉGATIF" ou "NEUTRE",
  "sujet_principal": "1-3 mots maximum",
  "question_suivi": "une question pertinente pour approfondir",
  "explication": "explication courte de l'analyse"
}

Exemple de réponse :
{
  "sentiment": "POSITIF",
  "sujet_principal": "Collaboration",
  "question_suivi": "Quels sont les bénéfices attendus de cette collaboration ?",
  "explication": "La phrase exprime de la satisfaction et un sentiment positif concernant une collaboration."
}

Maintenant, analyse cette phrase :
"""

# Initialiser notre chaîne simple
chain = SimpleChain(llm, PROMPT_TEMPLATE)

# Interface principale
st.header("📝 Analyse de phrase")

# Zone de texte
text = st.text_area(
    "Entrez votre phrase :",
    height=100,
    placeholder="Exemple : 'L'intelligence artificielle transforme positivement notre façon de travailler.'",
    key="input_text"
)

# Boutons
col1, col2 = st.columns([1, 3])
with col1:
    analyze_btn = st.button("🚀 Analyser", type="primary", use_container_width=True)

if analyze_btn and text.strip():
    with st.spinner("🧠 Analyse en cours..."):
        try:
            # Appeler notre chaîne
            response = chain.run(text)
            
            # Nettoyer la réponse
            response = response.strip()
            
            # Extraire le JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                result = json.loads(json_str)
                
                # Afficher les résultats
                st.success("✅ Analyse terminée !")
                
                # Métriques
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    sentiment = result.get("sentiment", "NEUTRE")
                    if sentiment == "POSITIF":
                        st.markdown("### 😊 POSITIF")
                        st.success("Sentiment positif détecté")
                    elif sentiment == "NÉGATIF":
                        st.markdown("### 😔 NÉGATIF")
                        st.error("Sentiment négatif détecté")
                    else:
                        st.markdown("### 😐 NEUTRE")
                        st.info("Sentiment neutre détecté")
                
                with col2:
                    st.markdown("### 📌 Sujet")
                    st.write(f"**{result.get('sujet_principal', 'N/A')}**")
                
                with col3:
                    st.markdown("### ❓ Question")
                    st.write(result.get('question_suivi', 'N/A'))
                
                # Détails
                with st.expander("📋 Détails de l'analyse"):
                    st.write(f"**Phrase analysée :**")
                    st.info(f'"{text}"')
                    
                    st.write(f"**Explication :**")
                    st.success(result.get('explication', 'N/A'))
                    
                    # Code JSON brut
                    st.write(f"**Réponse JSON :**")
                    st.code(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Animation
                st.balloons()
                
            else:
                st.error("❌ Format de réponse invalide")
                st.code(f"Réponse brute : {response}")
                
        except json.JSONDecodeError:
            st.error("❌ Erreur de décodage JSON")
            st.code(f"Réponse : {response}")
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

elif analyze_btn and not text.strip():
    st.warning("⚠️ Veuillez entrer une phrase à analyser")

# Section d'exemples
st.sidebar.header("💡 Exemples rapides")

sample_phrases = [
    "L'innovation technologique accélère le progrès économique.",
    "Le service client nécessite des améliorations significatives.",
    "La conférence débutera à 14h dans l'amphithéâtre principal."
]

for phrase in sample_phrases:
    if st.sidebar.button(f"📝 {phrase[:40]}...", key=f"sample_{phrase[:10]}"):
        st.session_state.input_text = phrase
        st.rerun()

# Footer
st.markdown("---")
st.caption("""
🔧 **Mini-projet d'analyse de phrases** | Streamlit • Groq API  
🎯 **Objectif :** Sentiment + Sujet + Question de suivi  
🔗 **Documentation :** [LangChain Groq](https://docs.langchain.com/oss/python/integrations/chat/groq)
""")