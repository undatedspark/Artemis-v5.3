import os
import time
import glob
import subprocess
import sys
import datetime
from colorama import Fore, Style, init
# 🟢 Importamos a lógica de monitoramento e limpeza do seu tools.py
from tools import obter_stats_sistema, purgar_memoria, VERSION 

# Inicializa as cores no terminal (necessário para Windows)
init(autoreset=True)

# Define o arquivo de log para auditoria do sistema
LOG_FILE = "artemis_session.log"

def registrar_log(mensagem):
    """Registra eventos importantes para análise posterior (Debug)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def limpar_cache_total():
    """🟢 Varre a pasta do projeto e remove arquivos temporários (fotos, áudios, docs)."""
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
    """🟢 Renderiza a interface visual do terminal (Interface Overseer)."""
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        L = os.get_terminal_size().columns # Ajusta o banner ao tamanho da janela
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
        # 🟢 Painel de Diagnóstico em tempo real
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
    """🟢 Inicializa o script do Telegram e monitora se ele vai 'crashear'."""
    if not os.path.exists("artemis_telegram.py"):
        print(f"{Fore.RED}[ FATAL ] Script artemis_telegram.py não encontrado.")
        return False

    print(f"{Fore.CYAN}[ SYSTEM ] Inicializando {VERSION}...")
    registrar_log("BOOT: Iniciando núcleo.")
    
    # 🟢 Inicia o bot como um sub-processo independente
    processo = subprocess.Popen([sys.executable, "artemis_telegram.py"])
    
    try:
        while processo.poll() is None:
            time.sleep(5) # Delay de checagem otimizado para não pesar na CPU
            
        if processo.returncode == 0:
            print(f"\n{Fore.YELLOW}[ SHUTDOWN ] Sessão encerrada normalmente.")
            return False 
        else:
            # 🟢 Auto-Recovery: se o bot cair, o Overseer o levanta novamente
            print(f"\n{Fore.RED}[ CRASH ] O núcleo colapsou. Reiniciando protocolos...")
            registrar_log(f"CRASH: Saída {processo.returncode}")
            return True 
            
    except KeyboardInterrupt:
        print(f"\n{Fore.MAGENTA}[ SIGNAL ] Encerrando por comando do Criador (Ctrl+C).")
        processo.terminate()
        return False

if __name__ == "__main__":
    reiniciar = True
    while reiniciar:
        exibir_banner()
        
        # 🟢 Protocolo de Limpeza Pré-Boot
        stats = obter_stats_sistema()
        if stats['ram'] > 80:
            print(f"{Fore.MAGENTA}[ AUTO-RECOVERY ] RAM alta detectada. Purgando lixo...")
            purgar_memoria()
            
        limpar_cache_total()
        
        # 🟢 Inicia o loop de execução
        reiniciar = executar_nucleo()
        
        if reiniciar:
            time.sleep(5) # Espera 5 segundos antes de tentar o reboot

    print(f"{Fore.CYAN}Sessão {VERSION} Finalizada.")