from supsisim.RCPblk import RCPblk

class EtherCATBlk(RCPblk):
    slave_type = ""
    vendor = -1
    product = -1
    master_id = -1
    position = -1
    alias = -1

    def setMaster(self,masterid):
        if(int(masterid) < 0):
            raise ValueError("Master-Id should be >=0; received %i." % int(masterid))
        self.master_id = int(masterid)

    def setSlaveType(self,slave_type):
        self.slave_type = slave_type

    def setVendor(self,vendor):
        if(int(vendor) < 0):
            raise ValueError("vendor should be 0<vendor; received %i." % int(vendor))
        self.vendor = int(vendor)

    def setProduct(self,product):
        if(int(product) < 0):
            raise ValueError("product should be 0<product; received %i." % int(product))
        self.product = int(product)
    
    def setAlias(self,alias):
        if(int(alias) < 0 or int(alias) > 255):
            raise ValueError("Alias should be 0<alias<255; received %i." % int(alias))
        self.alias = int(alias)

    def setPosition(self,position):
        if(int(position) < 0):
            raise ValueError("position should be 0<position; received %i." % int(position))
        self.position = int(position)

    def setSlaveIdent(
        self,
        slave_type,
        vendor,product,
        masterid,
        alias,
        position
        ):
        self.setSlaveType(slave_type)
        self.setVendor(vendor)
        self.setProduct(product)
        self.setMaster(masterid)
        self.setAlias(alias)
        self.setPosition(position)

    def addToDomainReg(self,mdlflags,entryindex,entrysubindex,offsetindex,offsetbitindex):
        if offsetbitindex is not None:
            bitstr = "&"+self.getSlaveBitOffsetIdent()+"["+str(offsetbitindex)+"]"
        else:
            bitstr = "NULL"
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

    def MdlBlockFlags(self,data):
        pass

    def MdlFlags(self,data):
        self.disableFunctionCall()
        if not "ETHERCAT_MASTER_LIST" in data.keys():
            data["ETHERCAT_MASTER_LIST"]=list()
        if not "ETHERCAT_DOMAINREG" in data.keys():
            data["ETHERCAT_DOMAINREG"]=dict()
        if not self.master_id in data["ETHERCAT_MASTER_LIST"]:
            data["ETHERCAT_MASTER_LIST"].append(self.master_id)
        if not self.master_id in data["ETHERCAT_DOMAINREG"].keys():
            data["ETHERCAT_DOMAINREG"][self.master_id]=list()
        self.MdlBlockFlags(data)

    def MdlBlockIncludes(self,mdlflags,data):
        pass

    def MdlIncludes(self,mdlflags, data):
        self.addToList(data,'#include<ecrt.h>')
        self.addToList(data,'#include <stdio.h>')
        self.MdlBlockIncludes(mdlflags,data)

    def MdlBlockLibraries(self,mdlflags,data):
        pass

    def MdlLibraries(self,mdlflags,data):
        self.addToList(data,'-lethercat')
        self.MdlBlockLibraries(mdlflags,data)

    def MdlBlockPredefines(self,mdlflags,data):
        pass

    def MdlPredefines(self,mdlflags,data):
        if not "ETHERCAT_MASTER_PREDEFINES" in mdlflags.keys():
            self.addToList(data,"#define ETHERCAT_TIMESPEC2NS(T) ((uint64_t) (T).tv_sec * (1000000000L) + (T).tv_nsec)")
            mdlflags["ETHERCAT_MASTER_PREDEFINES"]=True
        self.MdlBlockPredefines(mdlflags,data)

    def MdlBlockDeclerations(self,mdlflags,data):
        pass

    def MdlDeclerations(self,mdlflags,data):
        if not "ETHERCAT_MASTER_DATA_PTR" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,"static ec_master_t *"+self.getMasterIdent(id)+"=NULL;\n")
                self.addCode(data,"static ec_domain_t *"+self.getDomainIdent(id)+"=NULL;\n")
                self.addCode(data,"static uint8_t *"+self.getDomainDataIdent(id)+"=NULL;\n")
            mdlflags["ETHERCAT_MASTER_DATA_PTR"]=True
        self.MdlBlockDeclerations(mdlflags,data)

    def MdlBlockDeclerationsFinal(self,mdlflags,data):
        pass

    def MdlDeclerationsFinal(self,mdlflags,data):
        if not "ETHERCAT_DOMAINREG_DONE" in mdlflags.keys():
            if "ETHERCAT_DOMAINREG" in mdlflags.keys():
                for id in mdlflags["ETHERCAT_DOMAINREG"].keys():
                    self.addCode(data,"const static ec_pdo_entry_reg_t "+self.getDomainRegsIdent(id)+"[] = {\n")
                    n = len(mdlflags["ETHERCAT_DOMAINREG"][id])
                    for idx in range(0,n-1):
                        entry = mdlflags["ETHERCAT_DOMAINREG"][id][idx]
                        self.addCode(data,entry+",\n")
                    entry = mdlflags["ETHERCAT_DOMAINREG"][id][n-1]
                    self.addCode(data,entry+"\n")
                    self.addCode(data,"};\n\n")
            mdlflags["ETHERCAT_DOMAINREG_DONE"] = True
        self.MdlBlockDeclerationsFinal(mdlflags,data)

    def getMasterIdent(self,masterid):
        return "mdl_ethercat_master_"+str(masterid)

    def getDomainIdent(self,masterid):
        return "mdl_ethercat_domain_"+str(masterid)

    def getDomainDataIdent(self,masterid):
        return "mdl_ethercat_domain_data_ptr_"+str(masterid)

    def getDomainRegsIdent(self,masterid):
        return "mdl_ethercat_domain_regs_"+str(masterid)

    def getSlaveConfigIdent(self):
        return "mdl_ethercat_slave_config_"+self.cleanName()

    def getSlaveSyncIdent(self):
        return "mdl_ethercat_syncs_"+self.cleanName()

    def getSlaveOffsetIdent(self):
        return "mdl_ethercat_offsets_"+self.cleanName()

    def getSlaveBitOffsetIdent(self):
        return "mdl_ethercat_bit_offsets_"+self.cleanName()

    def getDataOffset(self,idx):
        return self.getDomainDataIdent(self.master_id)+"+"+self.getSlaveOffsetIdent()+"["+str(idx)+"]"

    def getDataBitOffset(self,idx):
        return self.getSlaveBitOffsetIdent()+"["+str(idx)+"]"

    def configPDOs(self,data):
        self.addCode(data,
        "    if (!("+self.getSlaveConfigIdent()+" = ecrt_master_slave_config(\n"+
        "        "+self.getMasterIdent(self.master_id)+", \n"+
        "        "+str(self.alias)+", \n"+
        "        "+str(self.position)+", \n"+
        "        "+hex(self.vendor)+", \n"+
        "        "+hex(self.product)+"))) {\n"+
        "       fprintf(stderr, \""+self.name+": Failed to get slave configuration.\\n\");\n"+
        "       exit(0);\n"+ 
        "    }\n\n"+
        "    if (ecrt_slave_config_pdos("+self.getSlaveConfigIdent()+", \n"+
        "            EC_END, "+self.getSlaveSyncIdent()+")) {\n"+
        "       fprintf(stderr, \""+self.name+": Failed to configure PDOs.\\n\");\n"+
        "       exit(0);\n"+
        "    }\n\n")

    def configDC(self,data):
            ecrt_slave_config_dc(sc, 0x0700, PERIOD_NS, 4400000, 0, 0);

    def MdlBlockFunctions(self,mdlflags,data):
        pass

    def MdlFunctions(self,mdlflags,data):
        self.MdlBlockFunctions(mdlflags,data)

    def MdlBlockEnd(slef,mdlflags,data):
        pass

    def MdlEnd(self,mdlflags,data):
        self.MdlBlockEnd(mdlflags,data)

    def MdlBlockEndFinal(slef,mdlflags,data):
        pass

    def MdlEndFinal(self,mdlflags,data):
        if not "ETHERCAT_MASTER_END" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,f"ecrt_release_master({self.getMasterIdent(id)});\n")
            mdlflags["ETHERCAT_MASTER_END"]=True
        self.MdlBlockEndFinal(mdlflags,data)

    def MdlBlockStartPre(self,mdlflags,data):
        pass

    def MdlStartPre(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,f"{self.getMasterIdent(id)} = ecrt_request_master({id});\n")
                self.addCode(data,"if (!"+self.getMasterIdent(id)+") {fprintf(stderr,\"Failed to request master.\");exit(0);}\n")
                self.addCode(data,f"{self.getDomainIdent(id)} = ecrt_master_create_domain({self.getMasterIdent(id)});\n")
                self.addCode(data,"if (!"+self.getDomainIdent(id)+") {fprintf(stderr,\"Failed to create domain.\");exit(0);}\n")
            mdlflags["ETHERCAT_MASTER_START"]=True
        self.MdlBlockStartPre(mdlflags,data)

    def MdlBlockStart(self,mdlflags,data):
        pass

    def MdlStart(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,f"{self.getMasterIdent(id)} = ecrt_request_master({id});\n")
                self.addCode(data,"if (!"+self.getMasterIdent(id)+") {fprintf(stderr,\"Failed to request master.\");exit(0);}\n")
                self.addCode(data,f"{self.getDomainIdent(id)} = ecrt_master_create_domain({self.getMasterIdent(id)});\n")
                self.addCode(data,"if (!"+self.getDomainIdent(id)+") {fprintf(stderr,\"Failed to create domain.\");exit(0);}\n")
            mdlflags["ETHERCAT_MASTER_START"]=True
        self.MdlBlockStart(mdlflags,data)


    def MdlBlockStartFinal(self,mdlflags,data):
        pass

    def MdlStartFinal(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START_FINAL" in mdlflags.keys():
            if "ETHERCAT_DOMAINREG" in mdlflags.keys():
                for id in mdlflags["ETHERCAT_DOMAINREG"].keys():
                    self.addCode(data,"if (ecrt_domain_reg_pdo_entry_list("+self.getDomainIdent(id)+", "+self.getDomainRegsIdent(id)+")) {\n")
                    self.addCode(data,"    fprintf(stderr, \"PDO entry registration failed!\\n\");\n")
                    self.addCode(data,"    exit(0);\n")
                    self.addCode(data,"}\n\n")

            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,"if (ecrt_master_activate("+self.getMasterIdent(id)+")){\n")
                self.addCode(data,"    fprintf(stderr,\"Failed to activate master.\");\n")
                self.addCode(data,"    exit(0);\n")
                self.addCode(data,"}\n\n")
                self.addCode(data,"if (!("+self.getDomainDataIdent(id)+" = ecrt_domain_data("+self.getDomainIdent(id)+"))){\n")
                self.addCode(data,"    exit(0);\n")
                self.addCode(data,"}\n\n")
            mdlflags["ETHERCAT_MASTER_START_FINAL"]=True
        self.MdlBlockStartFinal(mdlflags,data)

    def MdlBlockRunPre(self,mdlfllags,data):
        pass

    def MdlRunPre(self,mdlflags,data):
        if not "ETHERCAT_MASTER_RUN_PRE" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,f"ecrt_master_application_time(({self.getMasterIdent(id)}, ETHERCAT_TIMESPEC2NS(monotonic_time));\n")
                self.addCode(data,f"ecrt_master_receive({self.getMasterIdent(id)});\n")
                self.addCode(data,f"ecrt_domain_process({self.getDomainIdent(id)});\n")
            mdlflags["ETHERCAT_MASTER_RUN_PRE"]=True
        self.MdlBlockRunPre(mdlflags,data)

    def MdlBlockRun(self,mdlflags,data):
        pass

    def MdlRun(self,mdlflags,data):
        self.MdlBlockRun(mdlflags,data)

    def MdlBlockRunPost(self,mdlflags,data):
        pass

    def MdlRunPost(self,mdlflags,data):
        if not "ETHERCAT_MASTER_RUN_POST" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                self.addCode(data,f"ecrt_master_sync_reference_clock_to({self.getMasterIdent(id)}, ETHERCAT_TIMESPEC2NS(monotonic_time));\n")
                self.addCode(data,f"ecrt_master_sync_slave_clocks({self.getMasterIdent(id)});\n")
                self.addCode(data,f"ecrt_domain_queue({self.getDomainIdent(id)});\n")
                self.addCode(data,f"ecrt_master_send({self.getMasterIdent(id)});\n")
            mdlflags["ETHERCAT_MASTER_RUN_POST"]=True
        self.MdlBlockRunPost(mdlflags,data)

