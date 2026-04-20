import os
import time
import glob
import subprocess
import sys
import datetime
from colorama import Fore, Style, init

# 🟢 Integração com o seu tools.py
from tools import obter_stats_sistema, purgar_memoria, VERSION, enviar_email

# Inicializa as cores no terminal
init(autoreset=True)

# Configurações de Auditoria
LOG_FILE = "artemis_session.log"

def registrar_log(mensagem):
    """Registra eventos críticos para análise de estabilidade."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def limpar_cache_total():
    """Varre o diretório e remove arquivos temporários para otimizar espaço."""
    extensoes = ['*.png', '*.docx', '*.xlsx', '*.pptx', '*.jpg', '*.ogg', '*.mp3']
    removidos = 0
    for ext in extensoes:
        for arquivo in glob.glob(ext):
            try:
                os.remove(arquivo)
                removidos += 1
            except:
                pass
    if removidos > 0:
        print(f"{Fore.MAGENTA}[ CLEANER ] {removidos} arquivos de cache purgados.")

def exibir_banner():
    """Interface visual Overseer para o terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        L = os.get_terminal_size().columns
    except:
        L = 80

    logo = [
        r"    ___    ____  ______ ______ __  ____________",
        r"   /   |  / __ \/_  __// ____//  |/  //  _/ ___/",
        r"  / /| | / /_/ / / /  / __/  / /|_/ / / / \__ \ ",
        r" / ___ |/ _, _/ / /  / /___ / /  / /_/ / ___/ / ",
        r"/_/  |_/_/ |_| /_/  /_____//_/  /_//___//____/  ",
        f"         CORE INTERFACE - {VERSION}"
    ]

    print("\n")
    for linha in logo:
        print(f"{Fore.CYAN}{linha.center(L)}")
    print(f"{Fore.WHITE}{'BY SØREN'.center(L)}\n")
    
    div = "─" * (L // 2)
    print(f"{Fore.LIGHTBLACK_EX}{div.center(L)}")
    
    try:
        # Diagnóstico de Hardware
        diag = obter_stats_sistema()
        cor_ram = Fore.RED if diag['ram'] > 85 else Fore.YELLOW
        
        cpu_bar = "█" * int(diag['cpu'] / 10) + "░" * (10 - int(diag['cpu'] / 10))
        ram_bar = "█" * int(diag['ram'] / 10) + "░" * (10 - int(diag['ram'] / 10))
        
        print(f"{Fore.GREEN}{'[ CPU LOAD ]':<15} {cpu_bar} {diag['cpu']}%".center(L))
        print(f"{cor_ram}{'[ RAM LOAD ]':<15} {ram_bar} {diag['ram']}%".center(L))
        
        if diag['ram'] > 90:
            print(f"{Fore.RED}{'!!! ALERTA: MEMÓRIA EM NÍVEL CRÍTICO !!!'.center(L)}")
            
    except:
        print(f"{Fore.RED}{'[ ERROR ] Sensores Offline'.center(L)}")
    
    print(f"{Fore.LIGHTBLACK_EX}{div.center(L)}\n")

def executar_nucleo():
    """Gerencia o sub-processo do Telegram e executa o Auto-Recovery."""
    if not os.path.exists("artemis_telegram.py"):
        print(f"{Fore.RED}[ FATAL ] Script artemis_telegram.py não encontrado.")
        return False

    print(f"{Fore.CYAN}[ SYSTEM ] Inicializando bot...")
    registrar_log("BOOT: Iniciando núcleo.")
    
    # Inicia o bot como processo independente
    processo = subprocess.Popen([sys.executable, "artemis_telegram.py"])
    
    try:
        while processo.poll() is None:
            time.sleep(5)
            
        if processo.returncode == 0:
            print(f"\n{Fore.YELLOW}[ SHUTDOWN ] Sessão encerrada normalmente.")
            return False 
        else:
            # 🔴 LOGICA DE CRASH E ALERTA POR E-MAIL
            print(f"\n{Fore.RED}[ CRASH ] O núcleo colapsou. Código: {processo.returncode}")
            registrar_log(f"CRASH: Saída {processo.returncode}")
            
            # Tenta avisar o criador via SMTP
            try:
                enviar_email(
                    destinatario="gabriel.orph@gmail.com",
                    assunto="⚠️ Alerta Crítico: Artemis v5.3 Offline",
                    corpo=f"O processo do Telegram caiu inesperadamente às {datetime.datetime.now()}. Reiniciando..."
                )
            except:
                print(f"{Fore.RED}[ SMTP ] Falha ao enviar alerta de crash.")
                
            return True 
            
    except KeyboardInterrupt:
        print(f"\n{Fore.MAGENTA}[ SIGNAL ] Encerrando por comando do Criador (Ctrl+C).")
        processo.terminate()
        return False

if __name__ == "__main__":
    reiniciar = True
    while reiniciar:
        exibir_banner()
        
        # Limpeza prévia
        stats = obter_stats_sistema()
        if stats['ram'] > 80:
            purgar_memoria()
        limpar_cache_total()
        
        # Inicia o loop e verifica se precisa reiniciar
        reiniciar = executar_nucleo()
        
        if reiniciar:
            print(f"{Fore.CYAN}[ REBOOT ] Aguardando 5 segundos para nova tentativa...")
            time.sleep(5)

    print(f"{Fore.CYAN}Sessão {VERSION} Finalizada.")