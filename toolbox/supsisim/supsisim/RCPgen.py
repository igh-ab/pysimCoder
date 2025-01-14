"""
This is a procedural interface to the RCPblk library

roberto.bucher@supsi.ch

The following class is provided:

  RCPblk      - class with info for Rapid Controller Prototyping

The following commands are provided:

  genCode        - Create  C code from BlockDiagram
  genMake        - Generate the Makefile for the C code
  detBlkSeq      - Get the right block sequence for simulation and RT
  sch2blks       - Generate block list fron schematic
  
"""
from scipy import mat, size, array, zeros
from numpy import  nonzero, ones
from os import environ
import copy
import sys
from supsisim.RCPblk import RCPblk
from supsisim.SHVgen import genSHVtree, genSHVcode, genSHVheader, genSHVend

def initCodeData():
    codedata=dict()
    codedata['MdlFlags'] = dict()
    codedata['MdlCFlags'] = list()
    codedata['MdlLibraries'] = list()
    codedata['MdlCFiles'] = list()
    codedata['MdlIncludes'] = list()
    codedata['MdlPredefines'] = list()
    codedata['MdlDeclerations'] = dict()
    codedata['MdlDeclerationsFinal'] = dict()
    codedata['MdlFunctions'] = dict()
    codedata['MdlStartPre'] = dict()
    codedata['MdlStart'] = dict()
    codedata['MdlStartFinal'] = dict()
    codedata['MdlEnd'] = dict()
    codedata['MdlEndFinal'] = dict()
    codedata['MdlRunPre'] = dict()
    codedata['MdlRunPost'] = dict()
    codedata['MdlRun'] = dict()
    return codedata


def genCode(model, Tsamp, blocks, rkstep = 10):
    """Generate C-Code

    Call: genCode(model, Tsamp, Blocks, rkstep)

    Parameters
    ----------
    model     : Model name
    Tsamp     : Sampling Time
    Blocks    : Block list
    rkstep    : step division pro sample time for fixed step solver

    Returns
    -------
    -
"""

    maxNode = 0
    for blk in blocks:
        for n in range(0,size(blk.pin)):
            if blk.pin[n] > maxNode:
                maxNode = blk.pin[n]
        for n in range(0,size(blk.pout)):
            if blk.pout[n] > maxNode:
                maxNode = blk.pout[n]

    # Check outputs not connected together!
    outnodes = zeros(maxNode+1)
    for blk in blocks:
        for n in range(0,size(blk.pout)):
            if outnodes[blk.pout[n]] == 0:
                outnodes[blk.pout[n]] = 1
            else:
                raise ValueError('Problem in diagram: outputs connected together!')

    Blocks = detBlkSeq(maxNode, blocks)
    if size(Blocks) == 0:
        raise ValueError('No possible to determine the block sequence')

    N = size(Blocks)

    codedata = initCodeData()

    for cstate in codedata.keys():
        for n in range(0,N):
            blk = Blocks[n]
            blk.genCode(codedata,cstate)


    fn = model + '.c'
    f=open(fn,'w')
    strLn = "#include <pyblock.h>\n"
    strLn += "#include <stdio.h>\n"
    strLn += "#include <stdlib.h>\n"
    strLn += "#ifdef PDSERV\n"
    strLn += "#include <pdserv.h>\n\n"
    strLn += "extern struct pdserv* pdserv;\n"
    strLn += "extern struct pdtask* pdtask;\n"
    strLn += "#endif\n\n"
    f.write(strLn)

    f.write("/*Block defined includes*/\n")
    for header in codedata['MdlIncludes']:
        f.write(header+"\n")
       
    f.write("\n/*Block defined predefines*/\n")
    for predef in codedata['MdlPredefines']:
        f.write(predef+"\n")


    # genSHVheader(f, model, N)

    totContBlk = 0
    for blk in Blocks:
        totContBlk += blk.nx[0]

    f.write("\nextern struct timespec monotonic_time;\n\n")

    f.write("\n/*Block global declerations*/\n")
    for n in range(0,N):
        blk = Blocks[n]    
        for line in blk.getCode(codedata['MdlDeclerations']):
            f.write(line)

    for n in range(0,N):
        blk = Blocks[n]    
        for line in blk.getCode(codedata['MdlDeclerationsFinal']):
            f.write(line)


    f.write("\n/*Block defined functions*/\n")
    for func in codedata['MdlFunctions']:
        f.write(codedata['MdlFunctions'][func]+"\n")


    strLn = "double " + model + "_get_tsamp(void)\n"
    strLn += "{\n"
    strLn += "  return (" + str(Tsamp) + ");\n"
    strLn += "}\n\n"
    f.write(strLn)

    strLn = "python_block block_" + model + "[" + str(N) + "];\n\n"
    f.write(strLn)

    strLn = "/* Add named pointers to block structure*/\n"
    for n in range(0,N):
        blk = Blocks[n]    
        strLn += "python_block *"+blk.getBlockCStruct()+" = &block_" + model + "[" + str(n) + "];\n"
    f.write(strLn)
    f.write("\n")


    for n in range(0,N):
        blk = Blocks[n]
        if (size(blk.realPar) != 0):
            strLn = "static double realPar_" + str(n) +"[] = {"
            strLn += str(mat(blk.realPar).tolist())[2:-2] + "};\n"
            strLn += "static char *realParNames_" + str(n) + "[] = {"
            tmp = 0
            if (size(blk.realPar) != size(blk.realParNames)):
                for i in range(0, size(blk.realPar)):
                    strLn += "\"double" + str(i) + "\""
                    if ((tmp + 1) != size(blk.realPar)):
                        strLn += ", "
                    tmp += 1
            else:
                for i in range(0, size(blk.realPar)):
                    strLn += "\"" + str(blk.realParNames[i]) + "\""
                    if ((tmp + 1) != size(blk.realPar)):
                        strLn += ", "
                    tmp += 1
            strLn += "};\n"
            f.write(strLn)
        if (size(blk.intPar) != 0):
            strLn = "static int intPar_" + str(n) +"[] = {"
            strLn += str(mat(blk.intPar).tolist())[2:-2] + "};\n"
            strLn += "static char *intParNames_" + str(n) + "[] = {"
            tmp = 0
            for i in range(0, size(blk.intPar)):
                strLn += "\"int" + str(i) + "\""
                if ((tmp + 1) != size(blk.intPar)):
                    strLn += ", "
                tmp += 1
            strLn += "};\n"
            f.write(strLn)
        strLn = "static int nx_" + str(n) +"[] = {"
        strLn += str(mat(blk.nx).tolist())[2:-2] + "};\n"
        f.write(strLn)
    f.write("\n")

    f.write("/* Nodes */\n")
    for n in range(1,maxNode+1):
        strLn = "static double Node_" + str(n) + "[] = {0.0};\n"
        f.write(strLn)

    f.write("\n")

    f.write("/* Input and outputs */\n")
    for n in range(0,N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)
        if (nin!=0):
            strLn = "static void *inptr_" + str(n) + "[]  = {"
            for m in range(0,nin):
                strLn += "&Node_" + str(blk.pin[m]) + ","
            strLn = strLn[0:-1] + "};\n"
            f.write(strLn)
        if (nout!=0):
            strLn = "static void *outptr_" + str(n) + "[] = {"
            for m in range(0,nout):
                strLn += "&Node_" + str(blk.pout[m]) + ","
            strLn = strLn[0:-1] + "};\n"
            f.write(strLn)

    f.write("\n\n")

    Blks = []
    for n in range(0,N):
        Blks.append(Blocks[n].name)

    BlksOrigin = copy.deepcopy(Blks)
    Blks.sort()

    if (environ["SHV_TREE_TYPE"] == "GSA_STATIC") and (environ["SHV_USED"] == "True"):
        genSHVtree(f, Blocks, Blks)

    f.write("/* Worker funtions */\n\n")
 
    f.write("/* Initialization function */\n\n")
    strLn = "void " + model + "_init(void)\n"
    strLn += "{\n\n"
    f.write(strLn)

    f.write("/* Block definition */\n\n")
    for n in range(0,N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)
        num = 0

        strLn =  "  block_" + model + "[" + str(n) + "].nin  = " + str(nin) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].nout = " + str(nout) + ";\n"

        port = "nx_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].nx   = " + port + ";\n"

        if (nin == 0):
            port = "NULL"
        else:
            port = "inptr_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].u    = " + port + ";\n"
        if (nout == 0):
            port = "NULL"
        else:
            port = "outptr_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].y    = " + port + ";\n"
        strLn += "#ifdef PDSERV\n"
        for outs in range(0,nout):
            strLn += "  pdserv_signal(pdtask, 1, \"" + blk.sysPath + "/" + str(outs) + "\",pd_double_T,(double*)block_" + model + "[" + str(n) + "].y["+ str(outs) +"], 1, 0);\n"
        strLn += "#endif\n"
        if (size(blk.realPar) != 0):
            par = "realPar_" + str(n)
            parNames = "realParNames_" + str(n)
            num = size(blk.realPar)
        else:
            par = "NULL"
            parNames = "NULL"
            num = 0
        strLn += "  block_" + model + "[" + str(n) + "].realPar = " + par + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].realParNum = " + str(num) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].realParNames = " + parNames + ";\n"
        if num > 0:
            strLn += "#ifdef PDSERV\n"
            for reals in range(0,num):
                strLn += "  pdserv_parameter(pdserv, \"" + blk.sysPath + "/" + blk.realParNames[reals]+"\", 0666, pd_double_T, &block_" + model + "[" + str(n) + "].realPar["+str(reals)+"], 1, 0, 0, 0);\n"
            strLn += "#endif\n"
        if (size(blk.intPar) != 0):
            par = "intPar_" + str(n)
            parNames = "intParNames_" + str(n)
            num = size(blk.intPar)
        else:
            par = "NULL"
            parNames = "NULL"
            num = 0
        strLn += "  block_" + model + "[" + str(n) + "].intPar = " + par + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].intParNum = " + str(num) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].intParNames = " + parNames + ";\n"
        if num > 0 and size(blk.intParNames) == num:
            strLn += "#ifdef PDSERV\n"
            print(blk)
            for ints in range(0,num):
                strLn += "  pdserv_parameter(pdserv, \"" + blk.sysPath + "/" + blk.intParNames[ints]+"\", 0666, pd_sint_T, &block_" + model + "[" + str(n) + "].intPar["+str(ints) +"], 1, 0, 0, 0);\n"
            strLn += "#endif\n"

        strLn += "  block_" + model + "[" + str(n) + "].str = " +'"' + blk.str + '"' + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].ptrPar = NULL;\n"
        f.write(strLn)
        f.write("\n")
    f.write("\n")

    if environ["SHV_USED"] == "True":
        genSHVcode(f, model, Blocks, Blks)

    f.write("\n\n/*  Start: Model pre start function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        for line in blk.getCode(codedata['MdlStartPre']):
            f.write("  "+line)
    f.write("\n/* End: Model pre start function code */\n\n")


    f.write("\n\n/* Start: Model start function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        if not blk.isDisabledFunctionCall():
            strLn = "  " + blk.fcn + "(CG_INIT, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
        else:
            for line in blk.getCode(codedata['MdlStart']):
                f.write("  "+line)
    f.write("\n/* End: Model start function code */\n\n")


    f.write("\n\n/* Start: Model start final function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        for line in blk.getCode(codedata['MdlStartFinal']):
            f.write("  "+line)
    f.write("\n/* End: Model start final function code */\n\n")


    f.write("}\n\n")

    f.write("/* ISR function */\n\n")
    strLn = "void " + model + "_isr(double t)\n"
    strLn += "{\n"
    f.write(strLn)

    if (totContBlk != 0):
        f.write("int i;\n")
        f.write("double h;\n\n")

    f.write("\n\n/* Start: Model pre run function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        for line in blk.getCode(codedata['MdlRunPre']):
            f.write("  "+line)
    f.write("\n/* End: Model pre run function code */\n\n")


    f.write("\n\n/* Start: Model run function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        if not blk.isDisabledFunctionCall():
            strLn = "  " + blk.fcn + "(CG_OUT, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
        else:
            for line in blk.getCode(codedata['MdlRun']):
                f.write("  "+line)
    f.write("\n/* End: Model run function code */\n\n")


    f.write("\n")

    for n in range(0,N):
        blk = Blocks[n]
        if (blk.nx[1] != 0):
            strLn = "  " + blk.fcn + "(CG_STUPD, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
    f.write("\n")

    f.write("\n\n/* Model subsampling run function code */\n")
    if (totContBlk != 0):
        strLn = "  h = " + model + "_get_tsamp()/" + str(rkstep) + ";\n\n"
        f.write(strLn)

        for n in range(0,N):
            blk = Blocks[n]
            if blk.isDisabledFunctionCall():
                continue
            if (blk.nx[0] != 0):
                strLn = "  block_" + model + "[" + str(n) + "].realPar[0] = h;\n"
                f.write(strLn)

        strLn = "  for(i=0;i<" + str(rkstep) + ";i++){\n"
        f.write(strLn)
        for n in range(0,N):
            blk = Blocks[n]
            if blk.isDisabledFunctionCall():
                continue
            if (blk.nx[0] != 0):
                strLn = "    " + blk.fcn + "(CG_OUT, &block_" + model + "[" + str(n) + "]);\n"
                f.write(strLn)

        for n in range(0,N):
            blk = Blocks[n]
            if blk.isDisabledFunctionCall():
                continue
            if (blk.nx[0] != 0):
                strLn = "    " + blk.fcn + "(CG_STUPD, &block_" + model + "[" + str(n) + "]);\n"
                f.write(strLn)

        f.write("  }\n")

    f.write("\n\n/* Start: Model post run function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        for line in blk.getCode(codedata['MdlRunPost']):
            f.write("  "+line)
    f.write("\n/* End: Model post run function code */\n\n")

    f.write("}\n")

    f.write("/* Termination function */\n\n")

    strLn = "void " + model + "_end(void)\n"
    strLn += "{\n"
    f.write(strLn)

    if environ["SHV_USED"] == "True":
        genSHVend(f, model)

    f.write("\n\n/* Start: Model block end function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        if not blk.isDisabledFunctionCall():
            strLn = "  " + blk.fcn + "(CG_END, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
        else:
            for line in blk.getCode(codedata['MdlEnd']):
                f.write("  "+line)
    f.write("\n/* End: Model end function code */\n\n")


    f.write("\n\n/* Start: Model end final function code */\n")
    for n in range(0,N):
        blk = Blocks[n]
        for line in blk.getCode(codedata['MdlEndFinal']):
            f.write("  "+line)
    f.write("\n/* End: Model end final function code */\n\n")


    f.write("}\n\n")
    f.close()

    return codedata

def genMake(model, template, codedata, addObj = ''):
    """Generate the Makefile

    Call: genMake(model, template, codedata)

    Parameters
    ----------
    model     : Model name
    template  : Template makefile
    codedata  : Code generation data structure
    addObj    : Additional object files

    Returns
    -------
    -
"""
    template_path = environ.get('PYSUPSICTRL')
    fname = template_path + '/CodeGen/templates/' + template
    f = open(fname,'r')
    mf = f.read()
    f.close()
    mf = mf.replace('$$MODEL$$',model)
    addlibs = " ".join(codedata["MdlLibraries"])
    mf = mf.replace('$$ADD_FILES$$',addObj)
    mf = mf.replace('$$ADD_LIBS$$',addlibs)
    f = open('Makefile','w')
    f.write(mf)
    f.close()

def detBlkSeq(Nodes, blocks):
    """Generate the Block sequence for simulation and RT

    Call: detBlkSeq(Nodes, Blocks)

    Parameters
    ----------
    Nodes     : Number of total nodes in diagram
    blocks    : List with the unordered blocks

    Returns
    -------
    Blocks    : List with the ordered blocks

"""
    class blkDep:
        def __init__(self, block, blkL, nodeL):
            self.block = block
            self.block_in = []

            if len(block.pin) != 0:
                for node in block.pin:
                    if nodeL[node].block_in[0].uy == 1:
                        self.block_in.append(nodeL[node].block_in[0])
  

        def __str__(self):
            txt  = 'Block: ' + self.block.fcn.__str__() + '\n'
            txt += 'Inputs\n'
            for item in self.block_in:
                txt += item.fcn + '\n'
            txt += '\n'
            return txt

    class nodeClass:
        def __init__(self, N):
            self.PN = N
            self.block_in = []
            self.block_out = []

        def __str__(self):
            txt  = 'Node: ' + self.PN.__str__() + '\n'
            txt += ' Blocks in:\n'
            for item in self.block_in:
                try:
                    txt += item.fcn + '\n'
                except:
                    txt += 'None\n'
            txt += ' Blocks out:\n'
            for item in self.block_out:
                try:
                    txt += item.fcn + '\n'
                except:
                    txt += 'None\n'
            return txt

    def fillNodeList(nN,blks):
        nL = []
        nL.append(nodeClass(0))
        for n in range(1, nN+1):
            node = nodeClass(n)
            nL.append(node)
        for blk in blks:
            for n in blk.pin:
                nL[n].block_out.append(blk)
            for n in blk.pout:
                nL[n].block_in.append(blk)
        return nL

    blks = []
    blks2order = []

    nodes = fillNodeList(Nodes, blocks)

    # First search block with no input and no output

    for blk in blocks:
        if blk.uy == 0:
            if len(blk.pin) == 0 and len(blk.pout) == 0:
                blks.insert(0, blk)
            else:
                blks.append(blk)
        else:
            block = blkDep(blk, blocks, nodes)
            blks2order.append(block)

    # Order the remaining blocks
    counter = 0
    while len(blks2order) != counter:
        blk = blks2order.pop(0)
        if len(blk.block_in) == 0:
            blks.append(blk.block)
            counter = 0

            try:
                for node in blk.block.pout:
                    for bk in nodes[node].block_out:
                        el=[el for el in blks2order if el.block == bk]
                        try:
                            el[0].block_in.remove(blk.block)
                        except:
                            pass
            except:
                pass
        else:
            blks2order.append(blk)
            counter += 1

    # Check if remain blocks in blks2order -> Algeabric loop!
    if len(blks2order) != 0:
        for item in blks2order:
            print(item.block)
        raise ValueError("Algeabric loop!")

    return blks
