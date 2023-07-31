from supsisim.RCPblk import RCPblk
from scipy import size
from EtherCAT.EtherCAT import EtherCATBlk

class Beckhoff_EL1004_Blk(EtherCATBlk):

    def MdlPredefines(self,mdlflags,data):
        self.addToList(data,"#define Ident_Beckhoff_EL1004 0x00000002, 0x044c2c52")

    def MdlDeclerations(self,mdlflags,data):
        super().MdlDeclerations(mdlflags,data)
        data.append(
        "static ec_pdo_entry_info_t "+self.name+"}_el1004_pdo_entries[] = {\n"+
        "{0x3101, 1, 1}, // channel 1 value\n"+
        "{0x3102, 1, 1}, // channel 2 value\n"+
        "{0x3103, 1, 1}, // channel 3 value\n"+
        "{0x3104, 1, 1}, // channel 4 value\n"+
        "};")
        data.append(
        "static ec_pdo_info_t "+self.name+"_el1004_pdos[] = {\n"+
        "{0x1A00, 4, "+self.name+"_el1004_pdo_entries},\n"+
        "};")
        data.append(
        "static ec_sync_info_t "+self.name+"_el1004_syncs[] = {\n+
        "{2, EC_DIR_OUTPUT},\n"+
        "{3, EC_DIR_INPUT, 2, "+self.name+"_el1004_pdos},\n"+
        "{0xff}\n"+
        "};")

    def MdlStart(self,mdlflags,data):
        super().MdlStart(mdlflags,data)
        data.append(
        "{\n"+
        "    ec_slave_config_t *sc = NULL;\n"+
        "    if (!(sc = ecrt_master_slave_config(\n"+
        "        "+str(self.master_id)+", "+str(self.alias)+", "+str(self.position)+", Ident_Beckhoff_EL4102))) {\n"+
        fprintf(stderr, "Failed to get slave configuration.\n");
        return -1; 
    }

    if (ecrt_slave_config_pdos(sc, EC_END, el4102_syncs)) {
        fprintf(stderr, "Failed to configure PDOs.\n");
        return -1;
    }

"
        "}\n"
        )

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
    if(int(masterid) < 0):
        raise ValueError("Master-Id should be >=0; received %i." % int(masterid))
    if(int(alias) < 0 or int(alias) > 255):
        raise ValueError("Alias should be 0<alias<255; received %i." % int(alias))
    if(int(position) < 0 or int(position) > 255):
        raise ValueError("position should be 0<position<255; received %i." % int(position))
    blk = Beckhoff_EL1004_Blk('beckhoff_el1004',[],pout,[],[],[],[])
    blk.setMaster(int(masterid))
    blk.setAlias(int(alias))
    blk.setPosition(int(position))
    return blk

