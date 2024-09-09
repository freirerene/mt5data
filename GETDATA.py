import subprocess
from datetime import date
from tqdm import tqdm

from helpers import listar_dias, make_dir, codigo_win


def get_stocks_history(codigo, d_i, d_f):

    make_dir(f'data/{codigo}')

    d_i = date.fromisoformat(d_i)
    d_f = date.fromisoformat(d_f)
    dias = listar_dias(d_i, d_f)

    if codigo == 'win':
        codigos = {dia : codigo_win(dia) for dia in dias}
    else:
        codigos = lambda x: codigo

    for dia in tqdm(dias):

        command = ['wine', 'python', 'WINDOWS/windowsSTOCKS.py', codigos(dia), '-d', dia]

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        except subprocess.CalledProcessError as e:
            print(f"erro: {e.returncode}")
            print(f"Mensagem de erro: {e.stderr}")
            continue