import os
import uuid
from colorama import Fore
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
# 🟢 Importamos a versão centralizada para evitar inconsistências
from tools import (
    pensar, analisar_visao, transcrever_audio, 
    criar_word, criar_excel, criar_pptx, capturar_tela,
    gerar_imagem, formatar_log, obter_stats_sistema,
    purgar_memoria, sintetizar_voz, VERSION  
)
from config import TELEGRAM_TOKEN

# --- GESTÃO DE IDENTIDADE ---
ID_CRIADOR = 8768547953 
USUARIOS_CONHECIDOS = {
    ID_CRIADOR: "Søren",
    7857654896: "Gab",
    7851501820: "Japa"
}

def escapar_html(texto):
    """Sanitiza strings para evitar erros de renderização no Telegram HTML."""
    if texto is None: return "..."
    return str(texto).replace("<", "&lt;").replace(">", "&gt;")

# --- COMANDOS DE HARDWARE & IA ---

async def cmd_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera captura de tela local - Restrito ao Criador."""
    if update.message.from_user.id != ID_CRIADOR:
        await update.message.reply_text("<code>[ ACESSO NEGADO ]</code>", parse_mode=constants.ParseMode.HTML)
        return
    
    await update.message.reply_text("<code>[ ACESSANDO MATRIZ DE VÍDEO... ]</code>", parse_mode=constants.ParseMode.HTML)
    caminho = capturar_tela() # 🟢 Aciona o pyautogui via tools.py
    if caminho:
        with open(caminho, 'rb') as foto:
            await update.message.reply_photo(photo=foto, caption="Captura realizada, Senhor.")
        os.remove(caminho)

async def cmd_criar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Renderiza imagens baseadas em texto (IA Generativa)."""
    if not update.message or not update.message.from_user: return

    id_user = update.message.from_user.id
    if id_user not in USUARIOS_CONHECIDOS:
        await update.message.reply_text("<code>[ ACESSO NEGADO ]</code>", parse_mode="HTML")
        return

    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Søren, preciso de um prompt para renderizar.")
        return

    aviso = await update.message.reply_text("<code>[ RENDERIZANDO... ]</code>", parse_mode="HTML")
    resultado = gerar_imagem(prompt) # 🟢 Chama o motor de renderização

    if resultado == "timeout":
        await aviso.edit_text("⚠️ A Matriz demorou demais para responder (Timeout).")
    elif resultado and os.path.exists(resultado):
        with open(resultado, 'rb') as foto:
            await update.message.reply_photo(photo=foto, caption=f"Matriz Concluída.\nPrompt: {prompt}")
        await aviso.delete()
        os.remove(resultado)
    else:
        await aviso.edit_text("❌ Falha crítica na renderização.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitoramento de Hardware em tempo real."""
    stats = obter_stats_sistema() # 🟢 Busca CPU e RAM via psutil
    msg = (f"🖥️ <b>DIAGNÓSTICO {VERSION}</b>\n\n"
           f"CPU: {stats['cpu']}%\nRAM: {stats['ram']}%\n"
           f"📡 <b>Status:</b> Operacional")
    await update.message.reply_text(msg, parse_mode=constants.ParseMode.HTML)

# --- COMANDOS OFFICE ---

async def cmd_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera documentos .docx sob demanda."""
    if update.message.from_user.id != ID_CRIADOR: return
    conteudo = " ".join(context.args) if context.args else "Relatório Overseer"
    caminho = criar_word(conteudo)
    with open(caminho, 'rb') as f:
        await update.message.reply_document(document=f)
    os.remove(caminho)

# --- GERENCIADORES DE MÍDIA ---

async def gerenciar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Núcleo de conversa e resposta por voz em sequência."""
    if not update.message or not update.message.from_user: return
    id_user = update.message.from_user.id
    nome = USUARIOS_CONHECIDOS.get(id_user, f"Desconhecido ({id_user})")
    
    try:
        # 🟢 1. O cérebro Llama-3.3 processa a resposta
        resposta = pensar(update.message.text, nome_visitante=nome, eh_criador=(id_user == ID_CRIADOR))
        
        # 🟢 2. Envia a resposta em texto formatada em HTML
        await update.message.reply_text(
            formatar_log(escapar_html(resposta)), 
            parse_mode=constants.ParseMode.HTML
        )

        # 🟢 3. Upgrade v5.3: Gera áudio automático da resposta
        caminho_audio = sintetizar_voz(resposta)
        if caminho_audio:
            with open(caminho_audio, 'rb') as audio:
                await update.message.reply_voice(voice=audio)
            os.remove(caminho_audio) # Limpeza de cache imediata

    except Exception as e:
        print(f"{Fore.RED}[ ERRO NO ENVIO ] {e}")
        await update.message.reply_text("⚠️ Ocorreu um erro no meu núcleo cognitivo.")

async def gerenciar_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Módulo Vision: IA analisa o que está vendo na imagem."""
    id_user = update.message.from_user.id
    await update.message.reply_text("<code>[ ANALISANDO FOTO... ]</code>", parse_mode=constants.ParseMode.HTML)
    foto = await update.message.photo[-1].get_file()
    caminho = f"img_{uuid.uuid4()}.jpg"
    await foto.download_to_drive(caminho)
    # 🟢 Envia para o modelo Llama-Vision no tools.py
    resposta = analisar_visao(caminho, pergunta=update.message.caption or "O que vê?", eh_criador=(id_user == ID_CRIADOR))
    os.remove(caminho)
    await update.message.reply_text(formatar_log(escapar_html(resposta)), parse_mode=constants.ParseMode.HTML)

async def gerenciar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Módulo STT: Transcreve voz e responde."""
    id_user = update.message.from_user.id
    await update.message.reply_text("<code>[ PROCESSANDO VOZ... ]</code>", parse_mode=constants.ParseMode.HTML)
    voz = await update.message.voice.get_file()
    caminho = f"voz_{uuid.uuid4()}.ogg"
    await voz.download_to_drive(caminho)
    # 🟢 Transcrição via Whisper API
    texto = transcrever_audio(caminho)
    os.remove(caminho)
    if texto:
        nome = USUARIOS_CONHECIDOS.get(id_user, "Visitante")
        resposta = pensar(texto, nome_visitante=nome, eh_criador=(id_user == ID_CRIADOR))
        await update.message.reply_text(formatar_log(escapar_html(resposta)), parse_mode=constants.ParseMode.HTML)

# --- BOOT DO SISTEMA ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # 🟢 Registro de Comandos e Handlers
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(f"{VERSION} Online e pronta, Senhor.")))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("print", cmd_screenshot))
    app.add_handler(CommandHandler("word", cmd_word))
    app.add_handler(CommandHandler("criar", cmd_criar))
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), gerenciar_texto))
    app.add_handler(MessageHandler(filters.PHOTO, gerenciar_foto))
    app.add_handler(MessageHandler(filters.VOICE, gerenciar_audio))

    # 🟢 Mensagem de Log Final corrigida para v5.3
    print(f"[ OK ] {VERSION} Online.")
    app.run_polling()