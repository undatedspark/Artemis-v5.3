# ARTEMIS v5.3 | Overseer Edition 🛡️

Sistema de assistência multimodal e monitoramento de infraestrutura integrado ao Telegram.

## 🚀 Funcionalidades
- **Núcleo Cognitivo:** Processamento de linguagem natural via GPT-OSS (120B).
- **Módulo Visual:** Análise técnica de imagens com Llama-3.2 Vision.
- **Módulo Auditivo:** Transcrição de áudio via Whisper-large-v3.
- **Overseer (Watchdog):** Supervisor de sistema que monitora CPU/RAM e realiza Auto-Recovery em caso de falhas.
- **Integração Office & SMTP:** Geração automática de relatórios (.docx, .xlsx) e envio via protocolo SMTP.

## 🛠️ Tecnologias
- Python 3.x
- Telebot (pyTelegramBotAPI)
- Groq Cloud API (LLM & Vision)
- Smtplib (Protocolo de E-mail)
- Psutil (Monitoramento de Hardware)

## 🏗️ Arquitetura de Persistência
O sistema utiliza arquivos JSON para gestão dinâmica de credenciais e perfis de usuário, permitindo o desacoplamento de dados sensíveis do código-fonte.