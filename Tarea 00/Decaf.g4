grammar Decaf;

/* Lexer tokens */

fragment LETTER:        [a-zA-Z_];

fragment DIGIT:         [0-9];

ID:     LETTER (LETTER|DIGIT)* ;

NUM:    DIGIT (DIGIT)* ;

CHAR:   '\'' LETTER '\'';

SPACES : [ \t\r\n\f]+  ->channel(HIDDEN);


/* Rules */

program:        'class' ID '{' (declaration)* '}' EOF;

declaration:    structDeclaration 
        | varDeclaration 
        | methodDeclaration;

varDeclaration: varType ID ';' 
        | varType ID '[' NUM ']' ';';

structDeclaration:      'struct' ID '{' (varDeclaration)* '}' ; 
/* Para que los ejemplos que se dio no de error se debe agregar ';' al final */

varType:        'int' 
        | 'char' 
        | 'boolean' 
        | 'struct' ID 
        | structDeclaration 
        | 'void';

methodDeclaration:      methodType ID '(' (parameter (',' parameter)*)*  ')' block;

methodType:     'int' 
        | 'char' 
        | 'boolean' 
        | 'void';

parameter: parameterType ID 
        | parameterType ID '[' ']'; 
/* Para que los ejemplos que se dio no de error se debe agregar | 'void' al final */

parameterType:  'int' 
        | 'char' 
        | 'boolean';

block:  '{' (varDeclaration)* (statement)* '}';

statement:      'if' '(' expression ')' block ('else' block)?
        | 'while' '(' expression ')' block
        | 'return' (expression)? ';'
        | methodCall ';'
        | block
        | location '=' expression 
        | (expression)? ';'; 

location:       (ID | ID '[' expression ']' ) ('.' location)?;

expression:     location 
        | methodCall 
        | literal
        | expression op expression
        | '-' expression
        | '!' expression
        | '(' expression ')';
        
methodCall:     ID '(' (arg (',' arg)*)* ')';

arg:    expression;

op:     arith_op
        | rel_op
        | eq_op
        | cond_op;

arith_op:       '+' 
        | '-' 
        | '*' 
        | '/' 
        | '%';

rel_op: '<' 
        | '>' 
        | '<=' 
        | '>=';

eq_op:  '==' 
        | '!=';

cond_op:        '&&' 
        | '||';

literal: int_literal 
        | char_literal 
        | bool_literal;

int_literal: NUM;

char_literal: CHAR; 

bool_literal: 'true' 
        | 'false';