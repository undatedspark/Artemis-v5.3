# 🤖 ARTEMIS v5.3 - Overseer Edition
Assistente Multimodal de alto desempenho para Telegram, integrada com modelos de Inteligência Artificial de última geração e um núcleo de monitorização de hardware proprietário.

## 🚀 Tecnologias e Stack Técnica
- **Linguagem:** Python 3.14+
- **Cérebro (LLM):** Groq API - Llama 3.3 (Processamento de linguagem natural).
- **Visão:** Llama-3.2-11b-Vision-Preview (Análise de imagens).
- **Audição (STT):** Whisper-large-v3 (Transcrição de áudio de alta precisão).
- **Voz (TTS):** gTTS (Síntese de voz automática).
- **Imagens:** Pollinations API (IA Generativa para criação de arte).
- **Interface:** Python-Telegram-Bot (Integração assíncrona).

## 📊 Sistema Overseer (Monitorização & Hardware)
A Artemis v5.3 inclui o protocolo **Overseer**, que permite a gestão direta do servidor através do Telegram:
- **Diagnóstico em Tempo Real:** Comando `/status` para monitorizar o uso de CPU e RAM.
- **Gestão de Memória:** Comando `/purgar` que aciona o Garbage Collector do Python e limpa a cache de ficheiros temporários para otimização de performance.
- **Segurança:** Comando `/print` para captura de ecrã remota do servidor (restrito ao administrador).

## 📁 Suíte Office Integrada
Uma das grandes evoluções da versão 5.3 é a capacidade de gerar documentos profissionais sob demanda:
- **Microsoft Word:** Geração de ficheiros `.docx` formatados via comando `/word`.
- **Microsoft Excel:** Criação de planilhas `.xlsx` dinâmicas através do comando `/excel`.
- **Microsoft PowerPoint:** Montagem de apresentações `.pptx` automáticas com o comando `/ppt`.

## 🛠️ Funcionalidades Multimodais
- **Conversa Inteligente:** Respostas contextuais com memória de curto prazo.
- **Análise de Imagem:** Envie uma foto e a Artemis descreverá o que está a ver.
- **Resposta por Voz:** Todas as interações de texto podem ser acompanhadas por uma resposta em áudio automática.
- **Criação de Arte:** Renderização de imagens baseadas em prompts textuais com o comando `/criar`.

## 📦 Instalação e Execução
1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install python-telegram-bot groq gTTS python-docx openpyxl python-pptx psutil colorama