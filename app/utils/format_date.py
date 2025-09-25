def format_date(date_str: str) -> str:
    """recebe uma data no formato yyyy-mm-dd e retorna no formato dd/mm/yyyy"""
    parts = date_str.split("-")
    if len(parts) != 3:
        raise Exception("formato de data inválido")
    ano = parts[0]
    mes = parts[1]
    dia = parts[2]
    return f"{dia}/{mes}/{ano}"