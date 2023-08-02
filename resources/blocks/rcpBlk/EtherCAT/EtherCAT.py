from supsisim.RCPblk import RCPblk

class EtherCATBlk(RCPblk):
    slave_type = ""
    vendor = -1
    product = -1
    master_id = -1
    position = -1
    alias = -1

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
                data.append("static ec_master_t *"+self.getMasterIdent(id)+"=NULL;\n")
                data.append("static ec_domain_t *"+self.getDomainIdent(id)+"=NULL;\n")
                data.append("static uint8_t *"+self.getDomainDataIdent(id)+"=NULL;\n")
            mdlflags["ETHERCAT_MASTER_DATA_PTR"]=True
        data.append("static ec_slave_config_t *"+self.getSlaveConfigIdent()+" = NULL;\n")

    def MdlDeclerationsFinal(self,mdlflags,data):
        if "ETHERCAT_DOMAINREG" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_DOMAINREG"].keys():
                data.append("const static ec_pdo_entry_reg_t "+self.getDomainRegsIdent(id)+"[] = {\n")
                n = len(mdlflags["ETHERCAT_DOMAINREG"][id])
                for idx in range(0,n-1):
                    entry = mdlflags["ETHERCAT_DOMAINREG"][id][idx]
                    data.append(entry+",\n")
                entry = mdlflags["ETHERCAT_DOMAINREG"][id][n-1]
                data.append(entry+"\n")
                data.append("};\n\n")

    def getMasterIdent(self,masterid):
        return "ethercat_master_"+str(masterid)

    def getDomainIdent(self,masterid):
        return "ethercat_domain_"+str(masterid)

    def getDomainDataIdent(self,masterid):
        return "ethercat_domain_data_ptr_"+str(masterid)

    def getDomainRegsIdent(self,masterid):
        return "ethercat_domain_regs_"+str(masterid)

    def getSlaveConfigIdent(self):
        return "ethercat_slave_config_"+self.cleanName()

    def getSlaveSyncIdent(self):
        return "ethercat_syncs_"+self.cleanName()

    def getSlaveOffsetIdent(self):
        return "ethercat_offsets_"+self.cleanName()

    def getSlaveBitOffsetIdent(self):
        return "ethercat_bit_offsets_"+self.cleanName()

    def getDataOffset(self,idx):
        return self.getDomainDataIdent(self.master_id)+"+"+self.getSlaveOffsetIdent()+"["+str(idx)+"]"

    def getDataBitOffset(self,idx):
        return self.getSlaveBitOffsetIdent()+"["+str(idx)+"]"

    def configPDOs(self,data):
        data.append(
        "    if (!("+self.getSlaveConfigIdent()+" = ecrt_master_slave_config(\n"+
        "        "+self.getMasterIdent(self.master_id)+", \n"+
        "        "+str(self.alias)+", \n"+
        "        "+str(self.position)+", \n"+
        "        "+hex(self.vendor)+", \n"+
        "        "+hex(self.product)+"))) {\n"+
        "       fprintf(stderr, \""+self.name+": Failed to get slave configuration.\\n\");\n"+
        "       return -1;\n"+ 
        "    }\n\n"+
        "    if (ecrt_slave_config_pdos("+self.getSlaveConfigIdent()+", \n"+
        "            EC_END, "+self.getSlaveSyncIdent()+")) {\n"+
        "       fprintf(stderr, \""+self.name+": Failed to configure PDOs.\\n\");\n"+
        "       return -1;\n"+
        "    }\n\n")


    def MdlEnd(self,mdlflags,data):
        if not "ETHERCAT_MASTER_END" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                data.append(f"ecrt_release_master({self.getMasterIdent(id)});\n")
            mdlflags["ETHERCAT_MASTER_END"]=True

    def MdlStart(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                data.append(f"{self.getMasterIdent(id)} = ecrt_request_master({id});\n")
                data.append("if (!"+self.getMasterIdent(id)+") {fprintf(stderr,\"Failed to request master.\");return -1;}\n")
                data.append(f"{self.getDomainIdent(id)} = ecrt_master_create_domain({self.getMasterIdent(id)});\n")
                data.append("if (!"+self.getDomainIdent(id)+") {fprintf(stderr,\"Failed to create domain.\");return -1;}\n")
            mdlflags["ETHERCAT_MASTER_START"]=True

    def MdlStartFinal(self,mdlflags,data):
        if not "ETHERCAT_MASTER_START_FINAL" in mdlflags.keys():
            if "ETHERCAT_DOMAINREG" in mdlflags.keys():
                for id in mdlflags["ETHERCAT_DOMAINREG"].keys():
                    data.append("if (ecrt_domain_reg_pdo_entry_list("+self.getDomainIdent(id)+", "+self.getDomainRegsIdent(id)+")) {\n")
                    data.append("    fprintf(stderr, \"PDO entry registration failed!\\n\");\n")
                    data.append("    return -1;\n")
                    data.append("}\n\n")

            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                data.append("if (ecrt_master_activate("+self.getMasterIdent(id)+")){\n")
                data.append("    fprintf(stderr,\"Failed to activate master.\");\n")
                data.append("    return -1;\n")
                data.append("}\n\n")
                data.append("if (!("+self.getDomainDataIdent(id)+" = ecrt_domain_data("+self.getDomainIdent(id)+"))){\n")
                data.append("    return -1;\n")
                data.append("}\n\n")
            mdlflags["ETHERCAT_MASTER_START_FINAL"]=True

    def MdlRunPre(self,mdlflags,data):
        if not "ETHERCAT_MASTER_RUN_PRE" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                data.append(f"ecrt_master_receive({self.getMasterIdent(id)});\n")
                data.append(f"ecrt_domain_process({self.getDomainIdent(id)});\n")
            mdlflags["ETHERCAT_MASTER_RUN_PRE"]=True

    def MdlRunPost(self,mdlflags,data):
        if not "ETHERCAT_MASTER_RUN_POST" in mdlflags.keys():
            for id in mdlflags["ETHERCAT_MASTER_LIST"]:
                data.append(f"ecrt_domain_queue({self.getDomainIdent(id)});\n")
                data.append(f"ecrt_master_send({self.getMasterIdent(id)});\n")
            mdlflags["ETHERCAT_MASTER_RUN_POST"]=True
