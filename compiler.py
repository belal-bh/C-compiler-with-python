# ---------------------------------------------
#       SIMPLE C COMPILER USING PYTHON
#       Author: MD. BELAL HOSSAIN
#       Date  : 22 September, 2018
# ---------------------------------------------
import collections
import re
import csv

# Token collection
Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])

# file_path of the C program file
# file_path = 'c_file.c'
file_path = 'c_file_with_error.c'

# regex for COMMENT in C
commentdict = {
    r'/\*.*?\*\/': 't_MULTILINECOMMENT',
    r'//.*?\n': 't_SINGLELINECOMMENT'
}


# HEADER FILES
# regex for HEADER_FILE token in headerfiledict
headerfiledict = {
    r'[a-zA-Z]+\.h': 't_HEADER'
}
# HEADER_FILE list as headerfilelist
headerfilelist = [
    'stdio.h',
    'conio.h',
    'assert.h',
    'ctype.h',
    'cocale.h',
    'math.h',
    'setjmp.h',
    'signal.h',
    'stdarg.h',
    'stdlib.h',
    'string.h',
    'time.h',
    'complex.h',
    'stdalign.h',
    'errno.h',
    'locale.h',
    'stdatomic.h',
    'stdnoreturn.h',
    'uchar.h',
    'fenv.h',
    'wchar.h',
    'tgmath.h',
    'stdarg.h',
    'stdbool.h',
]

# ANSI C Keyword (32  + 2)
keywordlist = [
    'auto',
    'break',
    'case',
    'char',
    'const',
    'continue',
    'default',
    'do',
    'double',
    'else',
    'enum',
    'extern',
    'float',
    'for',
    'goto',
    'if',
    'int',
    'long',
    'register',
    'return',
    'short',
    'signed',
    'sizeof',
    'static',
    'struct',
    'switch',
    'typedef',
    'union',
    'unsigned',
    'void',
    'volatile',
    'while',
    # now something that not keyword in ANSI C but we assume it as keyword in our program
    'include',
    'define',
    'main'
]

# all 2 length's spacial character as meta2dict
meta2dict = {
    r'\+\+': 't_INCREMENT',
    r'\-\-': 't_DECREMENT',
    r'==': 't_EQEQUAL',
    r'!=': 't_NOTEQUAL',
    r'<=': 't_LESSEQUAL',
    r'<<': 't_LEFTSHIFT',
    r'>=': 't_GREATEREQUAL',
    r'>>': 't_RIGHTSHIFT',
    r'\+=': 't_PLUSEQUAL',
    r'\-=': 't_MINEQUAL',
    r'\*=': 't_STAREQUAL',
    r'/=': 't_SLASHEQUAL',
    r'%=': 't_PERCENTEQUAL',
    r'//': 't_SLASHSLASH',
    r'\|\|': 't_VVBAR'
}

# all 1 length spacial character as meta1dict
meta1dict = {
    r':': 't_COLON',
    r',': 't_COMMA',
    r';': 't_SEMI',
    r'\+': 't_PLUS',
    r'\-': 't_MINUS',
    r'\*': 't_STAR',
    r'/': 't_SLASH',
    r'\|': 't_VBAR',
    r'&': 't_AMPER',
    r'<': 't_LESS',
    r'>': 't_GREATER',
    r'=': 't_EQUAL',
    r'\.': 't_DOT',
    r'%': 't_PERCENT',
    r'#': 't_HASH',
    r'\(': 't_LPAREN',
    r'\)': 't_RPAREN',
    r'\{': 't_LBRACE',
    r'\}': 't_RBRACE',
    r'\[': 't_LSQB',
    r'\]': 't_RSQB',
    r'[?]': 't_QUESTION'
}
# something more regex
extradict = {
    r'[A-Za-z_][A-Za-z_0-9]*': 't_ID',
    r'[0-9]+[A-Za-z_][A-Za-z_0-9]*': 't_WRONGID',
    r'\d+(\.\d*)?': 't_NUMBER',
    '\n': 't_NEWLINE',
    r'[ \t]+': 't_SKIP',
    r'.': 't_MISMATCH'
}

#  global variable tokdict to store all dictionary with key as regex and value as token_type
tokdict = {}
tokdict.update(headerfiledict)
tokdict.update(meta2dict)
tokdict.update(meta1dict)
tokdict.update(extradict)

# ---- all ERROR/SUCCESS MESSAGE in msglist
msglist = []

# -----------------------------------------------
#       tokenize function
#       return all Token
# -----------------------------------------------

# global variable to store every line of code
codelines = [None]


def tokenize(file_path, tokdict):
    # global headerfilelist
    global codelines
    with open(file_path, 'r') as f:
        print("\n_____________Tokenize started in source program____________\n")
        code = ""
        for line in f:
            codelines.append(line)
            code = code + line
        # print(code)
        codelines.append("END")
        # -------------------remove comment-------------------------
        comment_regex = '|'.join('(?P<%s>%s)' % (value, key) for key, value in commentdict.items())
        # print(comment_regex)
        match = re.compile(comment_regex, re.MULTILINE | re.DOTALL)
        if match:
            print("\n___________Removing all comment in source program____________\n")
        for m in match.finditer(code):
            replace_comment = list(code[m.span()[0]:m.span()[1]])
            # print('replace_comment===befor:\n', ''.join(c for c in replace_comment))
            for i in range(len(replace_comment)):
                if replace_comment[i] != '\n':
                    replace_comment[i] = ' '
            # print('replace_comment===after:\n', ''.join(c for c in replace_comment))
            code = code[:m.span()[0]] + ''.join(c for c in replace_comment) + code[m.span()[1]:]
        # print("================modified code===========================\n", code)

        # --------------- tokenize --------------------------------------
        tok_regex = '|'.join('(?P<%s>%s)' % (value, key) for key, value in tokdict.items())
        # print(tok_regex)
        line_num = 1
        line_start = 0
        for m in re.finditer(tok_regex, code):
            kind = m.lastgroup
            value = m.group(kind)
            if kind == 't_NEWLINE':
                value = r'\n'
                # calculate column
                column = m.start() - line_start

                line_start = m.end()
                line_num += 1
                # add in Token list
                yield Token(kind, value, line_num, column)
            elif kind == 't_SKIP':
                pass
            elif kind == "t_WRONGID":
                yield Token(kind, value, line_num, column)
                # msglist.append(('error', None, "Invalid ID"))

            elif kind == 't_MISMATCH':
                # raise RuntimeError(f'{value!r} unexpected on line {line_num}')
                yield Token(kind, value, line_num, column)
            else:
                if kind == 't_ID' and value in keywordlist:
                    kind = 't_{}'.format(value.upper())
                elif kind == 't_HEADER' and value not in headerfilelist:
                    kind = 't_MISMATCH'
                    # raise RuntimeError(f'{value!r} unexpected on line {line_num}')
                column = m.start() - line_start
                yield Token(kind, value, line_num, column)
        print("\n_____________Tokenize complete in source program____________\n")


# ------------------------------------------------------------
#           HELPER FUNCTIONS
#
# -------------------------------------------------------------

# NEXT LINE'S INDEX function
def f_nextline(ind):
    '''return next line's first index'''
    while ind < len(toklist) and toklist[ind][0] != 't_NEWLINE':
        ind += 1
    if ind < len(toklist) - 1:
        ind + 1
    return ind


# Index of 'tok' token in current line
def f_tokindof(tok, ind):
    line = get_linetoks(ind)
    m = re.compile(tok).search(line)
    if m:
        pos = len(re.findall('t_', line[:m.end()]))
        if pos != 0:
            ind = ind + pos - 1
    # print(toklist[ind][0], " at index ", ind)
    return ind


# get all tokens in a line
def get_linetoks(ind):
    '''return all tokens in current line'''
    i = ind
    line = ''
    while i < len(toklist) and toklist[i][0] != 't_NEWLINE':
        line += toklist[i][0]
        i += 1
    return line


# Compiled Message function
def compile_message(msglist):
    '''Show message'''
    count_main = 0
    count_warning = 0
    count_error = 0
    for status, ind, msg in msglist:
        if(ind >= len(toklist) or ind < 0):
            continue
        if status.lower() == 'error':
            count_error += 1
            msg = f"ERROR !!! - at line -> {toklist[ind][2]} :\n\t{codelines[toklist[ind][2]]}\n \t{' '*toklist[ind][3]}^\t {msg}\n"
        elif status.lower() == 'ok':
            msg = f"OK - {msg} at line -> {toklist[ind][2]} :\n\t{codelines[toklist[ind][2]]}\n"
        else:
            if status == "okmain":
                count_main += 1
            elif status.lower() == 'warning':
                count_warning += 1
            if count_main > 1:
                count_error += 1
                status = 'error'
                msg = f'DUPLICATE MAIN FUNCTION (found multiple times -{count_main})'
            msg = f"{status.upper()} - at line -> {toklist[ind][2]} :\n\t{codelines[toklist[ind][2]]}\n \t{' '*toklist[ind][3]}^\t {msg}\n"
            if status.lower() == 'okmain' and count_main == 1:
                msg = f"{status.upper()} - at line -> {toklist[ind][2]} :\n\t{codelines[toklist[ind][2]]}\n"

        print(msg, end='\n')
    # if count_main == 0:
    #     msg = "ERROR !!! MAIN FUNCTION NOT FOUND"
    #     print(msg)

    msg = f"\n\n\n_______COMPILATION FINISHED : {count_error} ERROR(S) and {count_warning} WARNING(S)._______\n"
    print(msg)


# Expression
def f_exp(op="exp"):
    '''expression check
        optional parameter: op: "binary","assignment","conditional"
        default op="exp"
    '''
    # print(op)
    binary_oparator = "t_PLUS|t_MINUS|t_STAR|t_SLASH"
    oparand = "t_NUMBER|t_ID"
    incrementdecrement_op = f"(({oparand})(t_INCREMENT|t_DECREMENT))"
    binary_op = f"({oparand})({binary_oparator})({oparand})"
    binary_op = f"({binary_op}{binary_oparator}{binary_op})*"
    assignment_op = f"(t_ID)(t_EQUAL)(t_NUMBER|t_ID|{binary_op})"
    conditional_op = f"(t_NUMBER|t_ID)(t_LESS|t_LESSEQUAL|t_EQEQUAL|t_GREATER|t_GREATEREQUAL)(t_NUMBER|t_ID)"
    if op == 'binary':
        f_regex = binary_op
        # print(f_regex)
    elif op == "assignment":
        f_regex = assignment_op
    elif op == "conditional":
        f_regex = conditional_op
    elif op == "incrementdecrement":
        f_regex = incrementdecrement_op
    else:
        regex_list = [
            incrementdecrement_op,
            assignment_op,
            binary_op,
            conditional_op,
            f"(t_ID)",
            f"(t_NUMBER)"
        ]
        f_regex = '|'.join(item for item in regex_list)

    return f_regex


# INCLUDE SECTION
def f_include():
    '''include section'''
    f_regex = f"(t_HASH)[\s]*(t_INCLUDE)[\s]*(t_LESS)(t_HEADER)(t_GREATER)"
    return f_regex


# FOR LOOP
def f_for():
    '''for loop'''
    f_regex = f"(t_FOR)(t_LPAREN)({f_exp()})?(t_SEMI)({f_exp()})?(t_SEMI)({f_exp()})?(t_RPAREN)"
    return f_regex


# WHILE LOOP
def f_while():
    '''while loop'''
    f_regex = f"(t_WHILE)(t_LPAREN)({f_exp()})(t_RPAREN)"
    return f_regex


# IF STATEMENT
def f_if():
    '''if statement'''
    f_regex = f"(t_IF)(t_LPAREN)({f_exp()})+(t_RPAREN)"
    return f_regex


# ELSE STATEMENT
def f_else():
    '''else statement'''
    f_regex = f"(t_ELSE)"
    return f_regex


# SCOPE of C programe will be process here
def f_scope(ind):
    '''check { body } as scope. Using recursive function'''
    # print("SCOP START (tok=", toklist[ind][0], ") line:", codelines[toklist[ind][2]])
    codetoks = ''.join(tok[0] for tok in toklist[ind:])

    # calculate csope
    lind = ind
    rind = ind + 1
    while lind < rind:
        lm = re.compile('t_LBRACE').search(codetoks, lind)
        rm = re.compile('t_RBRACE').search(codetoks, rind)
        if lm:
            if rm is None:
                msglist.append(('error', ind, "'}' BRACE is missing after current '{'"))
                return ind
            # elif lm.end() > rm.end():
            #     msglist.append(('error', ind, "'}' BRACE is missing after current '{'"))
            #     return ind
            else:
                lind = lm.end()
                rind = rm.end()
        else:
            if rm:
                rind = rm.end()
            break
    scopetoks = codetoks[:rind]
    ntok = len(re.findall('(t_)', scopetoks))
    # scope_end is the index of last token in current scope- '}'
    scope_end = ntok + ind
    ind += 1
    # print("CODE in this scop (tok=", toklist[ind][0], ") line:\n",
    #       codelines[toklist[ind][2]:toklist[scope_end][2]])

    datatype = f"t_INT|t_CHAR|t_FLOAT|t_DOUBLE"
    var_defination = f"({datatype})(t_ID)({f_exp(op='binary')})?((t_COMMA)(t_ID)({f_exp(op='binary')})?)*(t_SEMI)"

    # body of scope {body} will be process here
    while ind < scope_end:
        if toklist[ind][0] == 't_NEWLINE':
            ind += 1
        elif toklist[ind][0] == 't_FOR':
            match = re.match(f_for(), get_linetoks(ind))
            if match is None:
                msglist.append(('error', ind, "FOR_LOOP_section"))
                ind = f_nextline(ind)
            else:
                msglist.append(('ok', ind, "FOR_LOOP_section"))
                ind += len(re.findall('t_', match.group(0)))
                if toklist[ind][0] == 't_LBRACE':
                    ind = f_scope(ind) + 1
                elif toklist[ind][0] == 't_NEWLINE':
                    ind += 1
                    if toklist[ind][0] == "t_LBRACE":
                        ind = f_scope(ind) + 1
                    else:
                        # that means one_line_scope
                        pass
            continue
        elif toklist[ind][0] == 't_WHILE':
            match = re.match(f_while(), get_linetoks(ind))
            if match is None:
                msglist.append(('error', ind, "WHILE_LOOP_section"))
                ind = f_nextline(ind)
            else:
                msglist.append(('ok', ind, "WHILE_LOOP_section"))
                ind = f_nextline(ind)
            continue
        elif toklist[ind][0] == 't_IF':
            match = re.match(f_if(), get_linetoks(ind))
            if match is None:
                msglist.append(('error', ind, "IF_section"))
                ind = f_nextline(ind)
            else:
                msglist.append(('ok', ind, "IF_section"))
                ind = f_nextline(ind)
            continue
        elif toklist[ind][0] == 't_ELSE':
            if not (toklist[ind - 2][0] == 't_RBRACE' or toklist[ind - 2][0] == 't_NEWLINE'):
                msglist.append(('warning', ind, "Note:ELSE_statement always following by IF_statement."))
            match = re.match(f_else(), get_linetoks(ind))
            if match is None:
                msglist.append(('error', ind, "ELSE_statement"))
                ind = f_nextline(ind)
            else:
                msglist.append(('ok', ind, "ELSE_statement"))
                ind = f_nextline(ind)
            continue
        elif re.match(datatype, toklist[ind][0]):
            if re.match(var_defination, get_linetoks(ind)):
                ind = f_tokindof('t_SEMI', ind)
                msglist.append(('ok', ind, "Variable Declaration"))
            else:
                msglist.append(('error', ind, "Invalid Variable Declaration"))
                ind = f_nextline(ind)
        elif toklist[ind][0] == 't_ID':
            # assignment operation
            if re.match(f_exp(op="assignment"), get_linetoks(ind)):
                msglist.append(('ok', ind, "Assignment statement"))
                ind = f_tokindof('t_SEMI', ind)
            elif re.match(f_exp(op='incrementdecrement'), get_linetoks(ind)):
                msglist.append(('ok', ind, "increment/decrement statement"))
                ind = f_tokindof('t_SEMI', ind)

        elif toklist[ind][0] == 't_WRONGID':
            msglist.append(('error', ind, "Wrong ID"))
        elif toklist[ind][0] == 't_MISMATCH':
            msglist.append(('error', ind, "Unknown Token"))
        else:
            ind = f_nextline(ind)
    # print("SCOPE END HERE (tok=", toklist[ind][0], ") line:", codelines[toklist[ind][2]])
    return ind


def displaymatch(match):
    if match is None:
        return None
    return '<Match: %r, groups=%r>' % (match.group(), match.groups())


# -----------------------------------------------------------
#               GENERATE TOKEN
#               STORE TOKEN IN CSV FILE
# -----------------------------------------------------------
# ----all Token in toklist variable-----------
toklist = []
for token in tokenize(file_path=file_path, tokdict=tokdict):
    toklist.append(token)
    # print(tuple(token))
    # print(token[0], token[1], token[2], token[3],sep='\t')

# ---Store all Token in 'new_symbol_table.csv' file----
with open('symbol_table.csv', 'w') as myFile:
    writer = csv.writer(myFile)
    csv_data = [['type', 'value', 'line', 'column']] + toklist
    writer.writerows(csv_data)


# -------------------------------------------------------------
#           SYNTAX ANALYSIS
#   Syntax analysis according to C language and
#   show error message if vailate grammer og C language
# -------------------------------------------------------------
print("\n_____________SYNTAX ANALYSIS Process Started ___________________________\n")
ind = 0
while ind < len(toklist):
    # include section
    if toklist[ind][0] == 't_HASH':
        match = re.compile(f_include()).match(get_linetoks(ind))
        if match is None:
            msglist.append(('error', ind, "Invalid INCLUDE_section"))
            ind = f_nextline(ind)
        else:
            msglist.append(('ok', ind, "INCLUDE section"))
            ind = f_nextline(ind)
        continue
    elif toklist[ind][0] == 't_NEWLINE':
        ind += 1
    # MAIN FUNCTION section
    elif ''.join(t[0] for t in toklist[ind:ind + 4]) == 't_INTt_MAINt_LPARENt_RPAREN':
        ind += 4
        if toklist[ind][0] == 't_LBRACE':
            ind = f_scope(ind) + 1
        elif toklist[ind][0] == 't_NEWLINE':
            ind += 1
            if toklist[ind][0] == "t_LBRACE":
                ind = f_scope(ind) + 1
            else:
                msglist.append(('error', ind, "Expected '{' after MAIN() FUNCTION"))
        msglist.append(('okmain', ind - 1, "MAIN function"))

    else:
        msglist.append(('ERROR', ind, "UNEXPECTED LINE .. Out of MAIN FUNCTION"))
        ind = f_nextline(ind)
print("\n____________ SYNTAX ANALYSIS Process Ended______________________________\n")

print("\n_____________Showing COMPILING Message _________________________________\n")
compile_message(msglist)
