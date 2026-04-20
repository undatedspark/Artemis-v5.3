import os
import uuid
import gc
import telebot
from colorama import Fore
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN
from tools import *

# 🟢 Importações centralizadas do seu tools.py
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

# --- 1. INSTANCIAÇÃO (Obrigatório vir antes dos handlers) ---
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- 2. DEFINIÇÃO DE COMANDOS (Handlers) ---

@bot.message_handler(commands=['start', 'ajuda'])
def cmd_start(message):
    """Boas-vindas e comandos disponíveis."""
    boas_vindas = (
        f"🛡️ <b>{VERSION} Online</b>\n\n"
        "Comandos disponíveis:\n"
        "/relatorio - Gera e envia relatório técnico para o e-mail do Criador.\n"
        "/stats - Exibe o uso de CPU e RAM em tempo real.\n"
        "Envie uma imagem ou áudio para análise técnica."
    )
    bot.reply_to(message, boas_vindas, parse_mode="HTML")

@bot.message_handler(commands=['relatorio'])
def cmd_enviar_relatorio(message):
    """Gera um documento Word e envia via SMTP usando credenciais do JSON."""
    user_id = str(message.from_user.id)
    
    # Camada de Autorização (Somente o Søren/ID Admin)
    if user_id == "8768547953": 
        bot.reply_to(message, "⚙️ <b>Overseer:</b> Gerando relatório técnico e disparando e-mail...", parse_mode="HTML")
        
        # 1. Gera o arquivo usando a lógica do tools.py
        data_atual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        conteudo = f"Relatório de integridade do sistema gerado em {data_atual}.\nStatus: Operacional."
        caminho_arquivo = criar_word(conteudo)
        
        # 2. Dispara o e-mail (A função enviar_email já busca os dados no usuarios.json)
        sucesso = enviar_email(
            destinatario="gabriel.orph@gmail.com", 
            assunto=f"Status Report | {VERSION}", 
            corpo="Segue em anexo o relatório de integridade gerado pelo sistema.",
            anexo=caminho_arquivo
        )
        
        if sucesso:
            bot.send_message(message.chat.id, "✅ E-mail enviado com sucesso para a caixa de entrada cadastrada.")
        else:
            bot.send_message(message.chat.id, "❌ Falha no protocolo SMTP. Verifique o console do Overseer.")
    else:
        bot.reply_to(message, "⚠️ <b>Acesso Negado:</b> ID de usuário não autorizado para disparos externos.", parse_mode="HTML")

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    """Retorna dados de hardware via Telegram."""
    diag = obter_stats_sistema()
    msg = f"📊 <b>Diagnóstico de Hardware</b>\n\nCPU: {diag['cpu']}%\nRAM: {diag['ram']}%"
    bot.reply_to(message, msg, parse_mode="HTML")

# --- 3. HANDLERS MULTIMIDIA (Visão e Áudio) ---

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Processa imagens enviadas."""
    bot.reply_to(message, "👁️ Analisando imagem...")
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("temp_vision.jpg", "wb") as f:
        f.write(downloaded_file)
    
    analise = analisar_visao("temp_vision.jpg", eh_criador=True)
    bot.reply_to(message, analise)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """Processa áudios (STT)."""
    bot.reply_to(message, "🎤 Transcrevendo áudio...")
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    caminho_audio = "temp_voice.ogg"
    with open(caminho_audio, "wb") as f:
        f.write(downloaded_file)
        
    texto = transcrever_audio(caminho_audio)
    if texto:
        resposta = pensar(texto, eh_criador=True)
        bot.reply_to(message, f"💬 <b>Transcrição:</b> {texto}\n\n🤖 <b>Resposta:</b> {resposta}", parse_mode="HTML")
    else:
        bot.reply_to(message, "❌ Falha ao processar áudio.")

# --- 4. HANDLER DE TEXTO (IA Pensando) ---

@bot.message_handler(func=lambda message: True)
def responder(message):
    """Processa conversas naturais e detecta intenção de e-mail."""
    texto = message.text.lower()
    
    # Atalho por linguagem natural
    if "mande" in texto and "e-mail" in texto:
        cmd_enviar_relatorio(message)
    else:
        resposta = pensar(message.text, eh_criador=(str(message.from_user.id) == "8768547953"))
        bot.reply_to(message, resposta)

# --- 5. INICIALIZAÇÃO ---

if __name__ == "__main__":
    print(f"🚀 {VERSION} Online e aguardando comandos.")
    bot.polling(none_stop=True)

def escapar_html(texto):
    """Sanitiza strings para evitar erros de renderização no Telegram HTML."""
    if texto is None: return "..."
    return str(texto).replace("<", "&lt;").replace(">", "&gt;")

# --- COMANDOS DE SISTEMA & HARDWARE ---

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitoramento de Hardware em tempo real."""
    stats = obter_stats_sistema()
    msg = (f"🖥️ <b>DIAGNÓSTICO {VERSION}</b>\n\n"
           f"CPU: {stats['cpu']}%\nRAM: {stats['ram']}%\n"
           f"📡 <b>Status:</b> Operacional")
    await update.message.reply_text(msg, parse_mode=constants.ParseMode.HTML)

async def cmd_purgar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a limpeza profunda de cache e memória RAM."""
    if update.message.from_user.id != ID_CRIADOR: return
    
    aviso = await update.message.reply_text("<code>[ INICIANDO PURGA DE MEMÓRIA... ]</code>", parse_mode="HTML")
    
    # Aciona o Garbage Collector e limpa arquivos temporários via tools.py
    purgar_memoria()
    
    stats = obter_stats_sistema()
    await aviso.edit_text(f"🧹 <b>MEMÓRIA PURGADA</b>\nRAM Atual: {stats['ram']}%\n<code>[ SISTEMA OTIMIZADO ]</code>", 
                         parse_mode="HTML")

async def cmd_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera captura de tela local - Restrito ao Criador."""
    if update.message.from_user.id != ID_CRIADOR: return
    
    await update.message.reply_text("<code>[ ACESSANDO MATRIZ DE VÍDEO... ]</code>", parse_mode=constants.ParseMode.HTML)
    caminho = capturar_tela() 
    if caminho:
        with open(caminho, 'rb') as foto:
            await update.message.reply_photo(photo=foto, caption="Captura realizada, Senhor.")
        os.remove(caminho)

# --- COMANDOS OFFICE (GERAÇÃO DE ARQUIVOS) ---

async def cmd_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera documentos .docx."""
    if update.message.from_user.id != ID_CRIADOR: return
    conteudo = " ".join(context.args) if context.args else "Relatório Overseer"
    caminho = criar_word(conteudo)
    if caminho:
        with open(caminho, 'rb') as f:
            await update.message.reply_document(document=f)
        os.remove(caminho)

async def cmd_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera planilhas .xlsx."""
    if update.message.from_user.id != ID_CRIADOR: return
    conteudo = " ".join(context.args) if context.args else "Item, Valor\nExemplo, 100"
    caminho = criar_excel(conteudo)
    if caminho:
        with open(caminho, 'rb') as f:
            await update.message.reply_document(document=f, caption="Sua planilha, Senhor.")
        os.remove(caminho)

async def cmd_pptx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera apresentações .pptx."""
    if update.message.from_user.id != ID_CRIADOR: return
    conteudo = " ".join(context.args) if context.args else "Título -- Conteúdo"
    caminho = criar_pptx(conteudo)
    if caminho:
        with open(caminho, 'rb') as f:
            await update.message.reply_document(document=f, caption="Slides prontos.")
        os.remove(caminho)

# --- COMANDOS DE IA GENERATIVA ---

async def cmd_criar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Renderiza imagens baseadas em texto."""
    if not update.message or not update.message.from_user: return
    id_user = update.message.from_user.id
    if id_user not in USUARIOS_CONHECIDOS: return

    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Søren, preciso de um prompt.")
        return

    aviso = await update.message.reply_text("<code>[ RENDERIZANDO... ]</code>", parse_mode="HTML")
    resultado = gerar_imagem(prompt)

    if resultado and os.path.exists(resultado):
        with open(resultado, 'rb') as foto:
            await update.message.reply_photo(photo=foto, caption=f"Matriz Concluída.\nPrompt: {prompt}")
        await aviso.delete()
        os.remove(resultado)
    else:
        await aviso.edit_text("❌ Falha na renderização.")

# --- GERENCIADORES DE MÍDIA (CONVERSA, FOTO, ÁUDIO) ---

async def gerenciar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    id_user = update.message.from_user.id
    nome = USUARIOS_CONHECIDOS.get(id_user, f"User_{id_user}")
    
    try:
        resposta = pensar(update.message.text, nome_visitante=nome, eh_criador=(id_user == ID_CRIADOR))
        await update.message.reply_text(formatar_log(escapar_html(resposta)), parse_mode=constants.ParseMode.HTML)

        # Resposta em áudio automática (v5.3)
        caminho_audio = sintetizar_voz(resposta)
        if caminho_audio:
            with open(caminho_audio, 'rb') as audio:
                await update.message.reply_voice(voice=audio)
            os.remove(caminho_audio)
    except Exception as e:
        print(f"{Fore.RED}[ ERRO ] {e}")

async def gerenciar_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_user = update.message.from_user.id
    await update.message.reply_text("<code>[ ANALISANDO... ]</code>", parse_mode=constants.ParseMode.HTML)
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

    # Registro de Comandos
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(f"{VERSION} Online.")))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("purgar", cmd_purgar))
    app.add_handler(CommandHandler("print", cmd_screenshot))
    app.add_handler(CommandHandler("word", cmd_word))
    app.add_handler(CommandHandler("excel", cmd_excel))
    app.add_handler(CommandHandler("ppt", cmd_pptx))
    app.add_handler(CommandHandler("criar", cmd_criar))
    
    # Handlers de Mensagem
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), gerenciar_texto))
    app.add_handler(MessageHandler(filters.PHOTO, gerenciar_foto))
    app.add_handler(MessageHandler(filters.VOICE, gerenciar_audio))

    print(f"{Fore.CYAN}[ OK ] {VERSION} Operacional.")
    app.run_polling()