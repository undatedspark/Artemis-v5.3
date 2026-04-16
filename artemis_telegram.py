import os
import uuid
from colorama import Fore
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tools import (
    pensar, analisar_visao, transcrever_audio, 
    criar_word, criar_excel, criar_pptx, capturar_tela,
    gerar_imagem, formatar_log, obter_stats_sistema,
    purgar_memoria, sintetizar_voz  # <-- Certifique-se que estas duas estão aqui!
)
from config import TELEGRAM_TOKEN

# --- GESTÃO DE IDENTIDADE ---
ID_CRIADOR = 8768547953 
USUARIOS_CONHECIDOS = {
    ID_CRIADOR: "Søren",
    7857654896: "Gab",   # <-- Faltava esta vírgula
    7851501820: "Japa"   # <-- Adicionada a vírgula aqui também por boa prática
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
    caminho = capturar_tela()
    if caminho:
        with open(caminho, 'rb') as foto:
            await update.message.reply_photo(photo=foto, caption="Captura realizada, Senhor.")
        os.remove(caminho)

async def cmd_criar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # SEGURANÇA: Se não houver mensagem (ex: mensagem editada), ignora
    if not update.message or not update.message.from_user:
        return

    id_user = update.message.from_user.id
    if id_user not in USUARIOS_CONHECIDOS:
        await update.message.reply_text("<code>[ ACESSO NEGADO ]</code>", parse_mode="HTML")
        return

    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Søren, preciso de um prompt para renderizar.")
        return

    aviso = await update.message.reply_text("<code>[ RENDERIZANDO... ]</code>", parse_mode="HTML")
    
    # Chama a função do tools.py
    resultado = gerar_imagem(prompt)

    if resultado == "timeout":
        await aviso.edit_text("⚠️ A Matriz demorou demais para responder (Timeout). Tente novamente.")
    elif resultado and os.path.exists(resultado):
        # MUITO IMPORTANTE: Use open() para enviar o arquivo local
        with open(resultado, 'rb') as foto:
            await update.message.reply_photo(
                photo=foto, 
                caption=f"Matriz Concluída.\nPrompt: {prompt}"
            )
        await aviso.delete()
    else:
        await aviso.edit_text("❌ Falha crítica na renderização.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitoramento de Hardware em tempo real."""
    stats = obter_stats_sistema()
    msg = (f"🖥️ <b>DIAGNÓSTICO ARTEMIS v5.3</b>\n\n"
           f"CPU: {stats['cpu']}%\nRAM: {stats['ram']}%\n"
           f"📡 <b>Status:</b> Online")
    await update.message.reply_text(msg, parse_mode=constants.ParseMode.HTML)

# --- COMANDOS OFFICE ---

async def cmd_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ID_CRIADOR: return
    conteudo = " ".join(context.args) if context.args else "Relatório v5.3"
    caminho = criar_word(conteudo)
    with open(caminho, 'rb') as f:
        await update.message.reply_document(document=f)
    os.remove(caminho)

async def cmd_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ID_CRIADOR: return
    conteudo = " ".join(context.args) if context.args else "Coluna1,Coluna2\nDado1,Dado2"
    caminho = criar_excel(conteudo)
    with open(caminho, 'rb') as f:
        await update.message.reply_document(document=f)
    os.remove(caminho)

async def cmd_pptx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ID_CRIADOR: return
    titulo = "Artemis v5.3"
    corpo = " ".join(context.args) if context.args else "Apresentação de Dados."
    caminho = criar_pptx(titulo, corpo)
    with open(caminho, 'rb') as f:
        await update.message.reply_document(document=f)
    os.remove(caminho)

# --- GERENCIADORES DE MÍDIA ---

async def gerenciar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    id_user = update.message.from_user.id
    nome = USUARIOS_CONHECIDOS.get(id_user, f"Desconhecido ({id_user})")
    
    print(f"[ MESSAGE ] Usuário: {nome} | ID: {id_user} enviou: {update.message.text}")
    
    try:
        # 1. IA Pensa na resposta
        resposta = pensar(update.message.text, nome_visitante=nome, eh_criador=(id_user == ID_CRIADOR))
        
        # 2. Envia o Texto Primeiro (Resposta Rápida)
        await update.message.reply_text(
            formatar_log(escapar_html(resposta)), 
            parse_mode=constants.ParseMode.HTML
        )

        # 3. Gera e Envia o Áudio em sequência (Upgrade v5.3)
        # Usamos uma versão curta/limpa do texto para o áudio (sem tags HTML)
        caminho_audio = sintetizar_voz(resposta)
        
        if caminho_audio:
            with open(caminho_audio, 'rb') as audio:
                await update.message.reply_voice(voice=audio)
            
            # Limpeza de cache (ADS: não deixar lixo no servidor)
            if os.path.exists(caminho_audio):
                os.remove(caminho_audio)

    except Exception as e:
        print(f"[ ERRO SEQUÊNCIA ] {e}")
    try:
        # Chama a IA
        resposta = pensar(update.message.text, nome_visitante=nome, eh_criador=(id_user == ID_CRIADOR))
        
        # Tenta enviar
        await update.message.reply_text(
            formatar_log(escapar_html(resposta)), 
            parse_mode=constants.ParseMode.HTML
        )
    except Exception as e:
        # SE DER ERRO, VAI APARECER AQUI NO SEU CMD:
        print(f"{Fore.RED}[ ERRO NO ENVIO ] {e}")
        await update.message.reply_text("⚠️ Ocorreu um erro no meu núcleo cognitivo.")

async def gerenciar_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_user = update.message.from_user.id
    await update.message.reply_text("<code>[ ANALISANDO FOTO... ]</code>", parse_mode=constants.ParseMode.HTML)
    foto = await update.message.photo[-1].get_file()
    caminho = f"img_{uuid.uuid4()}.jpg"
    await foto.download_to_drive(caminho)
    resposta = analisar_visao(caminho, pergunta=update.message.caption or "O que vê?", eh_criador=(id_user == ID_CRIADOR))
    os.remove(caminho)
    await update.message.reply_text(formatar_log(escapar_html(resposta)), parse_mode=constants.ParseMode.HTML)

async def gerenciar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_user = update.message.from_user.id
    await update.message.reply_text("<code>[ PROCESSANDO VOZ... ]</code>", parse_mode=constants.ParseMode.HTML)
    voz = await update.message.voice.get_file()
    caminho = f"voz_{uuid.uuid4()}.ogg"
    await voz.download_to_drive(caminho)
    texto = transcrever_audio(caminho)
    os.remove(caminho)
    if texto:
        nome = USUARIOS_CONHECIDOS.get(id_user, "Visitante")
        resposta = pensar(texto, nome_visitante=nome, eh_criador=(id_user == ID_CRIADOR))
        await update.message.reply_text(formatar_log(escapar_html(resposta)), parse_mode=constants.ParseMode.HTML)

# --- BOOT DO SISTEMA ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registro de Comandos (Slash Commands)
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Artemis v5.2 Online.")))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("print", cmd_screenshot))
    app.add_handler(CommandHandler("word", cmd_word))
    app.add_handler(CommandHandler("excel", cmd_excel))
    app.add_handler(CommandHandler("powerpoint", cmd_pptx))
    app.add_handler(CommandHandler("criar", cmd_criar))
    
    # Listeners de Mídia (Texto, Foto e Áudio)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), gerenciar_texto))
    app.add_handler(MessageHandler(filters.PHOTO, gerenciar_foto))
    app.add_handler(MessageHandler(filters.VOICE, gerenciar_audio))

    print(f"[ OK ] Artemis v5.2 OMNI Online.")
    app.run_polling()