import sys
import re

# 1. Implementar a árvore sintática abstrata (AST)
class PrePro:
    @staticmethod
    def filter(code):
        # Remove comentários
        return re.sub(r"--.*", "", code)


class Node:
    def __init__(self, value=None):
        self.value = value
        self.children = []

    def evaluate(self):
        pass


class BinOp(Node):
    def evaluate(self):
        left = self.children[0].evaluate()
        right = self.children[1].evaluate()
        if self.value == '+':
            return left + right
        elif self.value == '-':
            return left - right
        elif self.value == '*':
            return left * right
        elif self.value == '/':
            return left // right


class UnOp(Node):
    def evaluate(self):
        if self.value == '-':
            return -self.children[0].evaluate()
        else:
            return self.children[0].evaluate()



class IntVal(Node):
    def evaluate(self):
        return self.value


class NoOp(Node):
    def evaluate(self):
        pass


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
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

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
        return result_expression

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
        elif token.type == 'LPAR':
            result_expression = Parser.parseExpression()
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
        result = Parser.parseExpression()
        if Parser.tokenizer.next.type != 'EOF':
            raise SyntaxError("Erro: Tokens inesperados no final da expressão")
        return result


def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        code = file.read()
    result = Parser.run(code)
    print(result.evaluate())


if __name__ == "__main__":
    main()
