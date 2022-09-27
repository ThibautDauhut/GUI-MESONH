Options_init = {
#            - 'divskeys':{}, 'divsvalues':{} doivent Ãªtre des dics nuls (sont remplis par la suite)
#            - len(catName) must be == len(divName). empty name for catName is possible
#            - 'name' is the latex user's guide convention with \_
#            - len(buttonName) must be == len(divName) + 1 (with the first button = the general id button name for the sidebar
#            - empty name for buttonName is possible
'TURBn': {'name': 'NAM\_TURBn', 'model': 'mesonh',
        'catName': ['GÃ©nÃ©ral','Subgrid condensation','Online diagnostics'],
        'buttonName': ['NAMTURBn','NAMTURBngeneral','NAMTURBnsbg','NAMTURBndiag'],
        'divName': ['NAMTURBngeneral','NAMTURBnsbg','NAMTURBndiag'],
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
'PARAMn': {'name': 'NAM\_PARAMn', 'model': 'mesonh',
       'catName': [''],
       'buttonName': ['NAMPARAMn','NAMPARAMngeneral'],
       'divName': ['NAMPARAMngeneral'],
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
                'CCLOUD':{'type':'C','def':'NONE', 'cat': 0,
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

def lookfor_namelist_name(i):
# Look for all the namelist defined in the fortran code by 'NAMELIST/' from a file that contains a grep in folder MNH/ and SURFEX/
    s_after_fortranname = i[i.index('NAMELIST/')+9:]
    namelist = s_after_fortranname[:s_after_fortranname.index('/')]
    return namelist

def get_all_namelists():
    fin = open('NAMELIST_MNH.txt', 'r')
    contentbyline = fin.readlines()
    namelists_MNH,f90files_MNH,namelists_SURFEX,f90files_SURFEX=[],[],[],[]
    for i in contentbyline:
        f90files_MNH.append(i[:i.index('.f90') + 4])
        namelists_MNH.append(lookfor_namelist_name(i))
    
    fin = open('NAMELIST_SURFEX.txt', 'r')
    contentbyline = fin.readlines()
    for i in contentbyline:
        f90files_SURFEX.append(i[:i.index('.F90') + 4])
        namelists_SURFEX.append(lookfor_namelist_name(i))
    return namelists_MNH,f90files_MNH,namelists_SURFEX,f90files_SURFEX

def get_string_keysvalues(options):
    # Fill Options values for string type keys
    fin = open('MNH/read_exsegn.f90','r')
    contentbyline = fin.readlines()
    for i in contentbyline:
        if 'CALL TEST_NAM_VAR' in i:
            # Coder récupération de la clé remplie + des valeurs 
            # Puis boucler sur toutes les namelists et params; si une des clé matchs, on remplit
            
def get_default_inf90(options,nam,key):
    fin = open('MNH/default_desfmn.f90', 'r')
    contentbyline = fin.readlines()
    contentbyline_afterheader = contentbyline[330:]
    keyegal = key + '='
    val = ''
    print(keyegal)
    for i in contentbyline_afterheader:
        i=i.replace(' ','')
        if keyegal == i[:len(keyegal)]:
            try:
                lookforcommentary = i.index('!')
                val = i[len(keyegal):lookforcommentary]
            except(ValueError):
                val = i[len(keyegal):]
            #Control on val
            if 'FALSE' in val:
                val = 'False'
            elif 'TRUE' in val:
                val = 'True'
            elif '\'' in val: # String found
                val = val
            else:
                try: # if number (real or int)
                    val = float(val)
                except:
                    pass
            break
    # If not found in default_desfmn, look into f90file of namelist definition
    if val == '':
        print(key + ' not found, look into from90 = ',options[nam]['fromf90'])
        fin = open('MNH/'+options[nam]['fromf90'], 'r')
        contentbyline = fin.readlines()
        for i in contentbyline:
            i=i.replace(' ','')
            if keyegal == i[:len(keyegal)]:
                try:
                    lookforcommentary = i.index('!')
                    val = i[len(keyegal):lookforcommentary]
                except(ValueError):
                    val = i[len(keyegal):]
                #Control on val
                if 'FALSE' in val:
                    val = 'False'
                elif 'TRUE' in val:
                    val = 'True'
                elif '\'' in val: # String found
                    val = val
                else:
                    try: # if number (real or int)
                        val = float(val)
                    except:
                        pass
                break    
    return val

def get_default_values(options):
    for nam in options.keys():
            for k in options[nam]['keys']:
                if options[nam]['keys'][k]['def'] == '': # if the default value is not already filled, fill in it
                    if options[nam]['model'] == 'mesonh':
                        options[nam]['keys'][k]['def'] = get_default_inf90(options,nam,k)
                    else: #surfex, TODO
                        break
    return options

def get_keys_types(options):
    for nam in options.keys():
            for k in options[nam]['keys']:
                try:
                    options[nam]['keys'][k]['type']
                except(KeyError): # if the type is not already filled, fill in it
                    if k[0] == 'X' or k[0] == 'N' : # real of integer
                        options[nam]['keys'][k]['type'] = 'Input'
                        options[nam]['keys'][k]['min'] = ''
                        options[nam]['keys'][k]['max'] = ''
                    else: # Logical or String
                        options[nam]['keys'][k]['type'] = k[0] # C or L
    return options

def init_all_options(options, namelists, f90files):
    models = ['mesonh','surfex']
    for m,model in enumerate(models):
        for i,nam in enumerate(namelists[m]):
            shortName = nam[4:]
            modelName = model
            name = nam.replace('_','\_')
            from_f90 = f90files[m][i]
            try:
                options[shortName]
            except(KeyError):
                options[shortName] = {}
                options[shortName]['model'] = modelName
                options[shortName]['name'] = name
                options[shortName]['fromf90'] = from_f90
                options[shortName]['keys'] = {}
                options[shortName]['catName'] = ['']
                options[shortName]['buttonName'] = ['NAM'+shortName,'NAM'+shortName+'general'] # [Bouton general de la sidebar, ' Boutton du div general = 1 subdiv par defaut ']
                options[shortName]['divName'] = ['NAM'+shortName+'general']
                options[shortName]['divskeys'], options[shortName]['divsvalues'], options[shortName]['mainDiv'] = {}, {}, {}
    return options

def find_keys_fromf90lines(lines):
# Returns a list of all keys name given a list of lines read from f90 files
    Lkeys=[]
    for l in lines:
        Lkeys.append(l.split(','))
    Lkeys_flat = [x for xs in Lkeys for x in xs] #Flatten list of list into a list
    Lkeys = [x for x in Lkeys_flat if x] # Remove empty object
    return Lkeys

def get_all_keys(options):
    for nam in options.keys():
        if options[nam]['keys'] == {}: # For namelists not filled by hand (still empty)
            if options[nam]['model'] == 'mesonh':
                fin = open('MNH/' + options[nam]['fromf90'], 'r')
            else: 
                fin = open('SURFEX/' + options[nam]['fromf90'], 'r')
            contentbyline = fin.readlines()
            lines_withkeys = []
            found = False
            for i in contentbyline:
                if not found:
                    if 'NAMELIST/'+options[nam]['name'].replace('\_','_') in i:
                        found = True
                        lines_withkeys.append(i)
                else:
                    if '&' in i:
                        lines_withkeys.append(i)
                    else:
                        break
            lines_withkeys[0] = lines_withkeys[0].replace('NAMELIST/'+options[nam]['name'].replace('\_','_')+'/','')
            for n,i in enumerate(lines_withkeys):
                lines_withkeys[n] = lines_withkeys[n].replace('&','')
                lines_withkeys[n] = lines_withkeys[n].replace('\n','')
                lines_withkeys[n] = lines_withkeys[n].replace(' ','')
            Lkeys=find_keys_fromf90lines(lines_withkeys)
            # Add the keys to the main Dict
            if options[nam]['model'] == 'mesonh':
                for k in Lkeys:
                    options[nam]['keys'][k] = {}
                    options[nam]['keys'][k]['cat'] = 0 #Init all keys in cat 0
                    options[nam]['keys'][k]['options'] = []
                    options[nam]['keys'][k]['def'] = ''
            else:
                break
    return options
def create_options():
    #Options filled by hand
    Options = Options_init
    
    # Get all namelists names and fill the dict
    print("Get all namelists names and fill the dict")
    namelists_MNH, f90files_MNH, namelists_SURFEX, f90files_SURFEX = get_all_namelists()
    Options = init_all_options(Options, [namelists_MNH, namelists_SURFEX] , [f90files_MNH, f90files_SURFEX])
    
    # Set all keys for all namelists
    print("Set all keys for all namelists")
    Options = get_all_keys(Options)

    # Get Default values
    print("Get Default values")
    Options = get_default_values(Options)
    
    # Set keys types
    print("Set keys types")
    Options = get_keys_types(Options)
    
    #TODO  Get possible values for strings keys
    #Options = get_string_keysvalues(Options)
    
    # Set particular values
    Options['PARAM_KAFRn']['keys']['XDTCONV']['def'] = 300.0 # The true default value in mesonh code is MAX(300,XTSTEP)
    
    # Selection of specific namelist (for testing)
    Namelists_toshow = ('PARAMn','TURBn','PARAM_LIMA','PARAM_ICE','PARAM_RADn','PARAM_ECRADn',
    'PARAM_C2R2','PARAM_MFSHALLn','PARAM_KAFRn')
    Options_selected = {k:Options[k] for k in Namelists_toshow if k in Options}
    #Options_selected = Options
    return Options_selected
