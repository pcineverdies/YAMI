from _Token.const import AND
import _Token.token as token

# List of priorities 
LOWEST          = 0
OR              = 1
AND             = 2
EQUALS          = 3 
LESSGREATER     = 4
SUM             = 5
PRODUCT         = 6
PREFIX          = 7
CALL            = 8
INDEX           = 9

# Dictionary that associates each token type
# to its priority
precedences = {
    token.EQ        : EQUALS,
    token.NOT_EQ    : EQUALS,
    token.LT        : LESSGREATER,
    token.GT        : LESSGREATER,
    token.LTE       : LESSGREATER,
    token.GTE       : LESSGREATER,
    token.PLUS      : SUM,
    token.MINUS     : SUM,
    token.SLASH     : PRODUCT,
    token.ASTERISK  : PRODUCT,
    token.MODULUS   : PRODUCT,
    token.LPAREN    : CALL,
    token.LBRACKET  : INDEX,
    token.AND       : AND,
    token.OR        : OR,
}