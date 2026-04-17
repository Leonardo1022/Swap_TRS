import yfinance as yf
import database as db

from datetime import date, datetime, timedelta

#from form import bolsa_moeda_str

if __name__ == "__main__":
    #contrato = db.selecionar_contrato(1)
    #print(contrato["con_mont"])
    valor_dict = dict()
    for i in range(3):
        bolsa_moeda_str = input("Digite a string ")
        acao_valor = float(input("Digite o valor"))
        if bolsa_moeda_str not in valor_dict.keys():
            valor_dict[bolsa_moeda_str] = acao_valor
        else:
            valor_dict[bolsa_moeda_str] += acao_valor
        print(valor_dict)

    for key, valor in valor_dict.items():
        print(f"Key: {key} Valor: {valor:.2f}")
