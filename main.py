import os
import time
import glob
import subprocess
import sys
import datetime
from colorama import Fore, Style, init
# Importamos a purga diretamente do seu tools.py otimizado
from tools import obter_stats_sistema, purgar_memoria 

# Inicializa as cores
init(autoreset=True)

VERSION = "5.3 | OVERSEER"
LOG_FILE = "artemis_session.log"

def registrar_log(mensagem):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def limpar_cache_total():
    """Limpa resíduos e arquivos temporários da v5.3."""
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
        f"         CORE INTERFACE - v{VERSION}"
    ]

    print("\n")
    for linha in logo:
        print(f"{Fore.CYAN}{linha.center(L)}")
    print(f"{Fore.WHITE}{'BY SØREN'.center(L)}\n")
    
    div = "─" * (L // 2)
    print(f"{Fore.LIGHTBLACK_EX}{div.center(L)}")
    
    try:
        diag = obter_stats_sistema()
        # Lógica de cores para a RAM (Aviso visual para o Criador)
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
    if not os.path.exists("artemis_telegram.py"):
        print(f"{Fore.RED}[ FATAL ] Script principal não encontrado.")
        return False

    print(f"{Fore.CYAN}[ SYSTEM ] Inicializando Artemis v5.3...")
    registrar_log("BOOT: Iniciando núcleo.")
    
    processo = subprocess.Popen([sys.executable, "artemis_telegram.py"])
    
    try:
        while processo.poll() is None:
            time.sleep(2) # Aumentamos o delay de checagem para poupar CPU
            
        if processo.returncode == 0:
            print(f"\n{Fore.YELLOW}[ SHUTDOWN ] Sessão encerrada normalmente.")
            return False 
        else:
            print(f"\n{Fore.RED}[ CRASH ] O núcleo colapsou. Reiniciando protocolos...")
            registrar_log(f"CRASH: Saída {processo.returncode}")
            return True 
            
    except KeyboardInterrupt:
        print(f"\n{Fore.MAGENTA}[ SIGNAL ] Encerrando por comando do Criador.")
        processo.terminate()
        return False

if __name__ == "__main__":
    reiniciar = True
    while reiniciar:
        exibir_banner()
        
        # PROTOCOLO DE PURGA ANTES DO BOOT
        stats = obter_stats_sistema()
        if stats['ram'] > 80:
            print(f"{Fore.MAGENTA}[ AUTO-RECOVERY ] RAM alta detectada. Purgando lixo de memória...")
            purgar_memoria()
            
        limpar_cache_total()
        reiniciar = executar_nucleo()
        
        if reiniciar:
            time.sleep(5)

    print(f"{Fore.CYAN}Sessão Artemis v5.3 Finalizada.")