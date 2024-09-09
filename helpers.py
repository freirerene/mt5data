import os
from datetime import timedelta, date

meses_vencimento = {
    2: 'G', 4: 'J', 6: 'M', 8: 'Q', 10: 'V', 12: 'Z'
}


def listar_dias(data_inicio, data_fim):

    dia_atual = data_inicio

    dias = []
    while dia_atual <= data_fim:
        dias.append(dia_atual)
        dia_atual += timedelta(days=1)

    dias = [dia.strftime('%F') for dia in dias]

    return dias


def find_wednesday(dia):

    dia_15 = dia + timedelta(days=15 - dia.day)

    data_inicio = dia_15 - timedelta(days=14)

    dias = listar_dias(data_inicio, dia_15)

    dias.reverse()

    quarta = None
    for d in dias:
        if d.weekday() == 2:
            quarta = d.day
            break

    return quarta


def codigo_win(dia):

    dia = date.fromisoformat(dia)
    day = dia.day
    month = dia.month
    year = dia.year

    year = str(year)[-2:]

    if month%2 == 0:
        if day >= 15:
            if month == 12:
                code_letter = meses_vencimento[2]
                year = int(year) + 1
            else:
                code_letter = meses_vencimento[month+2]

        else:
            quarta = find_wednesday(dia)

            if day < quarta:
                code_letter = meses_vencimento[month]
            else:
                if month == 12:
                    code_letter = meses_vencimento[2]
                    year = int(year) + 1

                else:
                    code_letter = meses_vencimento[month+2]

        code = f"WIN{code_letter}{year}"
    else:
        code = meses_vencimento[month+1]
        code = f"WIN{code}{year}"

    return code


def make_dir(diretorio):
    path = f"{diretorio}"

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            print(f'Ocorreu um erro ao criar o diretório "{diretorio}": {e}')