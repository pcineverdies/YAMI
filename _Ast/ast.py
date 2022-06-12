import _Token.token as token

class Node:
    def tokenLiteral(self):
        pass

class Statement(Node):
    def statementNode(self):
        pass

class Expression(Node):
    def expressionNode(self):
        pass

class Program:
    def __init__(self):
        self.statements = []
    
    def tokenLiteral(self):
        if len(self.statements) > 0:
            return self.statements[0].tokenLiteral()
        
        else:
            return ""

class Identifier(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value
    
    def expressionNode(self):
        return super().expressionNode()
    
    def tokenLiteral(self):
        return self.token.literal

class LetStatement(Statement):
    def __init__(self, token, name, value):
        self.token = token
        self.name = name
        self.value = value

    def statementNode(self):
        return super().statementNode()
    
    def tokenLiteral(self):
        return self.token.literal

class ReturnStatement(Statement):
    def __init__(self, token, returnValue):
        self.token = token
        self.returnValue = returnValue
        
    def statementNode(self):
        return super().statementNode()
    
    def tokenLiteral(self):
        return self.token.literal