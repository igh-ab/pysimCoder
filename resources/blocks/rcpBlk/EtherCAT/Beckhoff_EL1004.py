from supsisim.RCPblk import RCPblk
from scipy import size
from EtherCAT.EtherCAT import EtherCATBlk

class Beckhoff_EL1004_Blk(EtherCATBlk):

    def MdlDeclerations(self,mdlflags,data):
        super().MdlDeclerations(mdlflags,data)
        data.append(
        "static ec_pdo_entry_info_t "+self.cleanName()+"}_el1004_pdo_entries[] = {\n"+
        "{0x3101, 1, 1}, // channel 1 value\n"+
        "{0x3102, 1, 1}, // channel 2 value\n"+
        "{0x3103, 1, 1}, // channel 3 value\n"+
        "{0x3104, 1, 1}, // channel 4 value\n"+
        "};")
        data.append(
        "static ec_pdo_info_t "+self.cleanName()+"_el1004_pdos[] = {\n"+
        "{0x1A00, 4, "+self.cleanName()+"_el1004_pdo_entries},\n"+
        "};")
        data.append(
        "static ec_sync_info_t "+self.getSlaveSyncIdent()+"[] = {\n+
        "{2, EC_DIR_OUTPUT},\n"+
        "{3, EC_DIR_INPUT, 2, "+self.cleanName()+"_el1004_pdos},\n"+
        "{0xff}\n"+
        "};")
        self.addToList(data,"static unsigned int "+self.getSlaveOffsetIdent()+"[4];")
        self.addToList(data,"static unsigned int "+self.getSlaveBitOffsetIdent()+"[4];")


    def MdlDeclerationsFinal(self,mdlflags,data):


    def MdlStart(self,mdlflags,data):
        super().MdlStart(mdlflags,data)
        self.configPDOs(data)

    def MdlFunctions(self,mdlflags,data):
        if 'beckhoff_el1004' in data:
            return
        data['beckhoff_el1004']="""
        void beckhoff_el1004(int Flag, python_block *block)
        {
        }
        """


def beckhoff_el1004_blk(pout,masterid,alias,position):
    
    if(size(pout) != 4):
        raise ValueError("Block should have 4 output port; received %i." % size(pout))
    blk = Beckhoff_EL1004_Blk('beckhoff_el1004',[],pout,[],[],[],[])
    blk.setSlaveIdent('Beckhoff_EL1004',0x2,0x001,masterid,alias,position)
    return blk

