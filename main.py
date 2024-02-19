#imports
import sys

# 1. Colocar o Diagrama Sintático no GitHub

# 2. Criar uma Classe Token com 2 atributos:
# - type: string. tipo do token
# - value: integer. valor do token

class Token:
    def __init__(self, type:str, value):
        self.type = type
        self.value = value

# 3. Criar uma Classe Tokenizer com 3 atributos e 1 método:
# - source: string. código-fonte que será tokenizado
# - position: integer. posição atual que o Tokenizador está separando
# - next: Token. o último token separado
# - selectNext(): lê o próximo token e atualiza o atributo next
        
class Tokenizer:
    def __init__(self, source:str):
        self.source = source
        self.position = 0
        self.current_char = self.source[self.position] if self.position < len(self.source) else None

    def advance(self):
        self.position += 1
        if self.position < len(self.source):
            self.current_char = self.source[self.position]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token('INT', self.integer())

            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')

            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')

            # Se não corresponder a nenhum dos tipos de token conhecidos, levanta um erro
            raise SyntaxError("Caractere inválido encontrado: {}".format(self.current_char))

        return Token('EOF', '')

    def selectNext(self):
        token = self.get_next_token()
        self.next = token
        return token

class Parser:
    def __init__(self, tokenizer:Tokenizer):
        self.tokenizer = tokenizer

    @staticmethod
    def parseExpression():
        token = Parser.tokenizer.selectNext()

        if token.type == 'INT':
            result = token.value
            token = Parser.tokenizer.selectNext()

            while token.type in ['PLUS', 'MINUS']:
                if token.type == 'PLUS':
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'INT':
                        result += token.value
                    else:
                        raise SyntaxError("Erro: Esperado número após '+'")
                elif token.type == 'MINUS':
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'INT':
                        result -= token.value
                    else:
                        raise SyntaxError("Erro: Esperado número após '-'")
                token = Parser.tokenizer.selectNext()

            return result
        else:
            raise SyntaxError("Erro: Expressão inválida")

    @staticmethod
    def run(code):
        Parser.tokenizer = Tokenizer(code)
        result = Parser.parseExpression()
        if Parser.tokenizer.next.type != 'EOF':
            raise SyntaxError("Erro: Tokens inesperados no final da expressão")
        return result

def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    expression = sys.argv[1]
    result = Parser.run(expression)
    print(result)

if __name__ == "__main__":
    main()




         
        

        


            
        

    

    