from typing import List
import _Ast.ast as ast
import _Object.object as object

# main evaluator (recursive) function: depending on the curret ast.node,
# it calls different functions
def Eval(node : ast.Node, env : object.Environment) -> object.Object:
    # case of the program, as an array of statements
    if isinstance(node, ast.Program):
        return evalProgram(node.statements, env)

    # case of an expression
    elif isinstance(node, ast.ExpressionStatement):
        return Eval(node.expression, env)

    # case of an integer literal
    elif isinstance(node, ast.IntegerLiteral):
        return object.Integer(node.value)

    # case of a boolean
    elif isinstance(node, ast.Boolean):
        return nativeBoolToBooleanObject(node.value)

    # case of a prefix expression
    elif isinstance(node, ast.PrefixExpression):
        # first: eval the right expression
        right = Eval(node.right, env)
        if isError(right):
            return right

        # second: apply the prefix operator
        return evalPrefixExpression(node.operator, right)

    # case of infix expression
    elif isinstance(node, ast.InfixExpression):
        # first: eval the right expression
        right = Eval(node.right, env)
        if isError(right):
            return right

        # second: eval the left expression
        left  = Eval(node.left, env)
        if isError(left):
            return left

        # third: apply the operator
        return evalInfixExpression(node.operator, left, right)
    
    # case of a block statement (eval eash stmt)
    elif isinstance(node, ast.BlockStatement):
        return evalBlockStatements(node, env)
    
    # case of an if statement (eval consequence depending on condition)
    elif isinstance(node, ast.IfExpression):
        return evalIfExpression(node, env)
    
    # case of a return statement
    elif isinstance(node, ast.ReturnStatement):
        val = Eval(node.value, env)
        if isError(val):
            return val

        return object.ReturnValue(val)
    
    # case of a let statement
    elif isinstance(node, ast.LetStatement):
        val = Eval(node.value, env)
        if isError(val):
            return val
        
        # set the current enviroment value
        env.set(node.name.value, val)
    
    # case of an identifier (get its value from env)
    elif isinstance(node, ast.Identifier):
        return evalIdentifier(node, env)
    
    # case of a function literal
    elif isinstance(node, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return object.Function(params, body, env)
    
    # case of a call expression
    elif isinstance(node, ast.CallExpression):
        # eval the function
        function = Eval(node.function, env)
        if isError(function):
            return function
        
        # eval its arguments
        args = evalExpressions(node.arguments, env)
        if len(args) == 1 and isError(args[0]):
            return args[0]

        # apply the function
        return applyFunction(function, args)

    # no functino to eval the ast.node
    else:
        return None

# return the corresponding instance of object.Object
def nativeBoolToBooleanObject(exp : bool) -> object.Object:
    return object.TRUE if exp else object.FALSE

# eval prefix expression depending on the operator
def evalPrefixExpression(operator : str, right : object.Object) -> object.Object:
    if operator == "!":
        return evalBangOperatorExpression(right)
    elif operator == "-":
        return evalMinusPrefixOperatorExpression(right)
    else:
        return newError("unknwon operator: {}{}", operator, right.type())

# eval the bang operator
def evalBangOperatorExpression(right : object.Object) -> object.Object:
    if right in [object.FALSE, object.NULL]:
        return object.TRUE
    return object.FALSE

# eval the minus prefix operator
def evalMinusPrefixOperatorExpression(right : object.Object) -> object.Object:
    if not isinstance(right, object.Integer):
        return newError("unknown operator: -{}", right.type())
    
    value = right.value
    return object.Integer(-value)

# eval infix expression: get the vlaues of left and right and apply the python's correspondant operator
def evalInfixExpression(operator : str, left : object.Object, right : object.Object) -> object.Object:  
    # case of both integers
    if left.type() == object.INTEGER_OBJ and right.type() == object.INTEGER_OBJ:
        return evalIntegerInfixExpression(operator, left, right)
    
    if operator == "==":
        return nativeBoolToBooleanObject(left == right)
    if operator == "!=":
        return nativeBoolToBooleanObject(left != right)
    if left.type() != right.type():
        return newError("type mismatch: {} {} {}", left.type(), operator, right.type())
    else:
        return newError("unknown operator: {} {} {}", left.type(), operator, right.type())

# eval integer infix expression
def evalIntegerInfixExpression(operator : str, left : object.Object, right : object.Object) -> object.Object:  
    leftValue = left.value
    rightValue = right.value

    if operator == "+":
        return object.Integer(leftValue + rightValue)
    if operator == "-":
        return object.Integer(leftValue - rightValue)
    if operator == "*":
        return object.Integer(leftValue * rightValue)
    # in case of integers, '/' is the division between integers
    if operator == "/":
        return object.Integer(leftValue // rightValue)
    if operator == "<":
        return nativeBoolToBooleanObject(leftValue <  rightValue)
    if operator == ">":
        return nativeBoolToBooleanObject(leftValue >  rightValue)
    if operator == "==":
        return nativeBoolToBooleanObject(leftValue == rightValue)
    if operator == "!=":
        return nativeBoolToBooleanObject(leftValue != rightValue)
    
    return newError("unknown operator: {} {} {}", left.type(), operator, right.type())

# eval if expression
def evalIfExpression(ie : ast.IfExpression, env: object.Environment) -> object.Object:
    # eval condition
    condition = Eval(ie.condition, env)
    if isError(condition):
        return condition
    
    # if condition is true, eval consequence
    if isTruthy(condition):
        return Eval(ie.consequence, env)
    
    # else if there's else branch, eval it
    elif ie.alternative is not None:
        return Eval(ie.alternative, env)
    
    # else return NULL
    else:
        return object.NULL

def isTruthy(obj : object.Object) -> bool:
    if obj in [object.FALSE, object.NULL]:
        return False
    return True

# eval each statement of the program
def evalProgram(program : ast.Program, env : object.Environment) -> object.Object:
    result = None
    for statement in program:
        # refresh the result value for each statement, so that that last statement
        # give the return value of the block
        result = Eval(statement, env)

        # if we encounter a return statement, we don't want to go on
        if isinstance(result, object.ReturnValue):
            return result.value
        elif isinstance(result, object.Error):
            return result
    return result

# eval each statement of the block
def evalBlockStatements(block : ast.BlockStatement, env : object.Environment) -> object.Object:
    result = None
    for statement in block.statements:
        result = Eval(statement, env)

        if result is not None:
            rt = result.type()
            if rt == object.RETURN_VALUE_OBJ or rt == object.ERROR_OBJ:
                return result

    return result

def newError(*args):
    return object.Error(args[0].format(*args[1:]))

def isError(obj : object.Object) -> bool:
    if obj is not None:
        return obj.type() == object.ERROR_OBJ
    return False

# get the identifer from the current env
def evalIdentifier(node : ast.Identifier, env : object.Environment) -> object.Object:
    val, ok = env.get(node.value)
    if not ok:
        return newError("identifier not found: " + node.value)
    return val

# eval expressions as input of function call
def evalExpressions(exps : List[ast.Expression], env : object.Object) -> List[object.Object]:
    result = []

    for elem in exps:
        evaluated = Eval(elem, env)
        if isError(evaluated):
            return [evaluated]
        result.append(evaluated)
    
    return result

# apply a function
def applyFunction(fn : object.Object, args : List[object.Object]) -> object.Object:
    if not isinstance(fn, object.Function):
        return newError("not a function: {}", fn.type())
    if len(fn.parameters) != len(args):
        return newError("wrong number of parametrs: wanted {}, got {}", len(fn.parameters), len(args))
    
    # we extended the environment of a function pushing the arguments too
    extendedEnv = extendFunctionEnvironment(fn, args)
    evaluated = Eval(fn.body, extendedEnv)
    return unwrapReturnValue(evaluated)

# extend function environment
def extendFunctionEnvironment(fn : object.Object, args : List[object.Object]) -> object.Environment:
    env = object.Environment(fn.env)

    for idx, param in enumerate(fn.parameters):
        env.set(param.value, args[idx])

    return env

def unwrapReturnValue(ev : object.Object) -> object.Object:
    if isinstance(ev, object.ReturnValue):
        return ev.value
    
    return ev