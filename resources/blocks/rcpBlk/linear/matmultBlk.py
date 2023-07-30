from supsisim.RCPblk import RCPblk
from control import tf2ss, TransferFunction
from scipy import shape, size, mat
from numpy import reshape

from linear.matSupportFunction import addMatMult

class MatMultBlk(RCPblk):

    def MdlFunctions(self,mdlflags,data):
        addMatMult(mdlflags,data)
        if 'mxmult' in data:
            return
        data['mxmult']="""
        void mxmult(int Flag, python_block *block)
        {

            /* blk = RCPblk('mxmult',pin,pout,0,realPar,[n,m]) */

            int i;
            double *y;
            double *u;

            int nin = block->intPar[1];
            int nout = block->intPar[0];
            double tmpY[nout];
            double tmpU[nin];

            double * gain = block->realPar;

            switch(Flag){
            case CG_OUT:
            case CG_INIT:
            case CG_END:
                for (i=0; i<nin; i++) {
                u = block->u[i];
                tmpU[i]=u[0];
                }
                matmult(gain,nout,nin,tmpU,nin,1,tmpY);
                for(i=0; i<nout; i++){
                y = block->y[i];
                y[0] = tmpY[i];
                }
                break;
            default:
                break;
            }
        }
        """

def matmultBlk(pin, pout, Gains):
    """

    Matrix multiplication of the input signals
    
    Call: matmultBlk(pin,pout, Gains)

    Parameters
    ----------
       pin: connected input port(s)
       pout: connected output port(s)
       Gains : Gains

    Returns
    -------
        blk  : RCPblk

    """
    
    Gains = mat(Gains)
    n,m = shape(Gains)
    if(size(pin) != m):
        raise ValueError("Block should have %i input port; received %i." % (m,size(pin)))
    if(size(pout) != n):
        raise ValueError("Block should have %i output port; received %i." % (n,size(pout)))
    realPar  = reshape(Gains,(1,size(Gains)),'C')
    blk = MatMultBlk('mxmult',pin,pout,[0,0],1,realPar,[n,m])
    return blk

