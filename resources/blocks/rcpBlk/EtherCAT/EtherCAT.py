from supsisim.RCPblk import RCPblk


class EtherCATBlk(RCPblk):
    self.master_id = -1
    self.position = -1
    self.alias = -1

    def MdlFlags(self,data):
        if not "ETHERCAT_MASTER_LIST" in data.keys():
            data["ETHERCAT_MASTER_LIST"]=list()
        if not self.master_id in data["ETHERCAT_MASTER_LIST"]:
            data["ETHERCAT_MASTER_LIST"].append(self.master_id)

    def MdlIncludes(self,mdlflags, data):
        self.addToList(data,'#include<ecrt.h>')

    def MdlLibraries(self,mdlflags,data):
        self.addToList(data,'-lethercat')

    def MdlDeclerations(self,mdlflags,data):
        if not "ETHERCAT_MASTER_DATA_PTR" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,"static ec_master_t *"+self.getMasterIdent(id)+"=NULL;")
                self.addToList(data,"static ec_domain_t *"+self.getDomainIdent(id)+"=NULL;")
                self.addToList(data,"static unit8_t *"+self.getDomainDataIdent(id)+"=NULL;")

            mdlflags["ETHERCAT_MASTER_DATA_PTR"]=True

    def setMaster(self, masterid)
        self.master_id = masterid

    def setAlias(self,alias):
        self.alias = alias

    def setPosition(self,position):
        self.position = position

    def getMasterIdent(self,masterid):
        return "ethercat_master_"+str(masterid)

    def getDomainIdent(self,masterid):
        return "ethercat_domain_"+str(masterid)

    def getDomainDataIdent(self,masterid):
        return "ethercat_domain_data_ptr_"+str(masterid)

    def MdlEnd(self,mdlflags,data):
        if not "ETHERCAT_MASTER_END" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"ecrt_release_master({self.getMasterIdent(id)});")
            mdlflags["ETHERCAT_MASTER_END"]=True

    def MdlStart(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"{self.getMasterIdent(id)} = ecrt_request_master({id});")
                self.addToList(data,f"if (!{sel.getMasterIdent(id)}) {return -1;}")
                self.addToList(data,f"{self.getDomainIdent(id)} = ecrt_master_create_domain({self.getMasterIdent(id)});")
                self.addToList(data,f"if (!{self.getDomainIdent(id)}) {return -1;}")
            mdlflags["ETHERCAT_MASTER_START"]=True

    def MdlStartFinal(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START_FINAL" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addToList(data,f"if (ecrt_master_activate({self.getMasterIdent(id)})){return -1;}")
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
