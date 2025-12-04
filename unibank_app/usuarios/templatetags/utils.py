from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Substitui todas as ocorrências de 'arg[0]' em 'value' por 'arg[1]'.
    Uso: {{ string|replace:".","|" }}
    """
    if isinstance(arg, str):
        # Espera uma string separada por vírgula: "busca,substituicao"
        try:
            old, new = arg.split(',', 1)
        except ValueError:
            # Caso o argumento não esteja no formato esperado, retorna o valor original
            return value

        return str(value).replace(old, new)
    
    # Caso o argumento 'arg' não seja uma string, retorna o valor original
    return value