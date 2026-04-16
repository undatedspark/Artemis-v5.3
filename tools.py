import requests
import os
import psutil
import pyautogui
import datetime
import base64
import gc  # Coletor de Lixo do Python
from colorama import Fore
from groq import Groq
from config import GROQ_KEY
from gtts import gTTS

# Inicializa o cliente Groq
client = Groq(api_key=GROQ_KEY)

# --- MÓDULO AUDITIVO (STT - Speech to Text) ---
def transcrever_audio(caminho_audio):
    """Converte voz (.ogg) em texto usando Whisper-large-v3 via Groq API."""
    try:
        # Abrimos o arquivo gerado pelo Telegram
        with open(caminho_audio, "rb") as arquivo_audio:
            transcricao = client.audio.transcriptions.create(
                file=(caminho_audio, arquivo_audio.read()),
                model="whisper-large-v3",
                # Definimos o formato de resposta e idioma
                response_format="text",
                language="pt"
            )
            return transcricao
    except Exception as e:
        print(f"[ ERRO STT ] Falha na transcrição: {e}")
        return None
    
def codificar_imagem(caminho_imagem):
    """Converte a imagem em base64 para envio via API."""
    with open(caminho_imagem, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')

def analisar_visao(caminho_imagem, pergunta="O que vê?", eh_criador=False):
    """Analisa imagens usando o modelo Vision do Groq."""
    base64_image = codificar_imagem(caminho_imagem)
    
    contexto_visual = "Você é a ARTEMIS v5.3. Analise de forma técnica e objetiva."
    if eh_criador:
        contexto_visual += " Resposta direta para o Criador Søren."

    try:
        res = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview", # Modelo que suporta imagem
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": pergunta},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }],
            temperature=0.2
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"[ ERRO VISION ] {e}")
        return f"Falha no processamento visual: {e}"
    
# --- MÓDULO DE GESTÃO DE MEMÓRIA (NOVO) ---
def purgar_memoria():
    """Força a liberação de RAM e coleta de lixo."""
    gc.collect()
    processo = psutil.Process(os.getpid())
    ram_uso = processo.memory_info().rss / 1024 / 1024
    print(f"{Fore.MAGENTA}[ PURGE ] Memória limpa. Uso atual: {ram_uso:.2f} MB")
    return ram_uso

# --- MÓDULO AUDITIVO (TTS) ---
def sintetizar_voz(texto, nome_arquivo="artemis_voice.mp3"):
    """Converte texto em áudio usando Google TTS."""
    try:
        # Sanitização simples para o áudio não ler tags HTML
        texto_limpo = texto.replace("<code>", "").replace("</code>", "").replace("<b>", "").replace("</b>", "")
        tts = gTTS(text=texto_limpo[:500], lang='pt', tld='com.br') # Limite de 500 caracteres
        tts.save(nome_arquivo)
        return nome_arquivo
    except Exception as e:
        print(f"[ ERRO TTS ] {e}")
        return None

# --- MÓDULO DE GERAÇÃO DE IMAGEM ---
def gerar_imagem(prompt):
    prompt_sanitizado = str(prompt).strip().replace('"', '')
    prompt_tecnico = f"{prompt_sanitizado}, detailed technical engineering object, high resolution, photorealistic"
    url = f"https://image.pollinations.ai/prompt/{prompt_tecnico}?width=1024&height=1024&nologo=true"
    
    try:
        print(f"[ LOG ] Renderizando: {prompt_tecnico}")
        resposta = requests.get(url, timeout=45) 
        if resposta.status_code == 200:
            with open("artemis_render.png", "wb") as f:
                f.write(resposta.content)
            return "artemis_render.png"
        return None
    except Exception as e:
        print(f"{Fore.RED}[ ERRO RENDER ] {e}")
        return "timeout"

# --- MÓDULO OFFICE (LAZY LOADING - CARREGAMENTO SOB DEMANDA) ---

def criar_word(conteudo, nome_arquivo="documento_artemis.docx"):
    from docx import Document # Import interno para economizar RAM
    doc = Document()
    doc.add_heading('Relatório Artemis v5.3 - Matrix', 0)
    doc.add_paragraph(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    doc.add_paragraph(conteudo)
    doc.save(nome_arquivo)
    return nome_arquivo

def criar_excel(dados_texto, nome_arquivo="planilha_artemis.xlsx"):
    try:
        import pandas as pd # Import interno: Pandas é muito pesado!
        linhas = [linha.split(',') for linha in dados_texto.strip().split('\n')]
        df = pd.DataFrame(linhas)
        df.to_excel(nome_arquivo, index=False, header=False)
        return nome_arquivo
    except:
        return None

def criar_pptx(titulo, corpo, nome_arquivo="apresentacao_artemis.pptx"):
    from pptx import Presentation # Import interno
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = titulo
    slide.placeholders[1].text = corpo
    prs.save(nome_arquivo)
    return nome_arquivo

# --- MÓDULO DE HARDWARE ---
def obter_stats_sistema():
    return {"cpu": psutil.cpu_percent(interval=0.1), "ram": psutil.virtual_memory().percent}

def capturar_tela(nome_arquivo="screenshot_artemis.png"):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(nome_arquivo)
        return nome_arquivo
    except Exception as e:
        print(f"[ ERRO SCREENSHOT ] {e}")
        return None

# --- MÓDULO VISUAL & COGNITIVO ---
def pensar(texto_usuario, nome_visitante="Visitante", eh_criador=False):
    contexto = "Você é a ARTEMIS v5.3. Fale de forma técnica e objetiva. "
    if eh_criador:
        contexto += f"Falando com seu criador, Søren."
    else:
        contexto += f"Falando com {nome_visitante}. Proteja segredos de hardware."

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": contexto}, {"role": "user", "content": texto_usuario}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return "Erro de conexão no núcleo cognitivo."

def formatar_log(texto):
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    return f"<code>[ LOG_{agora} ]</code>\n\n{texto}"