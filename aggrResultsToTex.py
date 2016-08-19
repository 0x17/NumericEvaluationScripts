import openpyxl

NUM_METHODS = 14
REPR_NAMES = ['x_{jt}', '(\\lambda)', '(\\lambda|\\beta)', '(\\lambda|\\tau)', '(\\lambda|\\tilde{\\tau})',
              '(\\lambda|z_r)', '(\\lambda|z_{rt})']
SEP = ' & '
NA = ' - '
NEXTLINE = "\\\\ \n \\hline \n"

mapLSIndex = {0: 3, 1: 0, 2: 1, 3: 2, 4: 4, 5: 5}
mapGAIndex = {0: 4, 1: 0, 2: 1, 4: 2, 5: 3}


def spit(fn, s):
    with open(fn, 'w') as fp: fp.write(s)


def generateOutStr(title, content):
    outStr = """
    \\begin{tabular}{ccccc}
    \\hline
    TITLE & GUROBI & LocalSolver & GA & B\\&B\\\\
    \\hline
    CONTENT
    \\end{tabular}
    """.replace('TITLE', title).replace('CONTENT', content)
    return outStr;


def decorate(v, inv=False):
    def col(c, s):
        return '\\textcolor{' + c + '}{' + s + '}'

    if v > 1.0:
        v = 1.0
    elif v < 0.0:
        v = 0.0
    vs = ("%.2f" % (v * 100.0)) + '\\%'
    if inv:
        if v <= 0.1:
            return col('darkred', vs)
        elif v <= 0.4:
            return col('darkyellow', vs)
        else:
            return col('darkgreen', vs)
    else:
        if v <= 0.1:
            return col('darkgreen', vs)
        elif v <= 0.4:
            return col('darkyellow', vs)
        else:
            return col('darkred', vs)


def generateContent(title, sheet):
    content = ""
    methNameToVal = {}
    for i in range(NUM_METHODS):
        colChar = chr(ord('B') + i)
        methNameToVal[sheet[colChar + '2'].value] = sheet[colChar + '3'].value

    doinv = title == '\\%BKS'
    content += '$' + REPR_NAMES[0] + '$' + SEP + decorate(methNameToVal['GMS_Gurobi_'], doinv) + SEP + decorate(
        methNameToVal['LocalSolver'], doinv) + SEP + NA + SEP + NA + NEXTLINE
    for i in range(len(REPR_NAMES) - 1):
        bbStr = decorate(methNameToVal['BranchAndBound'], doinv) if i == 3 else NA
        gaStr = decorate(methNameToVal['GA' + str(mapGAIndex[i])], doinv) if i != 3 else NA
        content += '$' + REPR_NAMES[i + 1] + '$' + SEP + NA + SEP + decorate(
            methNameToVal['LocalSolverNative' + str(mapLSIndex[i])], doinv) + SEP + gaStr + SEP + bbStr + NEXTLINE

    return content


wb = openpyxl.load_workbook(filename='EvalVBA.xlsm')
titleSheets = {'$\\varnothing$Gap': wb['Avg Gaps'], 'Max Gap': wb['Max Gaps'], '\\%BKS': wb['Perc BKS']}

ix = 0
for title, sheet in titleSheets.iteritems():
    spit('result_tables_' + str(ix) + '.tex', generateOutStr(title, generateContent(title, sheet)))
    ix += 1
