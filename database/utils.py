from datetime import datetime

def data_hoje():
    return datetime.today()

def converter_data(data: str):
    return datetime.strptime(data, "%Y-%m-%d")