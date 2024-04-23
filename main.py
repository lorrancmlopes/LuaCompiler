import sys
import re

# Palavras reservadas
RESERVED_KEYWORDS = ['print', 'if', 'else', 'while', 'then', 'end', 'do', 'or', 'and', 'not', 'read',
                     'local']  # atulizando v2.3 (local)


class PrePro:
    @staticmethod
    def filter(code):
        # Remove comentários e linhas em branco
        code = re.sub(r'\s*--.*', '', code)
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
        # faz um elif para vericar se é um Read, e aí não passa o symbol_table
        elif isinstance(value_node, Read):
            value = value_node.evaluate()
        # vamos ver se é uma string
        elif isinstance(value_node, String):
            value = value_node.evaluate()
        else:
            value = value_node.evaluate(symbol_table)  # Caso contrário, avaliamos a expressão
        symbol_table.set(identifier, value)


class BinOp(Node):
    def evaluate(self, symbol_table):
        left = self.children[0]
        right = self.children[1]
        if not isinstance(left, IntVal) and not isinstance(left, String):
            left = left.evaluate(symbol_table)

        if not isinstance(right, IntVal) and not isinstance(right, String):
            right = right.evaluate(symbol_table)

        # adicionar operador de concatenação
        if self.value == '..':
            #print(f"left: {left} right: {right} ...")
            #print(isinstance(left, IntVal))
            if isinstance(left, IntVal):
                 left = String((str(left.value[0]), 'STRING'))
                 #print(f"left: {left}")
            if isinstance(right, IntVal):
                right = String((str(right.value[0]), 'STRING'))
            #print(f"isinstance(left, tuple): {isinstance(left, tuple)}")
            if isinstance(left, tuple) and isinstance(right, tuple):
                return String((left[0] + right[0], 'STRING'))
            elif isinstance(left, String) and isinstance(right, tuple):
                return String((left.value[0] + right[0], 'STRING'))
            # print(f"left: {left} right: {right}")
            # print(String((left.value[0] + right.value[0], 'STRING')))
            if not isinstance(left, String) or not isinstance(right, String):
                #print(f"-------------------------------------")
                #print(f"left: {left} right.value[0]: {right.value[0]}")
                #print(f"-------------------------------------")
                #print(f"{left[0] + right.value[0]}")
                return String((left[0] + right.value[0], 'STRING'))
            return String((left.value[0] + right.value[0], 'STRING'))

        # Alterando a gambiarra da versão 2.1 ue verificava IntVal e int de cada lado:
        # se right não for IntVal, transforma em IntVal right e left
        # if not isinstance(right, IntVal):
        #     right = IntVal(right.value)
        # if not isinstance(left, IntVal):
        #     left = IntVal(left.value)
        # Operações binárias
        if self.value == '+':
            return IntVal((left.value[0] + right.value[0], 'INT'))
        elif self.value == '-':
            return IntVal((left.value[0] - right.value[0], 'INT'))
        elif self.value == '*':
            return IntVal((left.value[0] * right.value[0], 'INT'))
        elif self.value == '/':
            return IntVal((left.value[0] // right.value[0], 'INT'))
        # adicionar operadores de comparação and, or, ==, <, >:
        elif self.value == 'or':
            if left.value[1] == 'INT' and right.value[1] == 'INT':
                if left.value[0] or right.value[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
            raise TypeError("Operação não suportada para os valores tipos fornecidos")
        elif self.value == 'and':
            if left.value[1] == 'INT' and right.value[1] == 'INT':
                if left.value[0] and right.value[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
            raise TypeError("Operação não suportada para os valores tipos fornecidos")
        elif self.value == '==':
            if (isinstance(left, String) or isinstance(left, IntVal)) and (isinstance(right, String) or isinstance(right, IntVal)):
                if left.value[0] == right.value[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
            elif isinstance(left, tuple) and isinstance(right, tuple):
                if left[0] == right[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
        elif self.value == '<':
            if (isinstance(left, String) or isinstance(left, IntVal)) and (isinstance(right, String) or isinstance(right, IntVal)):
                if left.value[0] < right.value[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
            elif isinstance(left, tuple) and isinstance(right, tuple):
                if left[0] < right[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
        elif self.value == '>':
            if (isinstance(left, String) or isinstance(left, IntVal)) and (isinstance(right, String) or isinstance(right, IntVal)):
                if left.value[0] > right.value[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
            elif isinstance(left, tuple) and isinstance(right, tuple):
                if left[0] > right[0]:
                    return IntVal((1, 'INT'))
                return IntVal((0, 'INT'))
        else:
            raise TypeError("Operação não suportada para os valores fornecidos")


class UnOp(Node):
    def evaluate(self, symbol_table=None):
        if self.value == '-':
            #print(f"Estou no UnOp")
            #print(f"O retorno é: {IntVal((-self.children[0].evaluate(symbol_table).value[0], 'INT'))}")
            return IntVal((-self.children[0].evaluate(symbol_table).value[0], 'INT'))
        # adicionar operador de negação
        elif self.value == 'not':
            bool = not self.children[0].evaluate(symbol_table)
            if bool:
                return IntVal((1, 'INT'))
            return IntVal((0, 'INT'))
        else:
            # verifica se é um IntVal ou uma expressão
            if isinstance(self.children[0], IntVal):
                return self.children[0].evaluate()
            else:
                return self.children[0].evaluate(symbol_table)


class IntVal(Node):
    def evaluate(self):
        return IntVal(self.value)


class Identifier(Node):
    def evaluate(self, symbol_table):
        if symbol_table.get(self.value) is None:
            raise NameError(f"Variável '{self.value}' não definida na tabela de símbolos!")
        return symbol_table.get(self.value)


class Read(Node):
    def evaluate(self):
        return IntVal((int(input()), 'INT'))


class Concat(Node):
    def evaluate(self, symbol_table):
        return String((self.children[0].evaluate(symbol_table) + self.children[1].evaluate(symbol_table), 'STRING'))

# Adicionando Strigs
class String(Node):
    def evaluate(self):
        return self.value


class NoOp(Node):
    def evaluate(self):
        pass


class Print(Node):
    def evaluate(self, symbol_table):
        # avalia se children[0] é um IntVal ou uma expressão
        if isinstance(self.children[0], IntVal) or isinstance(self.children[0], String):
            print(self.children[0].evaluate())
        else:
            #print(f"self.children[0].evaluate(symbol_table): {self.children[0].evaluate(symbol_table).value}")
            print(self.children[0].evaluate(symbol_table).value[0])


class While(Node):
    def evaluate(self, symbol_table):
        #print(self.children[0].children)
        # raise
        while self.children[0].evaluate(symbol_table).value[0]:  # reavalia a condição em cada iteração
            # print(f"ST: {symbol_table.symbol_table}")
            self.children[1].evaluate(symbol_table)
            #print(f"ST: {symbol_table.symbol_table['x_1']}") #debug


class If(Node):
    def evaluate(self, symbol_table):
        expression = self.children[0]  # condição do if
        block = self.children[1]  # bloco de comandos
        # verifica o len do nó, se for 3, tem um else
        if len(self.children) == 3:
            block_else = self.children[2]  # bloco de comandos do else
            if expression.evaluate(symbol_table):
                block.evaluate(symbol_table)
            else:
                block_else.evaluate(symbol_table)
        else:
            if expression.evaluate(symbol_table):
                block.evaluate(symbol_table)


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
        return int(result), 'INT'

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
                if self.current_char == '=':
                    self.advance()
                    return Token('EQUALS', '==')
                else:
                    return Token('ASSIGN', '=')
            # operador de comparação booleana
            if self.current_char == '<':
                self.advance()
                return Token('LT', '<')
            if self.current_char == '>':
                self.advance()
                return Token('GT', '>')

            # concateção em lua: ..
            if self.current_char == '.':
                self.advance()
                if self.current_char == '.':
                    self.advance()
                    return Token('CONCAT', '..')
            # adicionando string em lua
            if self.current_char == '"':
                self.advance()
                result = ''
                while self.current_char != '"':
                    result += self.current_char
                    self.advance()
                self.advance()
                return Token('STRING', result)

            # Verificar o caso de ser um identificador de variável (começa com letra e contém letras e números)
            if self.current_char.isalpha():
                identifier = ''
                while self.current_char is not None and self.current_char.isalnum() or self.current_char == "_":
                    identifier += self.current_char
                    self.advance()
                if identifier in RESERVED_KEYWORDS:
                    # Se for um print, desvia
                    if identifier == 'print':
                        return Token('PRINT', 'print')
                    # checando para os novos elementos da lista de palavras reservadas
                    elif identifier == 'if':
                        return Token('IF', 'if')
                    elif identifier == 'else':
                        return Token('ELSE', 'else')
                    elif identifier == 'while':
                        return Token('WHILE', 'while')
                    elif identifier == 'do':
                        return Token('DO', 'do')
                    elif identifier == 'end':
                        return Token('END', 'end')
                    elif identifier == 'then':
                        return Token('THEN', 'then')
                    elif identifier == 'or':
                        return Token('OR', 'or')
                    elif identifier == 'and':
                        return Token('AND', 'and')
                    elif identifier == 'not':
                        return Token('NOT', 'not')
                    elif identifier == 'read':
                        return Token('READ', 'read')
                    elif identifier == 'local':
                        return Token('LOCAL', 'local')
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
                if Parser.symbol_table.get(identifier) is None:
                    raise NameError(f"Variável '{identifier}' não definida na tabela de símbolos!")
                expression, next_token = Parser.parseBooleanExpression()
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
        # Criação de variável (local)
        elif token.type == 'LOCAL':
            token = Parser.tokenizer.selectNext()
            if token.type == 'IDENTIFIER':
                identifier = token.value
                token = Parser.tokenizer.selectNext()
                if type(Parser.symbol_table.get(identifier)) is str:
                    raise NameError(f"Variável '{identifier}' já declarada!!")
                # verifica se já faz assign na criação
                if token.type == 'ASSIGN':
                    expression, next_token = Parser.parseBooleanExpression()
                    # Verifica se o próximo token é um /n, se não for, levanta um erro
                    if next_token.type != 'NEWLINE':
                        raise SyntaxError(f"Erro: Esperado fim de linha, encontrado '{next_token.value}'")
                    assignment_node = Assignment()
                    assignment_node.value = token.value
                    assignment_node.children.append(identifier)
                    assignment_node.children.append(expression)
                    Parser.symbol_table.set(identifier, expression)
                    return assignment_node
                elif token.type == 'NEWLINE':
                    Parser.symbol_table.set(identifier, "_")
                    return
                else:
                    raise SyntaxError("Erro: Esperado símbolo de atribuição '=' após identificador ou quebra de linha")
        # Se o token for um print, verifica se tem um (, expressao e um ). Se sim, cria um nó de print
        elif token.type == 'PRINT':
            token = Parser.tokenizer.selectNext()
            if token.type == 'LPAR':
                # print("-------------------------------------------\n")
                expression, token = Parser.parseBooleanExpression()
                # print(f"symbol_table(x): {Parser.symbol_table.symbol_table}\n")
                if token.type == 'RPAR':
                    print_node = Print()
                    print_node.value = "print"
                    print_node.children.append(expression)
                    # print(f"symbol_table(x): {Parser.symbol_table.symbol_table}\n")
                    return print_node
                else:
                    raise SyntaxError("Erro: Parênteses não fechados")
            else:
                raise SyntaxError("Erro: Parênteses não abertos")
        # adicionando a estrutura de repetição while considerando a lingugagem Lua
        elif token.type == 'WHILE':  # precisa ser WHILE, BooleanExpression, DO, \n, Statement até achar um END. Se não achar end, levanta um erro
            expression, token = Parser.parseBooleanExpression()
            if token.type == 'DO':
                # verificar se o próximo token é um \n
                token = Parser.tokenizer.selectNext()
                if token.type == 'NEWLINE':
                    block_node = Block()
                    token = Parser.tokenizer.selectNext()
                    while token.type != 'END':
                        # verifica se o token é um EOF e lança um erro
                        if token.type == 'EOF':
                            raise SyntaxError("Erro: Esperado 'END' ao usar While")
                        statement = Parser.parseStatement(token)
                        block_node.children.append(statement)
                        token = Parser.tokenizer.selectNext()
                    while_node = While()
                    while_node.children.append(expression)
                    while_node.children.append(block_node)
                    return while_node
                else:
                    raise SyntaxError("Erro: Esperado '\n' após DO")
            # adicionar erro se não tiver o DO
            else:
                raise SyntaxError("Erro: Esperado 'DO' após a expressão booleana")
        elif token.type == 'IF':
            tem_else = False
            expression, token = Parser.parseBooleanExpression()
            if token.type == 'THEN':
                # verificar se o próximo token é um \n
                token = Parser.tokenizer.selectNext()
                if token.type == 'NEWLINE':
                    block_node = Block()
                    token = Parser.tokenizer.selectNext()
                    # não precisa ter um else, mas precisa ter um end pois é lua
                    while token.type != 'END':
                        # verifica se o token é um EOF e lança um erro
                        if token.type == 'EOF':
                            raise SyntaxError("Erro: Esperado 'END' ao usar If")
                        statement = Parser.parseStatement(token)
                        block_node.children.append(statement)
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'ELSE':
                            tem_else = True
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'NEWLINE':
                                block_node_else = Block()
                                token = Parser.tokenizer.selectNext()
                                while token.type != 'END':
                                    statement = Parser.parseStatement(token)
                                    block_node_else.children.append(statement)
                                    token = Parser.tokenizer.selectNext()
                                break
                            else:
                                raise SyntaxError("Erro: Esperado '\n' após ELSE")
                    if token.type == 'END':
                        if_node = If()
                        if_node.children.append(expression)
                        if_node.children.append(block_node)
                        # se tiver else, adiciona o bloco de comandos do else
                        if tem_else:
                            if_node.children.append(block_node_else)
                        # verifica se o próximo token é um \n
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'NEWLINE':
                            return if_node
                        else:
                            raise SyntaxError("Erro: Esperado quebra de linha após END")


        else:
            raise SyntaxError("Erro: Comando inválido")

    @staticmethod
    def parseExpression():
        result_expression, token = Parser.parseTerm()
        while token.type in ["MINUS", "PLUS", "CONCAT"]:
            op = token.value
            result_term, token = Parser.parseTerm()
            bin_op_node = BinOp(op)
            bin_op_node.children.append(result_expression)
            bin_op_node.children.append(result_term)
            result_expression = bin_op_node
        return result_expression, token

    # criando o método RelationalExpression, que é uma expressão que pode conter operadores de comparação ==, <, >
    @staticmethod
    def parseRelationalExpression():
        result_expression, token = Parser.parseExpression()
        while token.type in ["LT", "GT", "EQUALS"]:
            op = token.value
            result_term, token = Parser.parseExpression()
            bin_op_node = BinOp(op)
            bin_op_node.children.append(result_expression)
            bin_op_node.children.append(result_term)
            result_expression = bin_op_node
        return result_expression, token

    # criando o método BooleanTerm, que é uma expressão que pode conter o operator 'and'.
    @staticmethod
    def parseBooleanTerm():
        result_expression, token = Parser.parseRelationalExpression()
        while token.type == "AND":
            op = token.value
            result_term, token = Parser.parseRelationalExpression()
            bin_op_node = BinOp(op)
            bin_op_node.children.append(result_expression)
            bin_op_node.children.append(result_term)
            result_expression = bin_op_node
        return result_expression, token

    # criando o método BooleanExpression, que é uma expressão que pode conter o operator 'or'.
    @staticmethod
    def parseBooleanExpression():
        result_expression, token = Parser.parseBooleanTerm()
        while token.type == "OR":
            op = token.value
            result_term, token = Parser.parseBooleanTerm()
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
        elif token.type == 'STRING':
            return String((token.value, 'STRING')), Parser.tokenizer.selectNext()
        # Se for um identificador, verifica se está na tabela de símbolos
        elif token.type == 'IDENTIFIER':
            identifier = token.value
            # if Parser.symbol_table.get(identifier):
            return Identifier(token.value), Parser.tokenizer.selectNext()
            #comentei tentando resolver while
            # else:
            #     raise NameError(f"Variável '{identifier}' não definida na tabela de símbolos!.")
        elif token.type == 'LPAR':
            result_expression, _ = Parser.parseBooleanExpression()
            if Parser.tokenizer.next.type == 'RPAR':
                return result_expression, Parser.tokenizer.selectNext()
            else:
                raise SyntaxError("Erro: Parênteses não fechados")
        elif token.type in ['PLUS', 'MINUS', 'NOT']:
            un_op_node = UnOp(token.value)
            result_factor, token = Parser.parseFactor()
            un_op_node.children.append(result_factor)
            return un_op_node, token
        elif token.type == 'READ':
            # ver se tem ( e ) e se o próximo token é um \n
            token = Parser.tokenizer.selectNext()
            if token.type == 'LPAR':
                token = Parser.tokenizer.selectNext()
                if token.type == 'RPAR':
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'NEWLINE':
                        return Read(token.value), token
                    else:
                        raise SyntaxError("Erro: Esperado '\n' após comando de leitura")
                else:
                    raise SyntaxError("Erro: Parênteses não fechados")
            else:
                raise SyntaxError("Erro: Parênteses não abertos")

        else:
            raise SyntaxError(f"Erro: Token inesperado: {token.value}")

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
    try:
        Parser.run(code)
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()