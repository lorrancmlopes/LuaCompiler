import sys
import re

# Palavras reservadas
RESERVED_KEYWORDS = ['print']


# 1. Implementar a árvore sintática abstrata (AST)
import re

class PrePro:
    @staticmethod
    def filter(code):
        # Remove comentários e linhas em branco
        code = re.sub(r'\s*--.*', '', code)  # Adicionamos \s* para permitir espaços opcionais antes do comentário
        code = re.sub(r'\n\s*\n', '\n', code)
        # Remove espaços em branco no final de cada linha com rstrip()
        code = '\n'.join([line.rstrip() for line in code.split('\n')])
        return code



class SymbolTable:
    def __init__(self):
        self.symbol_table = {}

    def set(self, identifier, value):
        self.symbol_table[identifier] = value

    def get(self, identifier):
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]
        else:
            raise NameError(f"Variável '{identifier}' não definida na tabela de símbolos.")


class Node:
    def __init__(self, value=None):
        self.value = value
        self.children = []

    def evaluate(self):
        pass


class Block(Node):
    def evaluate(self, symbol_table):
        for child in self.children:
            if child != None:
                child.evaluate(symbol_table)


class Assignment(Node):
    def evaluate(self, symbol_table):
        identifier = self.children[0]
        value_node = self.children[1]  # Acessando o nó de valor

        if isinstance(value_node, IntVal):  # Verificando se o nó de valor é do tipo IntVal
            value = value_node.evaluate()  # Se for, apenas obtemos o valor
        else:
            value = value_node.evaluate(symbol_table)  # Caso contrário, avaliamos a expressão

        symbol_table.set(identifier, value)


class BinOp(Node):
    def evaluate(self, symbol_table):
        left = self.children[0]
        right = self.children[1]

        if not isinstance(left, IntVal):
            left = left.evaluate(symbol_table)

        if not isinstance(right, IntVal):
            right = right.evaluate(symbol_table)

        if isinstance(left, IntVal) and isinstance(right, IntVal):
            if self.value == '+':
                return left.value + right.value
            elif self.value == '-':
                return left.value - right.value
            elif self.value == '*':
                return left.value * right.value
            elif self.value == '/':
                return left.value // right.value
            else:
                raise TypeError("Operação não suportada para operandos não inteiros")
        # Se pelo menos uma das partes for um inteiro, tratamos esse caso separadamente
        elif isinstance(left, int) and isinstance(right, IntVal):
            if self.value == '+':
                return left + right.value
            elif self.value == '-':
                return left - right.value
            elif self.value == '*':
                return left * right.value
            elif self.value == '/':
                return left // right.value
        elif isinstance(left, IntVal) and isinstance(right, int):
            if self.value == '+':
                return left.value + right
            elif self.value == '-':
                return left.value - right
            elif self.value == '*':
                return left.value * right
            elif self.value == '/':
                return left.value // right

        elif isinstance(left, int) and isinstance(right, int):
            if self.value == '+':
                return left + right
            elif self.value == '-':
                return left - right
            elif self.value == '*':
                return left * right
            elif self.value == '/':
                return left // right
        else:
            raise TypeError("Operação não suportada para operandos não inteiros")


class UnOp(Node):
    def evaluate(self, symbol_table=None):
        if self.value == '-':
            return -self.children[0].evaluate(symbol_table)
        else:
            # verifica se é um IntVal ou uma expressão
            if isinstance(self.children[0], IntVal):
                return self.children[0].evaluate()
            else:
                return self.children[0].evaluate(symbol_table)



class IntVal(Node):
    def evaluate(self):
        return self.value



class NoOp(Node):
    def evaluate(self):
        pass


class Print(Node):
    def evaluate(self, symbol_table):
        #avalia se children[0] é um IntVal ou uma expressão
        if isinstance(self.children[0], IntVal):
            print(self.children[0].evaluate())
        else:
            print(self.children[0].evaluate(symbol_table))


class Token:
    def __init__(self, type: str, value):
        self.type = type
        self.value = value


class Tokenizer:
    def __init__(self, source: str):
        self.source = PrePro.filter(source)
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

            if self.current_char == '\n':
                self.advance()
                return Token('NEWLINE', '\n')

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

            if self.current_char == '=':
                self.advance()
                return Token('ASSIGN', '=')

            # Verificar o caso de ser um identificador de variável (começa com letra e contém letras e números)
            if self.current_char.isalpha():
                identifier = ''
                while self.current_char.isalnum() or self.current_char == "_":
                    identifier += self.current_char
                    self.advance()

                if identifier in RESERVED_KEYWORDS:
                    # Se for um print, desvia
                    if identifier == 'print':
                        return Token('PRINT', 'print')
                return Token('IDENTIFIER', identifier)

            # Se não corresponder a nenhum dos tipos de token conhecidos, levanta um erro
            raise SyntaxError("Caractere inválido encontrado: {}".format(self.current_char))

        return Token('EOF', '')

    def selectNext(self):
        token = self.get_next_token()
        self.next = token
        return token


class Parser:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
        self.symbol_table = SymbolTable

    @staticmethod
    def parseBlock():  # resolve cada linha, que é um Statement
        token = Parser.tokenizer.selectNext()
        # cria o nó de bloco
        block_node = Block()
        # tabela de símbolos
        Parser.symbol_table = SymbolTable()
        while token.type != 'EOF':
            statement = Parser.parseStatement(token)
            block_node.children.append(statement)
            token = Parser.tokenizer.selectNext()
        # fazer o evaluate do bloco
        block_node.evaluate(Parser.symbol_table)

    @staticmethod
    def parseStatement(token):
        # Se o token for um /n, não faz nada
        if token.type == 'NEWLINE':
            return
        # Se o token for um identificador, cria um nó de atribuição (Assignment)
        elif token.type == 'IDENTIFIER':
            identifier = token.value
            token = Parser.tokenizer.selectNext()
            if token.type == 'ASSIGN':
                expression, next_token = Parser.parseExpression()
                # Verifica se o próximo token é um /n, se não for, levanta um erro
                if next_token.type != 'NEWLINE':
                    raise SyntaxError(f"Erro: Esperado fim de linha, encontrado '{next_token.value}'")
                assignment_node = Assignment()
                assignment_node.value = token.value
                assignment_node.children.append(identifier)
                assignment_node.children.append(expression)
                Parser.symbol_table.set(identifier, expression)
                return assignment_node
            else:
                raise SyntaxError("Erro: Esperado símbolo de atribuição '=' após identificador")
        # Se o token for um print, verifica se tem um (, expressao e um ). Se sim, cria um nó de print
        elif token.type == 'PRINT':
            token = Parser.tokenizer.selectNext()
            if token.type == 'LPAR':
                expression, token = Parser.parseExpression()
                if token.type == 'RPAR':
                    print_node = Print()
                    print_node.value = "print"
                    print_node.children.append(expression)
                    return print_node
                else:
                    raise SyntaxError("Erro: Parênteses não fechados")
            else:
                raise SyntaxError("Erro: Parênteses não abertos")
        else:
            raise SyntaxError("Erro: Token inesperado após declaração")


    @staticmethod
    def parseExpression():
        result_expression, token = Parser.parseTerm()
        while token.type in ["MINUS", "PLUS"]:
            op = token.value
            result_term, token = Parser.parseTerm()
            bin_op_node = BinOp(op)
            bin_op_node.children.append(result_expression)
            bin_op_node.children.append(result_term)
            result_expression = bin_op_node
        return result_expression, token

    @staticmethod
    def parseTerm():
        result_term, token = Parser.parseFactor()
        while token.type in ["MULT", "DIV"]:
            op = token.value
            result_factor, token = Parser.parseFactor()
            bin_op_node = BinOp(op)
            bin_op_node.children.append(result_term)
            bin_op_node.children.append(result_factor)
            result_term = bin_op_node
        return result_term, token

    @staticmethod
    def parseFactor():
        token = Parser.tokenizer.selectNext()
        if token.type == 'INT':
            return IntVal(token.value), Parser.tokenizer.selectNext()
        # Se for um identificador, verifica se está na tabela de símbolos
        elif token.type == 'IDENTIFIER':
            identifier = token.value
            if Parser.symbol_table.get(identifier):
                return Parser.symbol_table.get(identifier), Parser.tokenizer.selectNext()
            else:
                raise NameError(f"Variável '{identifier}' não definida na tabela de símbolos.")
        elif token.type == 'LPAR':
            result_expression, _ = Parser.parseExpression()
            if Parser.tokenizer.next.type == 'RPAR':
                return result_expression, Parser.tokenizer.selectNext()
            else:
                raise SyntaxError("Erro: Parênteses não fechados")
        elif token.type in ['PLUS', 'MINUS']:
            un_op_node = UnOp(token.value)
            result_factor, token = Parser.parseFactor()
            un_op_node.children.append(result_factor)
            return un_op_node, token
        else:
            raise SyntaxError("Erro: Token inesperado")

    @staticmethod
    def run(code):
        Parser.tokenizer = Tokenizer(code)
        Parser.parseBlock()



def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        code = file.read()
#     code = '''x = 3
# print(x)'''
    try:
        Parser.run(code)
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
