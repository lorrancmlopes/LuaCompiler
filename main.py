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
            
            if self.current_char == '(':
                self.advance()
                return Token('LPAR', '(')
            
            if self.current_char == ')':
                self.advance()
                return Token('RPAR', ')')

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
        result_expression, token = Parser.parseTerm() 
        while(token.type in ["MINUS", "PLUS"]):
            if token.type == "MINUS":
                result_term, token = Parser.parseTerm() 
                if type(result_term) == int:
                    result_expression -= result_term
                else:
                    raise SyntaxError("Erro: Expressão inválida (esperava um número após -)")
            else: 
                result_term, token = Parser.parseTerm() 
                if type(result_term) == int:
                    result_expression += result_term 
                else:
                    raise SyntaxError("Erro: Expressão inválida (esperava um número após +)")
        return result_expression
            

    @staticmethod  
    def parseTerm():
        result_term, token = Parser.parseFactor() 
        while(token.type in ["MULT", "DIV"]):
            if token.type == "MULT":
                result_factor, token = Parser.parseFactor() 
                if type(result_factor) == int:
                    result_term *= result_factor
                else:
                    raise SyntaxError("Erro: Expressão inválida (esperava um número após *)")
            else: 
                result_factor, token = Parser.parseFactor() 
                if type(result_factor) == int:
                    result_term //= result_factor 
                else:
                    raise SyntaxError("Erro: Expressão inválida (esperava um número após /)")
        return result_term, token

    # 3. Implementar parseFactor
    @staticmethod
    def parseFactor():
        token = Parser.tokenizer.selectNext()
        if token.type == 'INT':
            return token.value, Parser.tokenizer.selectNext()
        elif token.type == 'LPAR':
            result_expression = Parser.parseExpression()
            if Parser.tokenizer.next.type == 'RPAR':
                return result_expression, Parser.tokenizer.selectNext()
            else:
                raise SyntaxError("Erro: Parênteses não fechados")
        # tratamento de operador unário + e -
        elif token.type == 'MINUS':
            result_factor, token = Parser.parseFactor()
            if type(result_factor) == int:
                return -result_factor, token
            else:
                raise SyntaxError("Erro: Expressão inválida (esperava um número após -)")
        elif token.type == 'PLUS':
            result_factor, token = Parser.parseFactor()
            if type(result_factor) == int:
                return result_factor, token
            else:
                raise SyntaxError("Erro: Expressão inválida (esperava um número após +)")
        else:
            raise SyntaxError("Erro: Token inesperado")

    @staticmethod
    def run(code):
        Parser.tokenizer = Tokenizer(code)
        result = Parser.parseExpression()
        if Parser.tokenizer.next.type != 'EOF':
            print(Parser.tokenizer.next.type)
            print(Parser.tokenizer.next.value)
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