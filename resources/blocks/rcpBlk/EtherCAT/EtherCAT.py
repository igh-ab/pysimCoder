from supsisim.RCPblk import RCPblk
import re

class EtherCATBlk(RCPblk):
    self.slave_type = ""
    self.vendor = -1
    self.product = -1
    self.master_id = -1
    self.position = -1
    self.alias = -1

    def cleanName(self):
        return re.sub(r'[^a-zA-Z0-9]', '', self.name)

    def setSlaveIdent(
        self,
        slave_type,
        vendor,product,
        masterid,
        alias,
        position
        ):
        self.slave_type = slave_type
        self.vendor = vendor
        self.product = product
        if(int(masterid) < 0):
            raise ValueError("Master-Id should be >=0; received %i." % int(masterid))
        if(int(alias) < 0 or int(alias) > 255):
            raise ValueError("Alias should be 0<alias<255; received %i." % int(alias))
        if(int(position) < 0 or int(position) > 255):
            raise ValueError("position should be 0<position<255; received %i." % int(position))
        self.master_id = int(masterid)
        self.alias = int(alias)
        self.position = int(position)

    def addToDomainReg(self,mdlfags,entryindex,entrysubindex,offsetindex,offsetbitindex);
        bitstr=offsetbitindex in not None?"&"+self.getSlaveBitOffsetIdent()+"["+str(offsetbitindex)+"]":"NULL"
        mdlflags["ETHERCAT_DOMAINREG"][self.master_id].append(
            "{"+str(self.alias)+","+
                str(self.position)+","+
                str(self.vendor)+","+
                str(self.product)+","+
                str(entryindex)+", "+
                str(entrysubindex)+", "+
                "&"+self.getSlaveOffsetIdent()+"["+str(offsetindex)+"],"+
                bitstr+
            "}"
        )

    def MdlFlags(self,data):
        if not "ETHERCAT_MASTER_LIST" in data.keys():
            data["ETHERCAT_MASTER_LIST"]=list()
        if not "ETHERCAT_DOMAINREG" in data.keys():
            data["ETHERCAT_DOMAINREG"]=dict()
        if not self.master_id in data["ETHERCAT_MASTER_LIST"]:
            data["ETHERCAT_MASTER_LIST"].append(self.master_id)
            data["ETHERCAT_DOMAINREG"][self.master_id]=list()

    def MdlIncludes(self,mdlflags, data):
        self.addToList(data,'#include<ecrt.h>')
        self.addToList(data,'#include <stdio.h>')
        
    def MdlLibraries(self,mdlflags,data):
        self.addToList(data,'-lethercat')

    def MdlDeclerations(self,mdlflags,data):
        if not "ETHERCAT_MASTER_DATA_PTR" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,"static ec_master_t *"+self.getMasterIdent(id)+"=NULL;")
                self.addToList(data,"static ec_domain_t *"+self.getDomainIdent(id)+"=NULL;")
                self.addToList(data,"static unit8_t *"+self.getDomainDataIdent(id)+"=NULL;")
            mdlflags["ETHERCAT_MASTER_DATA_PTR"]=True
        self.addToList(data,"static ec_slave_config_t *"+self.getSlaveConfigIdent()+" = NULL;\n"+

    def getMasterIdent(self,masterid):
        return "ethercat_master_"+str(masterid)

    def getDomainIdent(self,masterid):
        return "ethercat_domain_"+str(masterid)

    def getDomainDataIdent(self,masterid):
        return "ethercat_domain_data_ptr_"+str(masterid)

    def getSlaveConfigIdent(self):
        return "ethercat_slave_config_"+self.cleanName()

    def getSlaveSyncIdent(self):
        return "ethercat_syncs_"+self.cleanName()

    def getSlaveOffsetIdent(self):
        return "ethercat_offsets_"+self.cleanName()

    def getSlaveBitOffsetIdent(self):
        return "ethercat_bit_offsets_"+self.cleanName()


    def configPDOs(self,data):
        data.append(
        "    if (!("+self.getSlaveConfigIdent()+" = ecrt_master_slave_config(\n"+
        "        "+self.getMasterIdent(self.master_id)+", \n"+
        "        "+str(self.alias)+", \n"+
        "        "+str(self.position)+", \n"+
        "        "+hex(self.vendor)+", \n"+
        "        "+hex(self.product)+")) {\n"+
        "       fprintf(stderr, \""+self.name+": Failed to get slave configuration.\\n\");\n"+
        "       return -1;\n"+ 
        "    }\n\n"+
        "    if (ecrt_slave_config_pdos("+getSlaveConfigIdent()+", \n"+
        "            EC_END, "+self.getSlaveSyncIdent()+")) {\n"+
        "       fprintf(stderr, \""+self.name+": Failed to configure PDOs.\\n\");\n"+
        "       return -1;\n"+
        "    }\n\n")


    def MdlEnd(self,mdlflags,data):
        if not "ETHERCAT_MASTER_END" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"ecrt_release_master({self.getMasterIdent(id)});")
            mdlflags["ETHERCAT_MASTER_END"]=True

    def MdlStart(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"{self.getMasterIdent(id)} = ecrt_request_master({id});")
                self.addToList(data,"if (!"+sel.getMasterIdent(id)+") {fprintf(stderr,\"Failed to request master.\");return -1;}")
                self.addToList(data,f"{self.getDomainIdent(id)} = ecrt_master_create_domain({self.getMasterIdent(id)});")
                self.addToList(data,"if (!"+self.getDomainIdent(id)+") {fprintf(stderr,\"Failed to create domain.\");return -1;}")
            mdlflags["ETHERCAT_MASTER_START"]=True

    def MdlStartFinal(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START_FINAL" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,"if (ecrt_master_activate("+self.getMasterIdent(id)+")){fprintf(stderr,\"Failed to activate master.\")return -1;}")
                self.addToList(data,f"if (!({self.getDomainDataIdent(id)} = ecrt_domain_data({self.getDomainIdent(id)}))){return -1;}")
            mdlflags["ETHERCAT_MASTER_START_FINAL"]=True

    def MdlRunPre(self,mdlflags,data):
        if not "ETHERCAT_MASTER_RUN_PRE" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"ecrt_master_receive({self.getMasterIdent(id)});")
                self.addToList(data,f"ecrt_domain_process({self.getDomainIdent(id)});")
            mdlflags["ETHERCAT_MASTER_RUN_PRE"]=True

    def MdlRunPost(self,mdlflags,data):
        if not "ETHERCAT_MASTER_RUN_POST" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"ecrt_domain_queque({self.getDomainIdent(id)});")
                self.addToList(data,f"ecrt_master_send({self.getMasterIdent(id)});")
            mdlflags["ETHERCAT_MASTER_RUN_POST"]=True
