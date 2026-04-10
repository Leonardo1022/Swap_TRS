from datetime import datetime

data_hoje = datetime.today().strftime("%Y-%m-%d")

def converter_data(data: str):
    return datetime.strptime(data, "%Y-%m-%d")