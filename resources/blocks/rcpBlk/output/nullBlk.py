
from supsisim.RCPblk import RCPblk
from scipy import size

class NullBlk(RCPblk):

   def MdlFunctions(self,mdlflags,data):
      self.addFunction(data,'toNull',"""
      void toNull(int flag, python_block *block)
      {
      }
      """)

def nullBlk(pin):
    """

    Call:   nullBlk(pin)

    Parameters
    ----------
       pin: connected input port(s)

    Returns
    -------
       blk: RCPblk

    """

    blk = NullBlk('toNull', pin, [], [0,0], 1, [], [])
    return blk
