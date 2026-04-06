import json
import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

# ============ CARREGAR DADOS ============
# Nota: MantivemosManteve-se os nomes dos arquivos originais para compatibilidade, 
# mas a inteligência agora é da/o CRIS.
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')

# ============ MONTAR CONTEXTO ============
contexto_dados = f"""
NOME ORIGINAL NO CADASTRO: {perfil['nome']}
IDADE: {perfil['idade']} anos
DADOS FINANCEIROS ATUAIS: Patrimônio R$ {perfil['patrimonio_total']} | Reserva R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES PARA ANÁLISE DE CONSCIÊNCIA:
{transacoes.to_string(index=False)}

HISTÓRICO DE ORIENTAÇÕES:
{historico.to_string(index=False)}
"""

# ============ SYSTEM PROMPT (O DNA DA/O CRIS) ============
SYSTEM_PROMPT = """Você é CRIS, estrategista de consciência financeira e pessoa conselheira.
Seu tom é empático, pedagógico e respeitoso à diversidade. 
Seu foco é ajudar a sair da crise e gerir o dinheiro do dia a dia.

DIRETRIZES:
1. Respeite o nome e pronomes escolhidos pelo usuário.
2. NUNCA recomende investimentos específicos. Explique conceitos (ex: o que é Selic) para dar autonomia.
3. Se fugirem do tema (finanças do cotidiano), lembre gentilmente seu papel de conselheiro(a/e).
4. Use os dados de transações para dar exemplos REAIS e práticos, sem julgar os gastos.
5. Se não souber algo, admita.
6. Responda de forma sucinta (máximo 3 parágrafos) e sempre pergunte se a explicação foi clara.
"""

# ============ FUNÇÃO DE COMUNICAÇÃO ============
def perguntar_cris(msg, nome_usuario, apresentacao_agente):
    # Colocou-se a preferência de identidade diretamente no contexto do prompt
    identidade_contexto = f"O usuário quer ser chamado de: {nome_usuario}. Você deve se apresentar como: {apresentacao_agente}."
    
    prompt = f"""
    {SYSTEM_PROMPT}
    
    {identidade_contexto}

    CONTEXTO FINANCEIRO:
    {contexto_dados}

    Pergunta do Usuário: {msg}"""

    try:
        r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False})
        return r.json()['response']
    except Exception as e:
        return "Ops, tive um probleminha técnico. Você pode tentar de novo? 🤝"

# ============ INTERFACE STREAMLIT (O FLUXO DE RESPEITO) ============
st.set_page_config(page_title="CRIS - Consciência Financeira", page_icon="🎯")
st.title("🎯 CRIS: Estrategista de Liberdade Financeira")

# Inicialização do estado de identidade
if "identidade_definida" not in st.session_state:
    st.session_state.identidade_definida = False

if not st.session_state.identidade_definida:
    st.subheader("Boas-vindas ao seu espaço de segurança financeira! 🌈")
    st.write("Antes de começarmos, queremos te ouvir:")
    
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Como você gostaria de ser chamado(a/e)?")
    with col2:
        apresentacao = st.selectbox("Como eu devo me apresentar para você?", 
                                   ["A CRIS", "O CRIS", "Elu CRIS"])
    
    if st.button("Começar nossa jornada 🤝"):
        if nome:
            st.session_state.nome_usuario = nome
            st.session_state.apresentacao_agente = apresentacao
            st.session_state.identidade_definida = True
            st.rerun()
        else:
            st.warning("Por favor, me diga como prefere ser chamado(a/e).")

else:
    # Interface de Chat principal
    st.info(f"Logado como: **{st.session_state.nome_usuario}** | Agente: **{st.session_state.apresentacao_agente}**")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if pergunta := st.chat_input("Como posso te ajudar com seu dinheiro hoje?"):
        st.session_state.messages.append({"role": "user", "content": pergunta})
        st.chat_message("user").write(pergunta)
        
        with st.spinner("Analisando com cuidado..."):
            resposta = perguntar_cris(pergunta, st.session_state.nome_usuario, st.session_state.apresentacao_agente)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            st.chat_message("assistant").write(resposta)
