
from supsisim.RCPblk import RCPblk
from scipy import size

def microrosBlk(pin, pout, pub, subs):
    """

    Call:   MICROROSBlk(pin, pout, pub, subs)

    Parameters
    ----------
       pin: connected input port(s)
       pout: connected output port(s)
       pub : Publisher topic
       subs : Subscriber topic

    Returns
    -------
       blk: RCPblk

    """

    nin = size(pin)
    nout = size(pout)
    
    if (nin > 4):
        raise ValueError("Block have max 4 inputs: received %i input ports" % (nin))
    if (nout > 4):
        raise ValueError("Block have max 4 outputs: received %i output ports" % (nout))
    
    n = len(pub)
    
    blk = RCPblk('microros', pin, pout, [0,0], 0, [], [n], pub+subs)
    return blk
