import sys
import re

def compilador(string):
    # Análise Léxica:
    #verificar o que pertence à linguagem
    string = str(string)
    operacoes = ['+', '-'] #faz soma e sub
    tokens = ''.join(string.split()) 
    for elemento in tokens:
        if not(elemento.isnumeric()) and not(elemento in operacoes):
            return

    # Análise Sintática:
    #verificar a ordem dos tokens
    if tokens[0] in operacoes or len(tokens) < 3:
        return
    #verifica se depois de um numero tem uma operação
    for i in range(len(tokens)-1):
        if tokens[i] in operacoes:
            if tokens[i+1] in operacoes:
                return
        
    #Análise Semântica: 
    # ????

    pattern = r'[-+]'
    valores = re.split(pattern, tokens)
    resultado = int(valores[0])
    valor_atual = 0
    for elemento in tokens:
        if elemento in operacoes:
            if elemento == '+':
                resultado += int(valores[valor_atual+1])
            else:
                resultado -= int(valores[valor_atual+1])
            valor_atual += 1
    
    print(resultado)
    return 

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        argumento_chamada = sys.argv[1]
        compilador(argumento_chamada)