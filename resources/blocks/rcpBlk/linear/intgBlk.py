from supsisim.RCPblk import RCPblk
from scipy import size

class IntegralBlk(RCPblk):

    def MdlFunctions(self,mdlflags,data):
        self.addFunction(data,'integral',"""
        void integral(int Flag, python_block *block)
        {
            double * realPar = block->realPar;
            double *y;

            double h = realPar[0];
            double *U = block->u[0];

            switch(Flag){
            case CG_OUT:
                y = (double *) block->y[0];
                y[0] = realPar[1];
                break;

            case CG_STUPD:
                /* Runga Kutta */
                realPar[1] = realPar[1] + U[0]*h;
                break;
            case CG_INIT:
            case CG_END:
                break;
            default:
                break;
            }
        }
        """)

def intgBlk(pin,pout,X0=0.0):
    """ 

    Continous integral block

    Call: intgBlk(pin,pout,X0)

    Parameters
    ----------
       pin: connected input port(s)
       pout: connected output port(s)
       X0 : Initial conditions

    Returns
    -------
        blk  : RCPblk

    """
    
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)

    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = IntegralBlk('integral',pin,pout,[1,0],0,[0.0 ,X0],[])
    return blk

