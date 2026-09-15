import paramiko
import posixpath
import stat
from datetime import datetime


HOST = "SEU_HOST"
PORT = 1601
USERNAME = "SEU_USUARIO"
PASSWORD = "SUA_SENHA"

PASTA_REMOTA = "/ftp_CMKVNJ_production/dev/impter/zebra/expedicao"


def log(mensagem):
    horario = datetime.now().strftime("%H:%M:%S")
    print(f"[{horario}] {mensagem}", flush=True)


def conectar_sftp():

    log("Criando conexão via SSH...")

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    log("Conectando ao servidor...")

    ssh.connect(
       hostname="suntechsupplies170773.protheus.cloudtotvs.com.br",
        port=1901,
        username="ftp_CMKVNJ_production",
        password="4CXE8PQr",
        timeout=10



    )

    log("Conexão SSH realizada.")

    log("Abrindo conexão SFTP...")

    sftp = ssh.open_sftp()

    log("SFTP conectado com sucesso.")

    return ssh, sftp


def apagar_arquivos(sftp):

    log(f"Acessando pasta: {PASTA_REMOTA}")

    encontrados = 0
    apagados = 0
    preservados = 0
    pastas_ignoradas = 0
    erros = 0

    log("Lendo conteúdo da pasta...")

    itens = sftp.listdir_attr(PASTA_REMOTA)

    log(f"Total de itens encontrados: {len(itens)}")

    log("Iniciando limpeza...")

    for item in itens:

        nome = item.filename

        # ==========================================
        # IGNORA PASTAS
        # ==========================================

        if stat.S_ISDIR(item.st_mode):

            pastas_ignoradas += 1

            log(f"[PASTA IGNORADA] {nome}")

            continue

        # ==========================================
        # PROCESSA SOMENTE ARQUIVOS
        # ==========================================

        if stat.S_ISREG(item.st_mode):

            encontrados += 1

            # ======================================
            # PRESERVA ARQUIVOS .SEQ
            # ======================================

            if nome.lower().endswith((".seq")):

                preservados += 1

                log(f"[PRESERVADO] {nome}")

                continue

            # ======================================
            # APAGA TODOS OS DEMAIS ARQUIVOS
            # ======================================

            caminho = posixpath.join(
                PASTA_REMOTA,
                nome
            )

            log(f"Apagando arquivo: {nome}")

            try:

                sftp.remove(caminho)

                apagados += 1

                log(f"OK - {nome} apagado.")

            except Exception as erro:

                erros += 1

                log(
                    f"ERRO ao apagar {nome}: {erro}"
                )

    log("--------------------------------")
    log("Resumo da execução")
    log(f"Arquivos encontrados: {encontrados}")
    log(f"Arquivos apagados: {apagados}")
    log(f"Arquivos END/SEQ preservados: {preservados}")
    log(f"Pastas ignoradas: {pastas_ignoradas}")
    log(f"Erros: {erros}")
    log("--------------------------------")


def main():

    ssh = None
    sftp = None

    log("==============================")
    log("INICIANDO LIMPEZA DO SPOOL")
    log("==============================")

    try:

        ssh, sftp = conectar_sftp()

        apagar_arquivos(sftp)

    except paramiko.AuthenticationException:

        log("ERRO: usuário ou senha incorretos.")

    except FileNotFoundError:

        log("ERRO: pasta remota não encontrada.")

    except Exception as erro:

        log(f"ERRO inesperado: {erro}")

    finally:

        if sftp:

            log("Fechando conexão SFTP...")
            sftp.close()

        if ssh:

            log("Fechando conexão SSH...")
            ssh.close()

        log("==============================")
        log("PROCESSO FINALIZADO")
        log("==============================")


if __name__ == "__main__":
    main()