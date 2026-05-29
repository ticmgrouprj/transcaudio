# Transc-Carac Pro 🎙️📝

Um sistema robusto e moderno construído em Python e Streamlit para transcrição automatizada de áudio (usando Whisper da OpenAI) e separação de vozes/locutores (Diarização com Pyannote), além de fornecer ferramentas avançadas para contagem e análise de caracteres.

## 🚀 Como Executar o Sistema

Como o sistema utiliza Inteligência Artificial pesada, ele roda dentro de um ambiente virtual (`venv`) isolado para garantir que todas as dependências funcionem corretamente.

Siga este passo a passo sempre que for ligar o sistema:

### Passo 1: Abrir o Terminal
Abra o aplicativo **Terminal** do seu computador (Fedora/Linux) ou o terminal integrado do VS Code.

### Passo 2: Acessar a Pasta do Projeto
Navegue até a pasta onde o projeto está salvo:
```bash
cd /home/foragido/Documentos/CM/transcaudio/transc-carac
```

### Passo 3: Ativar o Ambiente Virtual
Ative o ambiente virtual que contém o Whisper, PyTorch e todas as bibliotecas necessárias:
```bash
source venv/bin/activate
```
*(Você verá que o nome do seu terminal mudará, ganhando um `(venv)` no começo da linha).*

### Passo 4: Rodar o Aplicativo
Execute o Streamlit:
```bash
streamlit run app.py
```
O servidor será iniciado. **Não feche esta janela do terminal!** Ele manterá o aplicativo no ar.

### Passo 5: Acessar no Navegador
Geralmente, o sistema abrirá sozinho. Caso contrário, acesse no seu navegador:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🛠️ Como Usar o Sistema

A interface foi desenhada para ser limpa e direta.

### 1. Transcrição Básica (Apenas Texto)
1. Certifique-se de que o **Idioma** está correto na barra lateral (ex: `pt` para português).
2. Na tela principal, faça o upload do seu áudio (suporta MP4, MP3, WAV, etc).
3. Clique em **Iniciar Transcrição Agora**.

### 2. Transcrição Avançada (Com Separação de Vozes)
Se você tem um áudio com múltiplas pessoas conversando (ex: uma entrevista ou audiência) e quer separar quem disse o quê (Locutor 1, Locutor 2):
1. Na barra lateral, abra o menu **⚙️ Configurações Avançadas**.
2. No campo **HuggingFace Token**, cole o seu código de acesso pessoal gerado no site Hugging Face (ex: `hf_kpW...`).
3. (Opcional) Informe a quantidade exata de locutores ou deixe `0` para o sistema adivinhar.
4. Faça o upload do áudio e clique em iniciar. A saída será formatada automaticamente agrupando as falas.

### 3. Resultados e Exportação
Ao fim do processo, o texto gerado aparecerá na tela. Você pode copiá-lo livremente ou usar os botões abaixo do texto para fazer o download oficial em:
- **Word (.docx)**
- **PDF (.pdf)**
- **Texto Puro (.txt)**

### 4. Contagem de Caracteres
Na segunda aba superior (**📊 Contagem de Caracteres**), você pode colar qualquer texto ou subir um arquivo de texto para que o sistema conte automaticamente o número de caracteres (com e sem espaços) e de palavras totais. Ideal para conferir limites de redações e documentos.

---

## ⚠️ Dica Importante (Git / GitHub)
**Nunca envie a pasta `venv` para o GitHub!** Ela pesa mais de 1 GB. O repositório já está configurado com um arquivo `.gitignore` que impede isso. Se for publicar o código, certifique-se de que está enviando apenas os arquivos de código (como `app.py`, `transcriber.py`, `requirements.txt`).
