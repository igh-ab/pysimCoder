from supsisim.RCPblk import RCPblk
from scipy import size

class SineBlk(RCPblk):

    def MdlIncludes(self,mdlflags,data):
        self.addToList(data,'#include <math.h>')

    def MdlPredefines(self,mdlflags,data):
        self.addToList(data,'double get_run_time(void);')

    def MdlLibraries(self,mdlflags,data):
        self.addToList(data,'-lm')

    def MdlFunctions(self,mdlflags,data):
        if 'sinus' in data:
            return
        data['sinus']="""
        void sinus(int Flag, python_block *block)
        {
            double t;
            double *y = (double *) block->y[0];

            double w,pi=3.1415927;
            double Amp = block->realPar[0];
            double Freq = block->realPar[1];
            double Phase = block->realPar[2];
            double Bias = block->realPar[3];
            double Delay = block->realPar[4];

            switch(Flag){
                case CG_OUT:
                    t = get_run_time();
                    if(t<Delay) y[0] = 0.0;
                    else {
                        w=2*pi*Freq*(t-Delay)-Phase;
                        y[0]=Amp*sin(w)+Bias;
                    }
                    break;
                case CG_INIT:
                    y[0]=0.0;
                    break;
                case CG_END:
                    y[0]=0.0;
                    break;
                default:
                    break;
            }
        }
        """

def sineBlk(pout, Amp, Freq, Phase, Bias, Delay):
    """

    Call:   sineBlk(pout, Amp, Freq, Phase, Bias, Delay)

    Parameters
    ----------
       pout: connected output port(s)
       Amp : Amplitude
       Freq : Freq
       Phase : Phase
       Bias : Bias
       Delay : Delay

    Returns
    -------
        blk  : RCPblk
    
    """

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = SineBlk('sinus', [],pout,[0,0],0,[Amp, Freq, Phase, Bias, Delay],[])
    return blk

