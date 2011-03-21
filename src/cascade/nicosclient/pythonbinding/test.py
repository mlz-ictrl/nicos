import cascadenicosobj

casc = cascadenicosobj.NicosClient()
casc.connecttohost("cascade7.reseda.frm2",1234)
print("Connected: "+repr(casc.isconnected()))

casc.communicate("CMD_status")
casc.communicate("CMD_start")
casc.communicate("CMD_status")
casc.communicate("CMD_readsram")

casc.disconnect()
