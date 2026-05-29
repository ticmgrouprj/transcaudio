import streamlit as st
import tempfile
import os
import re
from transcriber import transcrever_audio
from exporter import gerar_docx, gerar_pdf, gerar_txt

st.set_page_config(page_title="transc-carac", page_icon="📝", layout="wide")

st.title("📝 transc-carac")
st.markdown("---")

tabs = st.tabs(["🎙️ Transcrição de Áudio", "📊 Contagem de Caracteres"])

# BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Configurações")
    modelo_whisper = st.selectbox("Qualidade/Modelo", ["tiny", "base", "small", "medium", "large"], index=3, help="Maior = mais lento, porém mais preciso")
    idioma = st.text_input("Idioma (ex: pt, en)", value="pt")
    
    st.markdown("---")
    st.markdown("**Diarização (Separação de Vozes)**")
    hf_token = st.text_input("HuggingFace Token", type="password", help="Necessário para separar Locutor 1, 2. Crie uma conta no HuggingFace, aceite os termos do pyannote e gere um access token.")
    num_locutores = st.number_input("Número de Locutores (0 = auto)", min_value=0, value=0, step=1)

# TABA 1: TRANSCRIÇÃO
with tabs[0]:
    st.header("Upload e Transcrição")
    
    uploaded_audio = st.file_uploader("Faça upload do arquivo de áudio (MP3, WAV, MP4)", type=['mp3', 'wav', 'mp4', 'm4a', 'ogg'])
    
    if uploaded_audio:
        st.audio(uploaded_audio)
        
        # Se um novo arquivo for anexado e for diferente do anterior, limpa a transcrição antiga para não confundir
        if 'ultimo_arquivo' not in st.session_state or st.session_state['ultimo_arquivo'] != uploaded_audio.name:
            st.session_state['ultimo_arquivo'] = uploaded_audio.name
            if 'transcricao' in st.session_state:
                del st.session_state['transcricao']
                
    if st.button("Iniciar Transcrição", type="primary", use_container_width=True):
        if not uploaded_audio:
            st.error("Por favor, faça o upload de um arquivo de áudio.")
        else:
            with st.spinner("Processando o áudio..."):
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
                    st.success("Transcrição finalizada com sucesso!")
                except Exception as e:
                    st.error(f"Erro durante a transcrição: {e}")
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                        
    # Exibir resultados e botões de exportação
    if 'transcricao' in st.session_state:
        st.subheader("Resultado da Transcrição:")
        texto_t = st.session_state['transcricao']
        st.text_area("Texto transcrito:", value=texto_t, height=300)
        
        qtd_com_espaco = len(texto_t)
        qtd_sem_espaco = len(texto_t.replace(" ", "").replace("\n", "").replace("\t", ""))
        palavras = len(re.findall(r'\b\w+\b', texto_t))
        
        st.info(f"📊 **Estatísticas da Transcrição:** {qtd_com_espaco} caracteres (com espaços) | {qtd_sem_espaco} caracteres (sem espaços) | {palavras} palavras")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            docx_buffer = gerar_docx(st.session_state['transcricao'])
            st.download_button("📄 Baixar em Word (.docx)", data=docx_buffer, file_name="transcricao.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with c2:
            pdf_buffer = gerar_pdf(st.session_state['transcricao'])
            st.download_button("📕 Baixar em PDF", data=pdf_buffer, file_name="transcricao.pdf", mime="application/pdf", use_container_width=True)
        with c3:
            txt_buffer = gerar_txt(st.session_state['transcricao'])
            st.download_button("📝 Baixar em TXT", data=txt_buffer, file_name="transcricao.txt", mime="text/plain", use_container_width=True)

# TABA 2: CONTAGEM DE CARACTERES
with tabs[1]:
    st.header("Contagem de Caracteres e Palavras")
    
    texto_para_contar = ""
    
    col_input1, col_input2 = st.columns([1, 1])
    with col_input1:
        texto_digitado = st.text_area("Cole ou digite seu texto aqui:", height=200)
    with col_input2:
        st.markdown("**OU**")
        arquivo_texto = st.file_uploader("Faça upload de um arquivo de texto (.txt)", type=['txt'])
    
    if arquivo_texto:
        texto_para_contar = arquivo_texto.getvalue().decode("utf-8")
    elif texto_digitado:
        texto_para_contar = texto_digitado
        
    if texto_para_contar:
        qtd_com_espaco = len(texto_para_contar)
        qtd_sem_espaco = len(texto_para_contar.replace(" ", "").replace("\n", "").replace("\t", ""))
        palavras = len(re.findall(r'\b\w+\b', texto_para_contar))
        
        st.markdown("### Resultados")
        r1, r2, r3 = st.columns(3)
        r1.metric("Caracteres (com espaços)", qtd_com_espaco)
        r2.metric("Caracteres (sem espaços)", qtd_sem_espaco)
        r3.metric("Palavras", palavras)
