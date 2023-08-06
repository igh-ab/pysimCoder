from supsisim.RCPblk import RCPblk
from scipy import size
from EtherCAT.EtherCAT import EtherCATBlk

class Beckhoff_EL1004_Blk(EtherCATBlk):

    def MdlBlockDeclerations(self,mdlflags,data):
        self.addCode(data,
        "static ec_pdo_entry_info_t "+self.cleanName()+"_el1004_pdo_entries[] = {\n"+
        "{0x3101, 1, 8}, // channel 1 value\n"+
        "{0x3102, 1, 8}, // channel 2 value\n"+
        "{0x3103, 1, 8}, // channel 3 value\n"+
        "{0x3104, 1, 8}, // channel 4 value\n"+
        "};\n")
        self.addCode(data,
        "static ec_pdo_info_t "+self.cleanName()+"_el1004_pdos[] = {\n"+
        "{0x1A00, 4, "+self.cleanName()+"_el1004_pdo_entries},\n"+
        "};\n")
        self.addCode(data,
        "static ec_sync_info_t "+self.getSlaveSyncIdent()+"[] = {\n"+
        "{2, EC_DIR_OUTPUT},\n"+
        "{3, EC_DIR_INPUT, 2, "+self.cleanName()+"_el1004_pdos},\n"+
        "{0xff}\n"+
        "};\n\n")
        self.addCode(data,"static ec_slave_config_t *"+self.getSlaveConfigIdent()+" = NULL;\n")
        self.addCode(data,"static unsigned int "+self.getSlaveOffsetIdent()+"[4];\n")
        self.addCode(data,"static unsigned int "+self.getSlaveBitOffsetIdent()+"[4];\n")

        self.addToDomainReg(mdlflags,0x3101,1,0,0)
        self.addToDomainReg(mdlflags,0x3102,1,1,1)
        self.addToDomainReg(mdlflags,0x3103,1,2,2)
        self.addToDomainReg(mdlflags,0x3104,1,3,3)

    def MdlBlockStart(self,mdlflags,data):
        self.configPDOs(data)

    def MdlBlockStartFinal(self,mdlflags,data):
        for idx in range(0,4):
            self.addCode(data,"((double*)"+self.getBlockOutputPtr(idx)+")[0] = 0.0;\n")

    def MdlBlockRun(self,mdlfags, data):
        for idx in range(0,4):
            self.addCode(data,
                "((double*)"+self.getBlockOutputPtr(idx)+")[0] = (double)EC_READ_BIT("+
                self.getDataOffset(idx)+", "+
                self.getDataBitOffset(idx)+");\n")        


def beckhoff_el1004_blk(pout,masterid,alias,position):
    
    if(size(pout) != 4):
        raise ValueError("Block should have 4 output port; received %i." % size(pout))
    blk = Beckhoff_EL1004_Blk('beckhoff_el1004',[],pout,[0,0],[],[],[])
    blk.setSlaveIdent('Beckhoff_EL1004',0x2,0x001,masterid,alias,position)
    return blk

