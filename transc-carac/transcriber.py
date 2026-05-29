import whisper
import math
import os
from pydub import AudioSegment
import tempfile
import torch
import streamlit as st

def format_ts(seconds):
    '''Formata tempo em segundos para [hh:mm:ss]'''
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"[{h:02}:{m:02}:{s:02}]"

@st.cache_resource(show_spinner=False)
def load_whisper_model(modelo):
    return whisper.load_model(modelo)

@st.cache_resource(show_spinner=False)
def load_pyannote_pipeline(hf_token):
    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
    return pipeline

def transcrever_audio(audio_path, modelo="medium", idioma="pt", hf_token=None, num_locutores=None, progress_callback=None):
    '''
    Transcreve o áudio. Se hf_token for fornecido, tenta fazer a diarização das vozes.
    progress_callback(percent, status_message)
    '''
    if progress_callback: progress_callback(0.05, "Carregando áudio...")
    
    # Processando áudio
    audio = AudioSegment.from_file(audio_path)
    
    if progress_callback: progress_callback(0.15, "Carregando modelo Whisper (usa cache se já carregado)...")
    model = load_whisper_model(modelo)
    
    if progress_callback: progress_callback(0.30, "Realizando transcrição (isso pode demorar)...")
    
    # Executar transcrição
    result = model.transcribe(audio_path, language=idioma)
    segments = result["segments"]
    
    diarization_result = None
    if hf_token:
        try:
            if progress_callback: progress_callback(0.70, "Realizando separação de vozes (Diarização)...")
            
            # Carregar pipeline usando cache
            pipeline = load_pyannote_pipeline(hf_token)
                
            diarization_params = {}
            if num_locutores and num_locutores > 0:
                diarization_params["num_speakers"] = num_locutores
                
            diarization = pipeline(audio_path, **diarization_params)
            diarization_result = list(diarization.itertracks(yield_label=True))
            
        except Exception as e:
            if progress_callback: progress_callback(0.80, f"Aviso: Falha na diarização: {e}")
            diarization_result = None
            
    if progress_callback: progress_callback(0.90, "Formatando resultados...")
    
    texto_final = ""
    
    if diarization_result:
        # Mesclar whisper segments com pyannote diarization
        current_speaker = None
        current_paragraph = ""
        current_start = None
        
        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()
            
            # Encontrar locutor que mais falou neste segmento
            speaker_counts = {}
            for turn, _, speaker in diarization_result:
                # Intersecção
                overlap_start = max(start, turn.start)
                overlap_end = min(end, turn.end)
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > 0:
                    speaker_counts[speaker] = speaker_counts.get(speaker, 0) + overlap
            
            if speaker_counts:
                best_speaker = max(speaker_counts, key=speaker_counts.get)
            else:
                best_speaker = "Locutor Desconhecido"
                
            if best_speaker != current_speaker:
                if current_speaker is not None:
                    texto_final += f"{format_ts(current_start)} {current_speaker}:\n{current_paragraph.strip()}\n\n"
                current_speaker = best_speaker
                current_paragraph = text + " "
                current_start = start
            else:
                current_paragraph += text + " "
                
        if current_speaker is not None:
            texto_final += f"{format_ts(current_start)} {current_speaker}:\n{current_paragraph.strip()}\n"
            
    else:
        # Apenas whisper (sem separar por locutor, apenas agrupando blocos muito espaçados no tempo, ou gerando 1 paragrafo grande)
        current_paragraph = ""
        current_start = None
        last_end = 0
        
        for seg in segments:
            start = seg["start"]
            text = seg["text"].strip()
            
            if current_start is None:
                current_start = start
                
            # Se houver um silêncio muito grande (>3s), quebra o parágrafo
            if start - last_end > 3.0 and current_paragraph:
                texto_final += f"{format_ts(current_start)}\n{current_paragraph.strip()}\n\n"
                current_paragraph = text + " "
                current_start = start
            else:
                current_paragraph += text + " "
                
            last_end = seg["end"]
            
        if current_paragraph:
            texto_final += f"{format_ts(current_start)}\n{current_paragraph.strip()}\n"
            
    if progress_callback: progress_callback(1.0, "Concluído!")
    return texto_final.strip()
