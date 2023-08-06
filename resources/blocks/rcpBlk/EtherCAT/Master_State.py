from supsisim.RCPblk import RCPblk
from scipy import size
from EtherCAT.EtherCAT import EtherCATBlk

class EtherCAT_Master_State_Blk(EtherCATBlk):

    def MdlBlockStartFinal(self,mdlflags,data):
        for idx in range(0,3):
            self.addCode(data,"((double*)"+self.getBlockOutputPtr(idx)+")[0] = 0.0;\n")

    def MdlBlockRun(self,mdlfags, data):
        self.addCode(data,"{\n")
        self.addCode(data,"   ec_master_state_t ms;\n")
        self.addCode(data,"   ecrt_master_state("+self.getMasterIdent(self.master_id)+", &ms);\n")
        self.addCode(data,"   ((double*)"+self.getBlockOutputPtr(0)+")[0] = (double)ms.slaves_responding;\n")
        self.addCode(data,"   ((double*)"+self.getBlockOutputPtr(1)+")[0] = (double)ms.al_states;\n")        
        self.addCode(data,"   ((double*)"+self.getBlockOutputPtr(2)+")[0] = (double)ms.link_up;\n")        
        self.addCode(data,"}\n")

def ethercat_master_state_blk(pout,masterid):
    
    if(size(pout) != 3):
        raise ValueError("Block should have 3 output port; received %i." % size(pout))
    blk = EtherCAT_Master_State_Blk('ethercat_master_state',[],pout,[0,0],[],[],[])
    blk.setMaster(masterid)
    blk.setSlaveType("Master_State")
    return blk

