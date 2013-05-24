import cascadeclient    #pylint: disable=F0401

casc = cascadeclient.NicosClient()
casc.connecttohost("cascade.mira.frm2",1234)
print("Connected: "+repr(casc.isconnected()))

print(casc.communicate("CMD_status"))

casc.disconnect()
