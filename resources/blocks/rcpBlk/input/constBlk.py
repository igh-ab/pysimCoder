from supsisim.RCPblk import RCPblk
from scipy import size

class ConstBlk(RCPblk):

    def MdlFunctions(self,mdlflags,data):
        self.addFunction(data,'constant',"""
        void constant(int Flag, python_block *block)
        {
            double *y;
  
            y = (double *) block->y[0];

            switch(Flag){
                case CG_OUT:
                case CG_INIT:
                case CG_END:
                    y[0] = block->realPar[0];
                    break;
                default:
                    break;
            }
        }
        """)

def constBlk(pout, val):
    """

    Call:   constBlk(pout, val)

    Parameters
    ----------
       pout: connected output port(s)
       val : Value

    Returns
    -------
    blk  : RCPblk

    """
    
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = ConstBlk('constant',[],pout,[0,0],0,[val],[])
    return blk

