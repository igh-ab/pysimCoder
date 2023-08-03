"""
This is a procedural interface to the RCPblk library

roberto.bucher@supsi.ch

The following class is provided:

  RCPblk      - class with info for Rapid Controller Prototyping

"""
from numpy import array, ones
import re

class RCPblk:
    def __init__(self, *args):  
        if len(args) == 8:
            (fcn,pin,pout,nx,uy,realPar,intPar,str) = args
        elif len(args) == 7:
            (fcn,pin,pout,nx,uy,realPar,intPar) = args
            str=''
        else:
            raise ValueError("Needs 6 or 7 arguments; received %i." % len(args))
        
        self.name = None
        self.fcn = fcn
        self.pin = array(pin)
        self.pout = array(pout)
        self.dimPin = ones(self.pin.shape)
        self.dimPout = ones(self.pout.shape)
        self.nx = array(nx)
        self.uy = array(uy)
        self.realPar = array(realPar)
        self.realParNames = []
        self.intPar = array(intPar)
        self.intParNames = []
        self.str = str
        self.sysPath = ''
        self.no_fcn_call = False

    def __str__(self):
        """String representation of the Block"""
        str =  "Block Name         : " + self.name.__str__() + "\n"
        str += "Function           : " + self.fcn.__str__() + "\n"
        str += "System path        : " + self.sysPath.__str__() + "\n"
        str += "Input ports        : " + self.pin.__str__() + "\n"
        str += "Output ports      : " + self.pout.__str__() + "\n"
        str += "Input dimensions : " + self.dimPin.__str__() + "\n"
        str += "Output dimensions : " + self.dimPout.__str__() + "\n"
        str += "Nr. of states      : " + self.nx.__str__() + "\n"
        str += "Relation u->y      : " + self.uy.__str__() + "\n"
        str += "Real parameters    : " + self.realPar.__str__() + "\n"
        str += "Names of real parameters : " + self.realParNames.__str__() + "\n"
        str += "Integer parameters : " + self.intPar.__str__() + "\n"
        str += "Names of integer parameters : " + self.intParNames.__str__() + "\n"
        str += "String Parameter   : " + self.str.__str__() + "\n"
        return str

    def genCode(self,codedata,cstate):

        data = codedata[cstate]
        mdlflags = codedata['MdlFlags']

        if cstate == 'MdlFlags':
            self.MdlFlags(data)
        elif cstate == 'MdlCFlags':
            self.MdlCFlags(mdlflags,data)
        elif cstate == 'MdlLibraries':
            self.MdlLibraries(mdlflags,data)
        elif cstate == 'MdlCFiles':
            self.MdlCFiles(mdlflags,data)
        elif cstate == 'MdlIncludes':
            self.MdlIncludes(mdlflags,data)
        elif cstate == 'MdlPredefines':
            self.MdlPredefines(mdlflags,data)
        elif cstate == 'MdlDeclerations':
            self.MdlDeclerations(mdlflags,data)
        elif cstate == 'MdlDeclerationsFinal':
            self.MdlDeclerationsFinal(mdlflags,data)
        elif cstate == 'MdlFunctions':
            self.MdlFunctions(mdlflags,data)
        elif cstate == 'MdlStart':
            self.MdlStart(mdlflags,data)
        elif cstate == 'MdlStartFinal':
            self.MdlStartFinal(mdlflags,data)
        elif cstate == 'MdlEnd':
            self.MdlEnd(mdlflags,data)
        elif cstate == 'MdlRunPre':
            self.MdlRunPre(mdlflags,data)
        elif cstate == 'MdlRunPost':
            self.MdlRunPost(mdlflags,data)
        elif cstate == 'MdlRun':
            self.MdlRun(mdlflags,data)

    def MdlFlags(self,data=dict()):
        """
        Add flags to react on during code generation
        """
        pass

    def MdlCFlags(self,mdlflags,data=list()):
        """
        Add compiler CFlags
        Example: -Wall
        """
        pass
 
    def MdlLibraries(self,mdlflags,data=list()):
        """
        Add compiler linker libraries
        Example: -lm
        """
        pass

    def MdlCFiles(self,mdlflags,data=list()):
        pass

    def MdlIncludes(self,mdlflags,data=list()):
        """
        Add compiler include directives
        Example: #include<math.h>
        """
        pass

    def MdlPredefines(self,mdlflags,data=list()):
        """
        Declare preprocessor defines
        """
        pass

    def MdlDeclerations(self,mdlflags,data=list()):
        """
        Declare global data variables
        """
        pass

    def MdlDeclerationsFinal(self,mdlflags,data=list()):
        """
        Declare global data variables which depend on other global vars
        """
        pass


    def MdlFunctions(self,mdlflags,data=dict()):
        """
        Declare cyclic function call, old code generation style
        """
        pass

    def MdlStart(self,mdlflags,data=list()):
        """
        Initial function calls
        Example: Configure fieldbus
        """
        pass

    def MdlStartFinal(self,mdlflags,data=list()):
        """
        Final code directly before going into cyclic mode
        Example: Activate fieldbus configuration
        """
        pass

    def MdlEnd(self,mdlflags,data=list()):
        """
        Add code to model end section
        Example: Release fieldbus
        """
        pass

    def MdlRunPre(self,mdlflags,data=list()):
        """
        Add code at beginning of cyclic loop
        Example: Recieve fieldbus data
        """
        pass

    def MdlRunPost(self,mdlflags,data=list()):
        """
        Add code to the end of cyclic loop
        Example: Send fieldbus data
        """
        pass

    def MdlRun(self,mdlflags,data=list()):
        """
        Add block specific code to the cyclic loop
        Example: Access fieldbus data 
        """
        pass

    def addToList(self, data, value):
        """
        Add to data list, but check value already exists
        """
        if value in data:
            return
        else:
            data.append(value)

    def disableFunctionCall(self):
        self.no_fcn_call = True

    def isDisabledFunctionCall(self):
        return self.no_fcn_call
        
    def cleanName(self):
        """
        Return a c clean blockname
        """
        return re.sub(r'[^a-zA-Z0-9_]', '', self.name)

    def getBlockCStruct(self):
        """
        Return the pointer to the named point to the python block structure
        """
        return "block_"+self.cleanName()


    def getBlockOutputPtr(self,idx):
        return self.getBlockCStruct()+"->y["+str(idx)+"]"