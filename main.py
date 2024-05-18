import sys
import re

# Palavras reservadas
RESERVED_KEYWORDS = ['print', 'if', 'else', 'while', 'then', 'end', 'do', 'or', 'and', 'not', 'read',
                     'local', 'function', ',', 'return']

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
        self.offset = 0

    def create_entry(self, identifier):
        self.offset += 4
        self.symbol_table[identifier] = (None, None)

    def set(self, identifier, value):  # value é uma tupla de valor e tipo
        created = False
        if identifier not in self.symbol_table:
            self.create_entry(identifier)
            created = True
        self.symbol_table[identifier] = value

    def get(self, identifier):
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]


class FuncTable:
    functions = {}

    @staticmethod
    def get(func_name):
        return FuncTable.functions.get(func_name)

    @staticmethod
    def set(func_name, node):
        FuncTable.functions[func_name] = node


class Node:
    i = 0

    def __init__(self, value=None):
        self.value = value
        self.children = []
        self.id = self.newId()
        # self.id = 4

    @staticmethod
    def newId():
        Node.i += 1
        return Node.i

    def evaluate(self):
        pass


class Block(Node):
    def evaluate(self, symbol_table):
        for child in self.children:

            if child != None:
                #print(f"child: {child}")
                # verifica se o nó é um return
                if isinstance(child, Return):
                    return child.evaluate(symbol_table)
                child.evaluate(symbol_table)


class Assignment(Node):
    def evaluate(self, symbol_table):
        identifier = self.children[0]
        value_node = self.children[1]  # Acessando o nó de valor
        # print(f"isinstance(value_node, IntVal): {isinstance(value_node, IntVal)}")
        if isinstance(value_node, IntVal):  # Verificando se o nó de valor é do tipo IntVal
            value = value_node.evaluate()  # Se for, apenas obtemos o valor
        # faz um elif para vericar se é um Read, e aí não passa o symbol_table
        elif isinstance(value_node, Read):
            # faz o evaluate do read de modo que o metodo consiga acessar a posição do symbol_table para gerar o assembly corretamente
            value = value_node.evaluate(symbol_table.get(identifier)[1])
        # vamos ver se é uma string
        elif isinstance(value_node, String):
            value = value_node.evaluate()
        else:
            value = value_node.evaluate(symbol_table)  # Caso contrário, avaliamos a expressão
        if value is None:
            raise ValueError(f"Atribuição inválida para a variável '{identifier}'")
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
            if isinstance(left, IntVal):
                left = String((str(left.value[0]), 'STRING'))
            if isinstance(right, IntVal):
                right = String((str(right.value[0]), 'STRING'))
            if isinstance(left, tuple) and isinstance(right, tuple):
                return String((left[0] + right[0], 'STRING'))
            elif isinstance(left, String) and isinstance(right, tuple):
                return String((left.value[0] + right[0], 'STRING'))
            if not isinstance(left, String) or not isinstance(right, String):
                return String((left[0] + right.value[0], 'STRING'))
            return String((left.value[0] + right.value[0], 'STRING'))

        if self.value in ['+', '-', '*', '/'] or self.value in ['or', 'and', '==', '<', '>']:
            # print(f"left: {left}")
            # print(f"right: {right}")
            # se right não for uma tupla, transforma em uma com a posição 0 sendo o valor e a posição 1 sendo None
            if not isinstance(right, tuple):
                right = (right, None)
            # se left não for uma tupla, transforma em uma com a posição 0 sendo o valor e a posição 1 sendo None
            if not isinstance(left, tuple):
                left = (left, None)
            if self.value == '+':
                return IntVal((left[0].value[0] + right[0].value[0], 'INT'))
            elif self.value == '-':
                return IntVal((left[0].value[0] - right[0].value[0], 'INT'))
            elif self.value == '*':
                return IntVal((left[0].value[0] * right[0].value[0], 'INT'))
            elif self.value == '/':
                if right[0].value[0] == 0:
                    return IntVal((0, 'INT'))
                return IntVal((left[0].value[0] // right[0].value[0], 'INT'))
            # adicionar operadores de comparação and, or, ==, <, >:
            elif self.value == 'or':
                if left[0].value[1] == 'INT' and right[0].value[1] == 'INT':
                    if left[0].value[0] or right[0].value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
                raise TypeError("Operação não suportada para os valores tipos fornecidos")
            elif self.value == 'and':
                if left[0].value[1] == 'INT' and right[0].value[1] == 'INT':
                    if left[0].value[0] and right[0].value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
                raise TypeError("Operação não suportada para os valores tipos fornecidos")
            elif self.value == '==':
                if (isinstance(left, String) or isinstance(left, IntVal)) and (
                        isinstance(right, String) or isinstance(right, IntVal)):
                    if left.value[0] == right.value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
                elif isinstance(left, tuple) and isinstance(right, tuple):
                    if isinstance(left[0], str) and isinstance(right[0], str):
                        if left[0] == right[0]:
                            return IntVal((1, 'INT'))
                        return IntVal((0, 'INT'))
                    if left[0].value == right[0].value:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
            elif self.value == '<':
                # print(f"self.value: {self.value}")
                if (isinstance(left, String) or isinstance(left, IntVal)) and (isinstance(right, String) or isinstance(right, IntVal)):
                    if left.value[0] < right.value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
                elif isinstance(left, tuple) and isinstance(right, tuple):
                    if isinstance(left[0], str) and isinstance(right[0], str):
                        if left[0] < right[0]:
                            return IntVal((1, 'INT'))
                        return IntVal((0, 'INT'))
                    if left[0].value[0] < right[0].value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
            elif self.value == '>':
                # print(f"self.value: {self.value}")
                if (isinstance(left, String) or isinstance(left, IntVal)) and (
                        isinstance(right, String) or isinstance(right, IntVal)):
                    if left.value[0] > right.value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
                elif isinstance(left, tuple) and isinstance(right, tuple):
                    if isinstance(left[0], str) and isinstance(right[0], str):
                        if left[0] > right[0]:
                            return IntVal((1, 'INT'))
                        return IntVal((0, 'INT'))
                    if left[0].value[0] > right[0].value[0]:
                        return IntVal((1, 'INT'))
                    return IntVal((0, 'INT'))
        else:
            raise TypeError("Operação não suportada para os valores fornecidos")


class UnOp(Node):
    def evaluate(self, symbol_table=None):
        if self.value == '-':
            # print(f"Estou no UnOp")
            # print(f"O retorno é: {IntVal((-self.children[0].evaluate(symbol_table).value[0], 'INT'))}")
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
        return symbol_table.get(self.value)


class Read(Node):
    def evaluate(self, identifier):
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


class VarDec(Node):
    def evaluate(self, symbol_table):
        return


class Print(Node):
    def evaluate(self, symbol_table):
        # avalia se children[0] é um IntVal ou uma expressão
        if isinstance(self.children[0], IntVal) or isinstance(self.children[0], String):
            print(self.children[0].evaluate().value[0])
        else:
            # print("Else")
            # checar se é binOp. Se for, avaliar
            if isinstance(self.children[0], BinOp):
                print(self.children[0].evaluate(symbol_table).value[0])
                return
            print(self.children[0].evaluate(symbol_table).value[0])


class While(Node):
    def evaluate(self, symbol_table):
        # Introduzir o filho 0 (condição) e retornar o resultado em EBX
        # Instruções do filho 1 (bloco de comandos)
        while self.children[0].evaluate(symbol_table).value[0]:  # reavalia a condição em cada iteração
            self.children[1].evaluate(symbol_table)


class If(Node):
    def evaluate(self, symbol_table):
        expression = self.children[0]  # condição do if
        block = self.children[1]  # bloco de comandos
        # verifica o len do nó, se for 3, tem um else
        if len(self.children) == 3:
            block_else = self.children[2]  # bloco de comandos do else
            if expression.evaluate(symbol_table).value[0]:
                block.evaluate(symbol_table)
            else:
                block_else.evaluate(symbol_table)
        else:
            if expression.evaluate(symbol_table).value[0]:
                block.evaluate(symbol_table)


# classe para o return
class Return(Node):
    def __init__(self, value=None):
        super().__init__(value=value)

    def evaluate(self, symbol_table):
        return self.children[0].evaluate(symbol_table)


class FuncDec(Node):
    def evaluate(self, symbol_table):
        # set na funtable passando o nome da função e o node para o FuncTable
        FuncTable.set(self.value, self)
        # os filhos que são strings são os argumentos da funçãoo. Os filhos que são blocos são os comandos da função


class FuncCall(Node):
    def evaluate(self, symbol_table):
        # recupera o nó de declaração da função na FuncTable, atribuindo os valores dos argumentos de entrada e executando o bloco de comandos
        func_node = FuncTable.get(self.value)
        # criar uma nova tabela de símbolos para a função (temporária, será deletada após a execução da função)
        func_symbol_table = SymbolTable()
        # percorre func_node.children até achar o elementpo que é um bloco de comandos
        for i in range(len(func_node.children)):
            if isinstance(func_node.children[i], Block):
                break
        # verifica se o número de argumentos passados é igual ao número de argumentos esperaods pela função(i)
        if len(self.children) != i:
            raise ValueError("Número de argumentos passados diferente do número de argumentos esperados pela função")

        # for j in range(len(self.children)):
        #     if isinstance(self.children[j], IntVal) or isinstance(self.children[j], String):
        #         print("if")
        #         print(f"self.children[j]: {self.children[j]}")
        #         print(f"self.children[j].evaluate(): {self.children[j].evaluate().value[0]}")
        #     else:
        #         print("else")
        #         print(f"self.children[j]: {self.children[j]}")
        #         print(f"self.children[j].evaluate(symbol_table): {self.children[j].evaluate(symbol_table)[0].value[0]}")

        # preenche uma tabela de símbolos temporária para a função e seta os valores dos argumentos passados
        for j in range(len(self.children)):
            if isinstance(self.children[j], IntVal) or isinstance(self.children[j], String):
                #verifica se já existe a variável na tabela de símbolos, se já existir, gerar um erro
                func_symbol_table.set(func_node.children[j], self.children[j].evaluate())
            else:
                func_symbol_table.set(func_node.children[j], self.children[j].evaluate(symbol_table))
        # exibe a tabela de símbolos temporária
        # executa o bloco de comandos da função
        return func_node.children[i].evaluate(func_symbol_table)


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
            # adicionar a virgula
            if self.current_char == ',':
                self.advance()
                return Token('COMMA', ',')
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
                    elif identifier == 'function':
                        return Token('FUNCTION', 'function')
                    elif identifier == 'return':
                        return Token('RETURN', 'return')
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
            statement = Parser.parseStatement(token, False)
            block_node.children.append(statement)
            token = Parser.tokenizer.selectNext()
        # fazer o evaluate do bloco
        # print(f"Hello from parseBlock")
        block_node.evaluate(Parser.symbol_table)

    @staticmethod
    def parseStatement(token, isFunction):
        # Se o token for um /n, não faz nada
        if token.type == 'NEWLINE':
            return
        # Se o token for um identificador, cria um nó de atribuição (Assignment)
        elif token.type == 'IDENTIFIER':
            #print(f"token.value: {token.value}")
            identifier = token.value
            token = Parser.tokenizer.selectNext()
            #print(f"token.value: {token.value}")
            if token.type == 'ASSIGN':
                #if Parser.symbol_table.get(identifier) is None:
                #     raise NameError(f"Variável '{identifier}' não definida na tabela de símbolos!")
                expression, next_token = Parser.parseBooleanExpression()
                # Verifica se o próximo token é um /n, se não for, levanta um erro
                #print(f"next_token.type: {next_token.type}")
                # se o next_token for uma vírgula, ainda não é o fim da expressão, indica que é uma função com argumentos
                if next_token.type == 'COMMA':
                    next_token = Parser.tokenizer.selectNext()
                    #se o proximo token for uma quebra de linha, leva um erro
                    if next_token.type == 'NEWLINE':
                        raise SyntaxError("Erro: Esperado expressão após ','")
                    func_call_node = FuncCall()
                    func_call_node.value = identifier
                    func_call_node.children.append(expression)
                    while next_token.type != 'RPAR':
                        if next_token.type == 'INT':
                            func_call_node.children.append(IntVal(next_token.value))
                            next_token = Parser.tokenizer.selectNext()
                            if next_token.type == 'COMMA':
                                next_token = Parser.tokenizer.selectNext()
                            else:
                                break
                        elif next_token.type == 'STRING':
                            func_call_node.children.append(String((next_token.value, 'STRING')))
                            next_token = Parser.tokenizer.selectNext()
                            if next_token.type == 'COMMA':
                                next_token = Parser.tokenizer.selectNext()
                            else:
                                break
                        elif next_token.type == 'IDENTIFIER':
                            func_call_node.children.append(Identifier(next_token.value))
                            next_token = Parser.tokenizer.selectNext()
                            if next_token.type == 'COMMA':
                                next_token = Parser.tokenizer.selectNext()
                            else:
                                break
                    #print(f"Saiu do while")
                    #print(f"token.value: {next_token.value}")
                    #print(f"token.type: {next_token.type}")
                    if next_token.type == 'RPAR':
                        next_token = Parser.tokenizer.selectNext()
                        #print(f"token.value: {next_token.value}")
                        #print(f"token.type: {next_token.type}")
                        if next_token.type != 'NEWLINE':
                            raise SyntaxError("Erro: Esperado quebra de linha após a chamada da função")
                if next_token.type != 'NEWLINE':
                    raise SyntaxError(f"!Erro: Esperado fim de linha, encontrado '{next_token.value}'")
                assignment_node = Assignment()
                assignment_node.value = token.value
                assignment_node.children.append(identifier)
                assignment_node.children.append(expression)
                #if isFunction is False:
                Parser.symbol_table.set(identifier, expression)
                return assignment_node
            elif token.type == 'LPAR':
                block_node = Block()
                token = Parser.tokenizer.selectNext()
                func_call_node = FuncCall()
                func_call_node.value = identifier
                while token.type != 'RPAR':
                    if token.type == 'INT':
                        func_call_node.children.append(IntVal(token.value))
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'COMMA':
                            token = Parser.tokenizer.selectNext()
                        else:
                            break
                    elif token.type == 'STRING':
                        func_call_node.children.append(String((token.value, 'STRING')))
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'COMMA':
                            token = Parser.tokenizer.selectNext()
                        else:
                            break
                    elif token.type == 'IDENTIFIER':
                        func_call_node.children.append(Identifier(token.value))
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'COMMA':
                            token = Parser.tokenizer.selectNext()
                        else:
                            break
                if token.type == 'RPAR':
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'NEWLINE':
                        return func_call_node
                    else:
                        raise SyntaxError("Erro: Esperado quebra de linha após a chamada da função")
            else:
                raise SyntaxError(
                    f"Erro: Esperado símbolo de atribuição '=' após identificador. Encontrado token.type: '{token.type},token.value:'{token.value}'")
        # Criação de variável (local)
        elif token.type == 'LOCAL':
            token = Parser.tokenizer.selectNext()
            if token.type == 'IDENTIFIER':
                identifier = token.value
                token = Parser.tokenizer.selectNext()
                # verifica se a variável já foi declarada checandop se o get é uma tupla
                if isinstance(Parser.symbol_table.get(identifier), tuple):
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
                    #if isFunction is False:
                    Parser.symbol_table.set(identifier, expression)
                    return assignment_node
                elif token.type == 'NEWLINE':
                    var_declaration = VarDec()
                    var_declaration.value = identifier
                    #if isFunction is False:
                    Parser.symbol_table.create_entry(identifier)
                    return var_declaration
                else:
                    raise SyntaxError("Erro: Esperado símbolo de atribuição '=' após identificador ou quebra de linha")
        # Se o token for um print, verifica se tem um (, expressao e um ). Se sim, cria um nó de print
        elif token.type == 'PRINT':
            token = Parser.tokenizer.selectNext()
            if token.type == 'LPAR':
                expression, token = Parser.parseBooleanExpression()
                if token.type == 'RPAR':
                    print_node = Print()
                    print_node.value = "print"
                    print_node.children.append(expression)
                    return print_node
                else:
                    raise SyntaxError("Erro: Parênteses não fechados PRINT")
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
                        statement = Parser.parseStatement(token, isFunction)
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
                        # se o token.type já for ELSE, o IF não tem bloco de comandos
                        if token.type == 'ELSE':
                            tem_else = True
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'NEWLINE':
                                block_node_else = Block()
                                token = Parser.tokenizer.selectNext()
                                while token.type != 'END':
                                    statement = Parser.parseStatement(token, isFunction)
                                    block_node_else.children.append(statement)
                                    token = Parser.tokenizer.selectNext()
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
                                raise SyntaxError("Erro: Esperado '\n' após ELSE")
                        statement = Parser.parseStatement(token, isFunction)
                        token = Parser.tokenizer.selectNext()
                        block_node.children.append(statement)
                        if token.type == 'ELSE':
                            tem_else = True
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'NEWLINE':
                                block_node_else = Block()
                                token = Parser.tokenizer.selectNext()
                                while token.type != 'END':
                                    statement = Parser.parseStatement(token, isFunction)
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
        # adicionando function e return
        elif token.type == 'FUNCTION':
            token = Parser.tokenizer.selectNext()
            if token.type == 'IDENTIFIER':
                identifier = token.value
                token = Parser.tokenizer.selectNext()
                if token.type == 'LPAR':
                    token = Parser.tokenizer.selectNext()
                    block_node = Block()
                    func_dec_node = FuncDec()
                    func_dec_node.value = identifier
                    while token.type != 'RPAR':
                        if token.type == 'IDENTIFIER':
                            func_dec_node.children.append(token.value)
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'COMMA':
                                token = Parser.tokenizer.selectNext()
                            else:
                                break
                    if token.type == 'RPAR':
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'NEWLINE':
                            token = Parser.tokenizer.selectNext()
                            while token.type != 'END':
                                statement = Parser.parseStatement(token, True)
                                block_node.children.append(statement)
                                token = Parser.tokenizer.selectNext()
                            if token.type == 'END':
                                func_dec_node.children.append(block_node)
                                return func_dec_node
                        else:
                            raise SyntaxError("Erro: Esperado '\n' após parênteses")
                    else:
                        raise SyntaxError("Erro: Parênteses não fechados")
                else:
                    raise SyntaxError("Erro: Parênteses não abertos")
            else:
                raise SyntaxError("Erro: Esperado identificador após FUNCTION")
        elif token.type == 'RETURN':
            return_node = Return()
            expression, token = Parser.parseBooleanExpression()
            return_node.children.append(expression)
            return return_node
            # if token.type == 'NEWLINE':
            #     return return_node
            # else:
            #     raise SyntaxError("Erro: Esperado quebra de linha após RETURN")
        else:
            raise SyntaxError(
                f"Erro: Comando inválido: {token.value}.")  # \n O código de entrada foi:\n {Parser.tokenizer.source}")

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
        elif token.type == 'IDENTIFIER':
            identificador = token.value
            token = Parser.tokenizer.selectNext()
            if token.type == 'LPAR':
                func_call_node = FuncCall()
                func_call_node.value = identificador
                token = Parser.tokenizer.selectNext() #comentei aqui 17/05 20h13
                if token.type == 'RPAR':
                    func_call_node.children.append(NoOp())
                    token = Parser.tokenizer.selectNext()
                if token.type == 'IDENTIFIER':
                    identifier = token.value
                    #func_call_node.children.append(Identifier(identifier))
                    token = Parser.tokenizer.selectNext()
                    if token.type == 'LPAR':
                        # é uma chamada de função
                        func_call_node_2 = FuncCall()
                        func_call_node_2.value = identifier
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'RPAR':
                            # verifica se tem algum sinal de operação após a chamada da função
                            token = Parser.tokenizer.selectNext()
                            if token.type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'CONCAT', 'LT', 'GT', 'EQUALS', 'AND',
                                              'OR']:
                                bin_op_node = BinOp(token.value)
                                bin_op_node.children.append(func_call_node_2)
                                result_expression, token = Parser.parseFactor()
                                bin_op_node.children.append(result_expression)
                                func_call_node.children.append(bin_op_node)
                            else:
                                func_call_node.children.append(func_call_node_2)
                                # return func_call_node, token
                        else:
                            # é uma função com argumentos
                            result_expression, token = Parser.parseBooleanExpression()
                            func_call_node.children.append(result_expression)
                            while token.type == 'COMMA':
                                result_expression, token = Parser.parseBooleanExpression()
                                func_call_node.children.append(result_expression)
                            if token.type == 'RPAR':
                                token = Parser.tokenizer.selectNext()
                                if token.type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'CONCAT', 'LT', 'GT', 'EQUALS', 'AND',
                                                  'OR']:
                                    bin_op_node = BinOp(token.value)
                                    bin_op_node.children.append(func_call_node)
                                    result_expression, token = Parser.parseFactor()
                                    bin_op_node.children.append(result_expression)
                                    return bin_op_node, token
                                else:
                                    return func_call_node, token
                    elif token.type == 'COMMA':
                        func_call_node.children.append(Identifier(identifier))
                        token = Parser.tokenizer.selectNext()
                        if token.type == 'INT':
                            func_call_node.children.append(IntVal(token.value))
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'RPAR':
                                token = Parser.tokenizer.selectNext()
                                if token.type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'CONCAT', 'LT', 'GT', 'EQUALS', 'AND',
                                                  'OR']:
                                    bin_op_node = BinOp(token.value)
                                    bin_op_node.children.append(func_call_node)
                                    result_expression, token = Parser.parseFactor()
                                    bin_op_node.children.append(result_expression)
                                    return bin_op_node, token
                                else:
                                    return func_call_node, token
                            else:
                                raise SyntaxError("Erro: Parênteses não fechados 1")
                        elif token.type == 'STRING':
                            func_call_node.children.append(String((token.value, 'STRING')))
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'RPAR':
                                token = Parser.tokenizer.selectNext()
                                if token.type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'CONCAT', 'LT', 'GT', 'EQUALS', 'AND',
                                                  'OR']:
                                    bin_op_node = BinOp(token.value)
                                    bin_op_node.children.append(func_call_node)
                                    result_expression, token = Parser.parseFactor()
                                    bin_op_node.children.append(result_expression)
                                    return bin_op_node, token
                                else:
                                    return func_call_node, token
                            else:
                                raise SyntaxError("Erro: Parênteses não fechados 1")
                        elif token.type == 'IDENTIFIER':
                            identifier = token.value
                            func_call_node.children.append(Identifier(identifier))
                            token = Parser.tokenizer.selectNext()
                            if token.type == 'RPAR':
                                token = Parser.tokenizer.selectNext()
                                if token.type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'CONCAT', 'LT', 'GT', 'EQUALS',
                                                  'AND',
                                                  'OR']:
                                    bin_op_node = BinOp(token.value)
                                    bin_op_node.children.append(func_call_node)
                                    result_expression, token = Parser.parseFactor()
                                    bin_op_node.children.append(result_expression)
                                    return bin_op_node, token
                                else:
                                    return func_call_node, token
                    elif token.type == 'CONCAT':
                        bin_op_node = BinOp(token.value)
                        bin_op_node.children.append(Identifier(identifier))
                        result_expression, token = Parser.parseFactor()
                        bin_op_node.children.append(result_expression)
                        func_call_node.children.append(bin_op_node)
                    else:
                        func_call_node.children.append(Identifier(identifier))
                        return func_call_node, token
                while token.type == 'COMMA':
                    result_expression, token = Parser.parseBooleanExpression()
                    func_call_node.children.append(result_expression)
                if token.type == 'RPAR':
                    return func_call_node, Parser.tokenizer.selectNext()
                else:
                    raise SyntaxError("Erro: Parênteses não fechados 1")
            else:
                return Identifier(identificador), token
        elif token.type == 'LPAR':
            # novo
            # token = Parser.tokenizer.selectNext()
            # if token.type == 'RPAR':
            #     return NoOp(), Parser.tokenizer.selectNext()
            # até essa de cima
            result_expression, token = Parser.parseBooleanExpression()
            if token.type == 'RPAR':
                return result_expression, Parser.tokenizer.selectNext()
            else:
                raise SyntaxError("Erro: Parênteses não fechados")
        elif token.type in ['PLUS', 'MINUS', 'NOT']:
            un_op_node = UnOp(token.value)
            result_factor, token = Parser.parseFactor()
            un_op_node.children.append(result_factor)
            return un_op_node, token
        elif token.type == 'READ':
            token = Parser.tokenizer.selectNext()
            if token.type == 'LPAR':
                token = Parser.tokenizer.selectNext()
                if token.type == 'RPAR':
                    return Read(token.value), Parser.tokenizer.selectNext()
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
        #raise TypeError(f"code: {code}")
    try:
        Parser.run(code)
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()