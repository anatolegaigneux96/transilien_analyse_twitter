import streamlit as st

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

# Lire le contenu du fichier final_summary.txt
with open("final_summary.txt", "r", encoding="cp1252") as file:
    content = file.read()

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
