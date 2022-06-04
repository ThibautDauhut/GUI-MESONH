Options_init = {
#            - 'divskeys':{}, 'divsvalues':{} doivent être des dics nuls (sont remplis par la suite)
#            - len(catName) must be == len(divName). empty name for catName is possible
#            - 'name' is the latex user's guide convention with \_
#            - len(buttonName) must be == len(divName) + 1 (with the first button = the general id button name for the sidebar
#            - empty name for buttonName is possible
'TURBn': {'name': 'NAM\_TURBn',
        'catName': ['Général','Subgrid condensation','Online diagnostics'],
        'buttonName': ['NAMTURB','NAMTURBgeneral','NAMTURBsbg','NAMTURBdiag'],
        'divName': ['NAMTURBgeneral','NAMTURBsbg','NAMTURBdiag'],
        'divskeys':{}, 'divsvalues':{}, 'mainDiv':{},
        'keys':{
                'XIMPL':{'type':'Input','min': 0, 'max': 1, 'cat': 0, 'def': 1},
                'CTURBLEN':{'type':'C', 'def':'BL89', 'cat': 0,
                            'options': [{"label": "BL89", "value": "BL89"},
                                        {"label": "RM17", "value": "RM17"},
                                        {"label": "ADAP", "value": "ADAP"},
                                        {"label": "DEAR", "value": "DEAR"},
                                        {"label": "DELT", "value": "DELT"}]},
                'CTOM':{'type':'C', 'def':'NONE', 'cat': 0,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "TM06", "value": "TM06"}]},
                'LRMC01':{'type':'L', 'def': 'False', 'cat': 0},
                'XKEMIN':{'type':'Input','min': 0, 'max': 10, 'cat': 0, 'def': 0.01},
                'XCEDIS':{'type':'Input','min': 0, 'max': 10, 'cat': 0, 'def': 0.84},
                'LSUBG_COND':{'type':'L', 'def': 'False', 'cat': 1},
                'CCONDENS':{'type':'C', 'def':'CB02', 'cat': 1,
                            'options': [{"label": "CB02", "value": "CB02"},
                                        {"label": "GAUS", "value": "GAUS"}]},
                'CLAMBDA3':{'type':'C', 'def':'CB', 'cat': 1,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "CB", "value": "CB"}]},
                'CSUBG_AUCV':{'type':'C', 'def':'NONE', 'cat': 1,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "SIGM", "value": "SIGM"},
                                        {"label": "CLFR", "value": "CLFR"},
                                        {"label": "PDF", "value": "PDF"},
                                        {"label": "ADJU", "value": "ADJU"}]},
                'CSUBG_AUCV_RI':{'type':'C', 'def':'NONE', 'cat': 1,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "CLFR", "value": "CLFR"},
                                        {"label": "ADJU", "value": "ADJU"}]},
                'CSUBG_MF_PDF':{'type':'C', 'def':'TRIANGLE', 'cat': 1,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "TRIANGLE", "value": "TRIANGLE"}]},
                'LTURB_FLX':{'type':'L', 'def': 'False', 'cat': 2},
                'LTURB_DIAG':{'type':'L', 'def': 'False', 'cat': 2},
                }
        },
'PARAMn': {'name': 'NAM\_PARAMn',
	   'catName': [''],
	   'buttonName': ['NAMPARAM',''],
	   'divName': ['NAMPARAMgeneral'],
           'divskeys':{}, 'divsvalues':{}, 'mainDiv':{},
        'keys':{
                'CTURB':{'type':'C', 'def':'TKEL', 'cat': 0,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "TKEL", "value": "TKEL"}]},
                'CRAD':{'type':'C', 'def':'ECMW', 'cat': 0,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "TOPA", "value": "TOPA"},
                                        {"label": "FIXE", "value": "FIXE"},
                                        {"label": "ECMW", "value": "ECMW"},
                                        {"label": "ECRAD", "value": "ECRAD"}]},
                'CCLOUD':{'type':'C','def':'ICE3', 'cat': 0,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "REVE", "value": "REVE"},
                                        {"label": "KESS", "value": "KESS"},
                                        {"label": "C2R2", "value": "C2R2"},
                                        {"label": "KHKO", "value": "KHKO"},
                                        {"label": "ICE3", "value": "IEC3"},
                                        {"label": "ICE4", "value": "ICE4"},
                                        {"label": "LIMA", "value": "LIMA"}]},
                'CDCONV':{'type':'C', 'def':'NONE', 'cat': 0,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "EDKF", "value": "EDKF"}]},
                'CSCONV':{'type':'C', 'def':'EDKF', 'cat': 0,
                            'options': [{"label": "NONE", "value": "NONE"},
                                        {"label": "KAFR", "value": "KAFR"},
                                        {"label": "EDKF", "value": "EDKF"}] }
                }
        }
}

def get_keys_types(options):
	for nam in options.keys():
        	for k in options[nam]['keys']:
        		try:
        			options[nam]['keys'][k]['type']
        		except(KeyError): # if the type is not already filled, fill in it
        			if k[0] == 'X' or k[0] == 'N' : # real of integer
        				options[nam]['keys'][k]['type'] = 'Input'
        			else: # Logical or String
        				options[nam]['keys'][k]['type'] = k[0] # C or L
	return options

def create_options():
	Options = Options_init
	Options = get_keys_types(Options)
	print(Options['PARAMn']['keys']['CCLOUD']['type'])
	return Options
