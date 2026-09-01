import streamlit as st
import requests

st.set_page_config(page_title="CHEO AI", page_icon="🤖", layout="wide")

API_URL = "https://cheo-backend-api.onrender.com"

st.title("🤖 C.H.E.O. - AI Assistant")
st.caption("Threat Intelligence & Active Job Hunting Engine")

option = st.sidebar.selectbox(
    "Selecciona un Módulo",
    ["Chat General", "Job Hunter (Búsqueda de Empleo)", "Threat Intel (Caza de Amenazas)"]
)

if option == "Chat General":
    st.subheader("💬 Chat con CHEO")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu consulta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CHEO está pensando..."):
                try:
                    res = requests.post(f"{API_URL}/api/chat", json={"message": prompt})
                    reply = res.json().get("response", "Sin respuesta.")
                except Exception as e:
                    reply = f"Error de conexión: {str(e)}"
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

elif option == "Job Hunter (Búsqueda de Empleo)":
    st.subheader("🎯 Módulo Job Hunter")
    
    with st.form("job_form"):
        title = st.text_input("Título de la Oferta")
        company = st.text_input("Empresa")
        url = st.text_input("URL de la Vacante (opcional)")
        desc = st.text_area("Descripción de la Oferta")
        profile = st.text_area("Tu Perfil / Resumen de CV")
        submit = st.form_submit_button("Evaluar Vacante")

    if submit:
        with st.spinner("CHEO evaluando compatibilidad..."):
            payload = {
                "job_title": title,
                "company": company,
                "job_description": desc,
                "candidate_profile": profile,
                "job_url": url
            }
            try:
                res = requests.post(f"{API_URL}/api/jobs/evaluate", json=payload)
                data = res.json().get("data", [{}])[0]
                st.success("Evaluación guardada en la base de datos.")
                st.metric(label="Match Score", value=f"{data.get('match_score', 0)}%")
                st.write("**Resumen del Análisis:**")
                st.write(data.get("summary", ""))
            except Exception as e:
                st.error(f"Error al procesar: {str(e)}")

elif option == "Threat Intel (Caza de Amenazas)":
    st.subheader("🛡️ Módulo Threat Intelligence")
    
    ioc = st.text_input("Ingresa una IP, Dominio o Hash (SHA256/MD5):")
    if st.button("Analizar IOC"):
        if ioc:
            with st.spinner("CHEO analizando el indicador..."):
                try:
                    res = requests.post(f"{API_URL}/api/threats/analyze", json={"ioc_value": ioc})
                    data = res.json().get("data", [{}])[0]
                    st.success("IOC analizado y registrado en Supabase.")
                    st.write(f"**Tipo:** {data.get('ioc_type', '').upper()}")
                    st.write(f"**Veredicto:** {data.get('verdict', '').upper()}")
                    details = data.get("analysis_details", {})
                    st.json(details)
                except Exception as e:
                    st.error(f"Error al analizar: {str(e)}")
