import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Simulador de IMC", layout="centered", initial_sidebar_state="expanded")

def local_css(file_name: str):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

local_css("assets/style.css")

st.title("Simulador de IMC")
st.caption("Ferramenta simples e profissional para calcular seu Índice de Massa Corporal")

with st.sidebar.form(key="inputs"):
    unit = st.selectbox("Unidade", ("Métrico (kg / m)", "Imperial (lb / in)"))
    if unit == "Métrico (kg / m)":
        weight = st.number_input("Peso (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1, format="%.1f")
        height = st.number_input("Altura (m)", min_value=0.5, max_value=2.5, value=1.75, step=0.01, format="%.2f")
    else:
        weight = st.number_input("Peso (lb)", min_value=2.0, max_value=1100.0, value=154.0, step=0.1, format="%.1f")
        height = st.number_input("Altura (in)", min_value=20.0, max_value=100.0, value=69.0, step=0.1, format="%.1f")
    age = st.slider("Idade", 5, 120, 30)
    gender = st.selectbox("Gênero", ("Prefiro não dizer", "Masculino", "Feminino", "Outro"))
    submit = st.form_submit_button("Calcular")

def bmi_category(bmi: float):
    if bmi < 18.5:
        return "Abaixo do peso", "#60a5fa", "Considere aumentar a ingestão calórica e consultar um profissional."
    if bmi < 25:
        return "Peso normal", "#34d399", "Parabéns — mantenha hábitos saudáveis!"
    if bmi < 30:
        return "Sobrepeso", "#f59e0b", "Avalie alimentação e atividade física regulares."
    if bmi < 35:
        return "Obesidade grau I", "#f97316", "Procure acompanhamento médico e nutricional."
    if bmi < 40:
        return "Obesidade grau II", "#ef4444", "Atenção médica recomendada; plano de saúde/controle."
    return "Obesidade grau III", "#b91c1c", "Procure atendimento médico especializado."

def to_metric(weight: float, height: float, unit: str):
    if unit.startswith("Imperial"):
        return weight * 0.45359237, height * 0.0254
    return weight, height

if 'history' not in st.session_state:
    st.session_state['history'] = []

if submit:
    w_kg, h_m = to_metric(weight, height, unit)
    try:
        bmi = w_kg / (h_m ** 2)
    except Exception:
        st.error("Altura inválida — verifique os valores inseridos.")
        bmi = None

    if bmi:
        bmi_rounded = round(bmi, 1)
        label, color, advice = bmi_category(bmi)

        # Result card
        st.markdown(f"<div class='result-card'>",
                    unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.metric(label="Seu IMC", value=f"{bmi_rounded}")
            st.markdown(f"<p class='badge' style='background:{color}'>{label}</p>", unsafe_allow_html=True)
            st.write(advice)
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=bmi_rounded,
                number={'suffix': ""},
                gauge={
                    'axis': {'range': [10, 45]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [10, 18.5], 'color': '#bae6fd'},
                        {'range': [18.5, 25], 'color': '#bbf7d0'},
                        {'range': [25, 30], 'color': '#ffe8a1'},
                        {'range': [30, 35], 'color': '#ffd1b2'},
                        {'range': [35, 45], 'color': '#ffc4c4'}
                    ]
                }
            ))
            fig.update_layout(height=240, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Save history
        record = {
            'idade': age,
            'genero': gender,
            'unidade': unit,
            'peso_input': weight,
            'altura_input': height,
            'peso_kg': round(w_kg,2),
            'altura_m': round(h_m,2),
            'imc': bmi_rounded,
            'categoria': label
        }
        st.session_state['history'].append(record)

st.markdown("---")
st.header("Histórico")
if st.session_state['history']:
    df = pd.DataFrame(st.session_state['history'])
    st.dataframe(df.sort_values(by='imc', ascending=False).reset_index(drop=True))
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar histórico (CSV)", data=csv, file_name="imc_historico.csv", mime='text/csv')
    st.line_chart(df['imc'])
    if st.button("Limpar histórico"):
        st.session_state['history'] = []
        st.experimental_rerun()
else:
    st.info("Nenhum cálculo ainda — preencha os dados na barra lateral e clique em 'Calcular'.")

st.markdown("---")
with st.expander("O que é o IMC?"):
    st.write(
        "O Índice de Massa Corporal (IMC) é uma medida simples que relaciona peso e altura. "
        "Ele é útil como triagem, mas não substitui avaliação clínica."
    )
