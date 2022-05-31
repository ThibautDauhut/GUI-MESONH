from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import styles as sty
from read_tex import KEYdoc

def create_Cgrp(options, idname, defaultvalue):
    group =  dbc.Container(
            [dbc.RadioItems(
            options=options,
            id=idname,
            labelClassName="date-group-labels",
            labelCheckedClassName="date-group-labels-checked",
            className="date-group-items",
            inline=True,
            value=defaultvalue)], style={'padding':0})
    return group

def create_Lgrp(idname, defaultvalue):
    group = dbc.Container(
            [dbc.RadioItems(
            options=[
                {"label": "True", "value": "True"},
                {"label": "False", "value": "False"},
            ],
            id=idname,
            labelClassName="date-group-labels",
            labelCheckedClassName="date-group-labels-checked",
            className="date-group-items",
            inline=True,
            value=defaultvalue),
            ], style={'padding':0})
    return group

def create_subDiv(DNamelist,icat):
# Function that creates the sub Div for the 'cat' number icat of DNamelist
    contentdiv=[]
    for k in DNamelist['keys'].keys():
        if DNamelist['keys'][k]['cat'] == icat:
            contentdiv.append(html.Label(k, id=k+'labdoc'))
            contentdiv.append(html.Br())
    return html.Div(children=contentdiv,style=sty.STYLE_KEYS)
    
def create_subDivvalues(DNamelist,icat):
# Function that creates the sub Div values for the 'cat' number icat of DNamelist
    contentdiv=[]
    for k in DNamelist['keys'].keys():
        if DNamelist['keys'][k]['cat'] == icat:
            if DNamelist['keys'][k]['type'] == 'Input':
                contentdiv.append(dbc.Input(type="number", min=DNamelist['keys'][k]['min'], max=DNamelist['keys'][k]['max'], 
                style={'width':'18%','font-size':'9pt'}, value=DNamelist['keys'][k]['def'], id=k+'-sel'))
            elif DNamelist['keys'][k]['type'] == 'L':
                contentdiv.append(create_Lgrp(k+'-sel',DNamelist['keys'][k]['def']))
            elif DNamelist['keys'][k]['type'] == 'C':
                contentdiv.append(create_Cgrp(DNamelist['keys'][k]['options'], k+'-sel',DNamelist['keys'][k]['def']))
            else:
            	pass
    contentdiv.append(html.Hr()) # Last ligne is a full line
    return html.Div(children=contentdiv)

def create_KeyValuesDiv(DNamelist):
# Function that creates the main Div keys + values

    # Creates first keys divs and values divs à la volée and save it to Options dict
    for n,div in enumerate(DNamelist['divName']):
        print(div)
        DNamelist['divskeys'][div] = create_subDiv(DNamelist, n)
        DNamelist['divsvalues'][div] = create_subDivvalues(DNamelist, n)

    # Loop on each key-values divs pairs
    contentdiv=[html.H5('&'+DNamelist['name'].replace('\_','_'),style=sty.TEXT_STYLE),]
    for n,div in enumerate(DNamelist['divName']):
        contentdiv.append(html.H6(DNamelist['catName'][n],style=sty.TEXT_STYLE,id=DNamelist['buttonName'][n+1]+'-button'))
        contentdiv.append(dbc.Collapse(
        			html.Div([DNamelist['divskeys'][div],DNamelist['divsvalues'][div]],style=sty.STYLE1),
        			id=div,
        			is_open=True))
    collapse_general = dbc.Collapse(contentdiv, id=DNamelist['buttonName'][0], is_open=True)
    return html.Div(children=collapse_general, style=sty.STYLE_NAMELIST)


Options = {
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
                'CCLOUD':{'type':'C', 'def':'ICE3', 'cat': 0,
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

# Create key-values namelist divs list
all_namelistdivs=[]
for opt in Options.keys():
	Options[opt]['mainDiv'] = create_KeyValuesDiv(Options[opt])
	all_namelistdivs.append(Options[opt]['mainDiv'])

# Particular settings
Options['PARAMn']['divskeys']['NAMPARAMgeneral'].children.insert(5,html.Br())

# Keys-value div
col_allNamelists = html.Div(children=all_namelistdivs,style=sty.STYLE_COL_NAMELISTS)

# Documentation div
col_doc =  html.Div(id='container-userguide',style=sty.DOC_STYLE)

# Sidebar div
sidebar = html.Div([
        html.H2('Namelist groups', style=sty.TEXT_STYLE),
        html.Hr(),
        html.H4('&NAM_PARAMn',style=sty.TEXT_STYLE, id='NAMPARAM-button'),
        html.H4('&NAM_TURBn',style=sty.TEXT_STYLE, id='NAMTURB-button'),
    ],style=sty.SIDEBAR_STYLE)

# Upper static div
LineTopStatic = html.Div([
    html.Div(children=[
    html.H4('Keys',style=sty.TEXT_STYLE),
    ], style={'padding': 10, 'flex': 1}),
    html.Div(children=[html.Br()
    ], style={'padding': 10, 'flex': 2}),
    html.Div(children=[
        html.H4('User\'s guide',style=sty.TEXT_STYLE),
    ], style={'padding': 10, 'flex': 3})
    ],
    style=sty.CONTENT_STYLE)

generalContent = html.Div(children=[col_allNamelists,col_doc],className='row')
supercontent = html.Div(children=[LineTopStatic,generalContent], style={'width':'100%'})

# Layout Master
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(children=[sidebar,supercontent],className='row')

inputs=[]
suffix_label='labdoc'
# Create the list of Inputs for all labels
for nam in Options.keys():
    for keys in Options[nam]['keys'].keys():
        inputs.append(Input(keys+suffix_label,'n_clicks'))

# Callback qui actualise la documentation (container-userguide)
@app.callback(
    Output('container-userguide', 'children'),
    inputs)
def displayClick(*args):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    #changed_id is a key name + 'labdoc.' + 'n_clicks'
    size_to_remove = len('labdoc') + 1 + len('n_clicks')
    key_triggered = changed_id[:-size_to_remove]
    msg=''
    for nam in Options.keys():
        for keys in Options[nam]['keys'].keys():
    	     if keys == key_triggered:
                 msg = KEYdoc('simulation.tex',Options[nam]['name'],keys.replace('_','\_'))    
                 break
    return html.Div(msg)

# Callback des boutons afficher/cacher les options en namelist
def ButtonNam(nameid):
	@app.callback(
    	Output(nameid, "is_open"),
    	Input(nameid+'-button', "n_clicks"),
    	State(nameid, "is_open"))
    	# Fonction associée au callbak qui change le statut du bouton
	def toggle_collapse(n, is_open):
    		if n:
        		return not is_open
    		return is_open

# Create callbacks for hide/show buttons
for nam in Options.keys():
        for b in Options[nam]['buttonName']:
        	if b != '': # empty buttonName is possible
        		ButtonNam(b)

if __name__ == '__main__':
    app.run_server(debug=True,port='8086')
