from supsisim.RCPblk import RCPblk
from scipy import size
from EtherCAT.EtherCAT import EtherCATBlk

class EtherCAT_Domain_State_Blk(EtherCATBlk):

    def MdlBlockStartFinal(self,mdlflags,data):
        for idx in range(0,3):
            data.append("((double*)"+self.getBlockOutputPtr(idx)+")[0] = 0.0;\n")

    def MdlBlockRun(self,mdlfags, data):
        data.append("{\n")
        data.append("   ec_domain_state_t ds;\n")
        data.append("   ecrt_domain_state("+self.getDomainIdent(self.master_id)+", &ds);\n")
        data.append("   ((double*)"+self.getBlockOutputPtr(0)+")[0] = (double)ds.working_counter;\n")
        data.append("   ((double*)"+self.getBlockOutputPtr(1)+")[0] = (double)ds.wc_state;\n")        
        data.append("   ((double*)"+self.getBlockOutputPtr(2)+")[0] = (double)ds.redundancy_active;\n")        
        data.append("}\n")

def ethercat_domain_state_blk(pout,masterid):
    
    if(size(pout) != 3):
        raise ValueError("Block should have 3 output port; received %i." % size(pout))
    blk = EtherCAT_Domain_State_Blk('ethercat_domain_state',[],pout,[0,0],[],[],[])
    blk.setMaster(masterid)
    blk.setSlaveType("Domain_State")
    return blk

