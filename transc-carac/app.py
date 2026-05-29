import streamlit as st
import tempfile
import os
import re
from transcriber import transcrever_audio
from exporter import gerar_docx, gerar_pdf, gerar_txt

st.set_page_config(page_title="Transc-Carac Pro", page_icon="📝", layout="wide")

# ==========================================
# 1. ESTILIZAÇÃO GLOBAL (CUSTOM CSS)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* Ocultar menu do Streamlit e rodapé para visual de aplicativo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Arredondar cantos e melhorar visual de containers */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 8px;
    }
    
    /* Melhorar o visual das métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #1f77b4;
    }
    
    /* Espaçamento e títulos das etapas */
    .step-title {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Cabeçalho Principal
st.title("✨ Transc-Carac Pro")
st.markdown("Sistema inteligente para **transcrição de áudio** e **análise de texto**.")
st.markdown("---")

tabs = st.tabs(["🎙️ Transcrição de Áudio", "📊 Contagem de Caracteres"])

# ==========================================
# 2. BARRA LATERAL (SIDEBAR) MAIS LIMPA
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3252/3252972.png", width=100)
    st.header("⚙️ Opções Principais")
    idioma = st.text_input("🌍 Idioma do Áudio (ex: pt, en)", value="pt")
    
    st.markdown("---")
    
    # Escondendo as configurações sensíveis em um expander
    with st.expander("🛠️ Configurações Avançadas"):
        st.markdown("**Diarização (Separação de Vozes)**")
        hf_token = st.text_input("🔑 HuggingFace Token", type="password", help="Cole o token do HuggingFace para separar múltiplos locutores automaticamente.")
        num_locutores = st.number_input("👥 Número de Locutores (0 = auto)", min_value=0, value=0, step=1)
        
        st.markdown("**Qualidade da Transcrição**")
        modelo_whisper = st.selectbox("Qualidade/Modelo", ["tiny", "base", "small", "medium", "large"], index=3, help="Maior qualidade = tempo de processamento mais longo.")

# ==========================================
# 3. ABA 1: TRANSCRIÇÃO PASSO A PASSO
# ==========================================
with tabs[0]:
    
    st.markdown("<div class='step-title'>1️⃣ Passo 1: Selecione o Áudio</div>", unsafe_allow_html=True)
    uploaded_audio = st.file_uploader("Faça upload do arquivo de áudio ou vídeo (MP3, WAV, MP4)", type=['mp3', 'wav', 'mp4', 'm4a', 'ogg'], label_visibility="collapsed")
    
    if uploaded_audio:
        # Layout limpo para o player
        col_player, _ = st.columns([1, 1])
        with col_player:
            st.audio(uploaded_audio)
            
        # Limpar estado se arquivo mudar
        if 'ultimo_arquivo' not in st.session_state or st.session_state['ultimo_arquivo'] != uploaded_audio.name:
            st.session_state['ultimo_arquivo'] = uploaded_audio.name
            if 'transcricao' in st.session_state:
                del st.session_state['transcricao']
                
        st.markdown("<div class='step-title'>2️⃣ Passo 2: Iniciar Transcrição</div>", unsafe_allow_html=True)
        col_btn, _ = st.columns([1, 2])
        with col_btn:
            iniciar = st.button("🚀 Iniciar Transcrição Agora", type="primary", use_container_width=True)
                
        if iniciar:
            with st.spinner("Processando o áudio com Inteligência Artificial..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(percent, msg):
                    progress_bar.progress(percent)
                    status_text.text(msg)
                
                # Salvar temporariamente
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_audio.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_audio.getbuffer())
                    temp_audio_path = tmp_file.name
                
                try:
                    resultado = transcrever_audio(
                        temp_audio_path,
                        modelo=modelo_whisper,
                        idioma=idioma,
                        hf_token=hf_token if hf_token.strip() else None,
                        num_locutores=num_locutores if num_locutores > 0 else None,
                        progress_callback=update_progress
                    )
                    st.session_state['transcricao'] = resultado
                    st.success("✅ Transcrição concluída com sucesso!")
                except Exception as e:
                    st.error(f"Erro durante a transcrição: {e}")
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                        
    # ==========================================
    # 4. RESULTADOS E EXPORTAÇÃO
    # ==========================================
    if 'transcricao' in st.session_state:
        st.markdown("<div class='step-title'>3️⃣ Passo 3: Resultados e Exportação</div>", unsafe_allow_html=True)
        
        texto_t = st.session_state['transcricao']
        st.text_area("Texto gerado:", value=texto_t, height=300, label_visibility="collapsed")
        
        # Estatísticas via st.metric
        qtd_com_espaco = len(texto_t)
        qtd_sem_espaco = len(texto_t.replace(" ", "").replace("\n", "").replace("\t", ""))
        palavras = len(re.findall(r'\b\w+\b', texto_t))
        
        st.markdown("### 📊 Estatísticas da Transcrição")
        m1, m2, m3 = st.columns(3)
        m1.metric("Caracteres (Com Espaços)", f"{qtd_com_espaco:,}".replace(",", "."))
        m2.metric("Caracteres (Sem Espaços)", f"{qtd_sem_espaco:,}".replace(",", "."))
        m3.metric("Total de Palavras", f"{palavras:,}".replace(",", "."))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botões de Exportação Lado a Lado
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            docx_buffer = gerar_docx(texto_t)
            st.download_button("📄 Baixar em Word (.docx)", data=docx_buffer, file_name="transcricao.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, type="secondary")
        with ex2:
            pdf_buffer = gerar_pdf(texto_t)
            st.download_button("📕 Baixar em PDF (.pdf)", data=pdf_buffer, file_name="transcricao.pdf", mime="application/pdf", use_container_width=True, type="secondary")
        with ex3:
            txt_buffer = gerar_txt(texto_t)
            st.download_button("📝 Baixar em Texto (.txt)", data=txt_buffer, file_name="transcricao.txt", mime="text/plain", use_container_width=True, type="primary")

# ==========================================
# 5. ABA 2: CONTAGEM DE CARACTERES
# ==========================================
with tabs[1]:
    st.header("📊 Contagem de Caracteres e Palavras")
    st.markdown("Cole o seu texto abaixo ou faça upload de um arquivo para análise instantânea.")
    
    texto_para_contar = ""
    
    col_input1, col_input2 = st.columns([1.5, 1])
    with col_input1:
        texto_digitado = st.text_area("Área de Texto:", height=250, placeholder="Cole ou digite seu texto aqui...")
    with col_input2:
        st.info("Ou use um arquivo:")
        arquivo_texto = st.file_uploader("Upload de arquivo (.txt)", type=['txt'], label_visibility="collapsed")
    
    if arquivo_texto:
        texto_para_contar = arquivo_texto.getvalue().decode("utf-8")
    elif texto_digitado:
        texto_para_contar = texto_digitado
        
    if texto_para_contar:
        qtd_com_espaco = len(texto_para_contar)
        qtd_sem_espaco = len(texto_para_contar.replace(" ", "").replace("\n", "").replace("\t", ""))
        palavras = len(re.findall(r'\b\w+\b', texto_para_contar))
        
        st.markdown("---")
        st.markdown("### Resultados da Análise")
        r1, r2, r3 = st.columns(3)
        r1.metric("Caracteres (Com Espaços)", f"{qtd_com_espaco:,}".replace(",", "."))
        r2.metric("Caracteres (Sem Espaços)", f"{qtd_sem_espaco:,}".replace(",", "."))
        r3.metric("Total de Palavras", f"{palavras:,}".replace(",", "."))
