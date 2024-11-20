import streamlit as st
import os

# Configurer la page
st.set_page_config(
    page_title="Résumé des Tweets - Voix du Client",
    page_icon="🚆",
    layout="wide",
)

# Ajouter un en-tête avec une icône
st.markdown(
    """
# 🚆 Résumé des Tweets - Voix du Client
""",
    unsafe_allow_html=True,
)

# Ajouter le contexte et l'objectif
with st.expander("Contexte et Objectif"):
    st.markdown(
        """
    ## Contexte
    Transilien souhaite résumer les tweets afin de suivre et d'améliorer l'expérience voyageur pour un projet de **"Voix du Client"**.

    ## Objectif
    L'objectif est de mettre en évidence les détails essentiels des tweets, afin d'un résumé clair, objectif et concis qui aidera Transilien à comprendre les principaux problèmes et points positifs signalés par les voyageurs, afin de pouvoir apporter des améliorations.
    """,
        unsafe_allow_html=True,
    )

# Ajouter l'approche llm, langchain, langgraph, etc. et afficher l'image graph.png'
with st.expander("Approche"):
    st.markdown(
        """
    Nous utilisons un modèle de langage (LLM) pour résumer les tweets. L'approche est basée sur la méthode MapReduce, où les tweets sont d'abord mappés, puis réduits pour obtenir un résumé global.
    """,
        unsafe_allow_html=True,
    )
    st.image("graph.png", use_container_width=False)

# Obtenir la liste des fichiers dans le répertoire "summary_reports"
files = os.listdir("summary_reports")

# Sort files
files.sort()

# Créer un menu déroulant pour sélectionner un fichier
selected_file = st.selectbox("Sélectionnez un fichier à afficher :", files)

try:
    # Lire le contenu du fichier sélectionné
    with open(
        os.path.join("summary_reports", selected_file), "r", encoding="utf-8"
    ) as f:
        content = f.read()
except UnicodeDecodeError:
    # Lire le contenu du fichier sélectionné
    with open(
        os.path.join("summary_reports", selected_file), "r", encoding="latin-1"
    ) as f:
        content = f.read()


# Afficher le contenu avec le formatage approprié
st.divider()
st.markdown(content, unsafe_allow_html=True)

# Ajouter un pied de page
st.markdown(
    """
---
<span style='font-size:12px;'>Application développée pour Transilien - Voix du Client</span>
""",
    unsafe_allow_html=True,
)
