#imports
import sys

# 1. Atualizar o Diagrama Sintático e EBNF no GitHub

class Token:
    def __init__(self, type:str, value):
        self.type = type
        self.value = value

# 2. Implementar as melhorias conforme o DS atualizado
        
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

            if self.current_char == '*':
                self.advance()
                return Token('MULT', '*')

            if self.current_char == '/':
                self.advance()
                return Token('DIV', '/')
            
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
        #chama parseterm para todos
        result_parse = 0
        result_term = 0
        token = None
        result_parse, token = Parser.parseTerm() #1
        while(True):
            if token.type == 'EOF':
                return result_parse
            elif token.type in ["MINUS", "PLUS"]: #+
                if token.type == "MINUS":
                    result_term, token = Parser.parseTerm() #chama 
                    if type(result_term) == int:
                        result_parse -= result_term
                    else:
                        raise SyntaxError("Erro: Expressão inválida (esperava um número após -)")
                else: 
                    result_term, token = Parser.parseTerm() #2, EOF
                    if type(result_term) == int:
                        result_parse += result_term #1+
                    else:
                        raise SyntaxError("Erro: Expressão inválida (esperava um número após +)")
            else:
                raise SyntaxError("Erro: Expressão inválida")
            

    @staticmethod  # vai ter o parseterm
    def parseTerm():# renomear para parseterm e criar um novo Term # divisão é // (inteira)
        token = Parser.tokenizer.selectNext()
        result = token.value
        if token.type in ['INT']:
            token = Parser.tokenizer.selectNext()
            while token.type in ['MULT', 'DIV']:
                if token.type == 'MULT':
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'INT':
                        result *= token.value
                    else:
                        raise SyntaxError("Erro: Esperado número após '*'")
                elif token.type == 'DIV':
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'INT':
                        result //= token.value
                    else:
                        raise SyntaxError("Erro: Esperado número após '/'")
                token = Parser.tokenizer.selectNext()
            return (result, token)
        elif token.type in ["EOF", "PLUS", "MINUS"]:
            return (result, token)
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
    if len(sys.argv) < 2:
        sys.exit(1)
    expression = ' '.join(sys.argv[1:])
    result = Parser.run(expression)
    print(result)


if __name__ == "__main__":
    main()