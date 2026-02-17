import streamlit as st
from run_scheduler import run_scheduler

st.title("SmartScheduler")

if st.button("Générer l'emploi du temps"):
    with st.spinner("Résolution en cours..."):
        schedule = run_scheduler()

    if schedule:
        st.success("Planning généré")
        st.table(schedule)
    else:
        st.error("Aucune solution trouvée")
