from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px

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
    return html.Div(children=contentdiv,style=STYLE_KEYS)
    
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

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '15%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    'border': '0px solid black'
}

DOC_STYLE = {
    'width': '45%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    'border': '0px solid black'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '21%',
    'margin-right': '5%',
    'padding': '20px 10p',
    'display': 'flex',
    'flex-direction': 'row',
    'justify-content': 'right'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970',
}

STYLE1={
	'display': 'flex',
    	'flex-direction': 'row',	 
	'vertical-align': 'top', 
	'margin-left': '10%',
	'border': '0px solid black'
}
STYLE_NAMELIST={
	'width' : '100%',	 
	'vertical-align': 'top', 
	'margin-left': '0%',
	'border': '0px solid pink'
}	
STYLE_COL_NAMELISTS={
	'width' : '40%',	 
	'margin-left': '13%',
	'border': '0px solid pink'
}

STYLE_KEYS={
	'width' : '20%',	 
	'vertical-align': 'top', 
	'margin-left': '0%',
	'border': '0px solid green'
}	

# Listes des boutons afficher/cacher
ButtonNamelists=['NAMTURB','NAMTURBgeneral','NAMTURBsbg','NAMTURBdiag','NAMPARAM']
# Listes des labels documentés
Options = {
'TURBn': {'name': 'NAM\_TURBn',
        'catName': ['Général','Subgrid condensation','Online diagnostics'],
        'buttonName': ['NAMTURB','NAMTURBgeneral','NAMTURBsbg','NAMTURBdiag'],
        'divName': ['NAMTURBgeneral','NAMTURBsbg'],
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
'PARAMn': {'name': 'NAM\_PARAMn','catName': [],'buttonName': ['NAMPARAM'],'divName': [],
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

# TURBn Divs
DivGeneralNAMTURB = create_subDiv(Options['TURBn'],0)
DivSBGNAMTURB =  create_subDiv(Options['TURBn'],1)
DivDiagNAMTURB = create_subDiv(Options['TURBn'],2)

DivGeneralNAMTURBvalues = create_subDivvalues(Options['TURBn'],0)
DivSBGNAMTURBvalues = create_subDivvalues(Options['TURBn'],1)
DivDiagNAMTURBvalues = create_subDivvalues(Options['TURBn'],2)
#Div
col_turbn = html.Div(children=[
	dbc.Collapse([
		html.H5('&NAM_TURBn',style=TEXT_STYLE),
		html.H6('General',style=TEXT_STYLE,id='NAMTURBgeneral-button'),
		dbc.Collapse(
            		html.Div([DivGeneralNAMTURB,DivGeneralNAMTURBvalues],style=STYLE1),
            		id="NAMTURBgeneral",
            		is_open=True,
        		),
		html.H6('Subgrid condensation',style=TEXT_STYLE,id='NAMTURBsbg-button'),
		dbc.Collapse(
            		html.Div([DivSBGNAMTURB,DivSBGNAMTURBvalues],style=STYLE1),
            		id="NAMTURBsbg",
            		is_open=True,
        		),
        	html.H6('Online diagnostics',style=TEXT_STYLE,id='NAMTURBdiag-button'),
		dbc.Collapse(
            		html.Div([DivDiagNAMTURB,DivDiagNAMTURBvalues],style=STYLE1),
            		id="NAMTURBdiag",
            		is_open=True,
        		)],id="NAMTURB",is_open=True)],style=STYLE_NAMELIST)

#PARAMn
DivGeneralNAMPARAM = create_subDiv(Options['PARAMn'],0)
DivGeneralNAMPARAM.children.insert(5,html.Br()) # Add by hand a new return lineS

DivGeneralNAMPARAMvalues = create_subDivvalues(Options['PARAMn'],0)

#3 Automatiser le Div final (peut être + difficile)           
col_paramn = html.Div(children=[dbc.Collapse([
		html.H5('&NAM_PARAMn',style=TEXT_STYLE),
		dbc.Collapse(
            		html.Div([DivGeneralNAMPARAM,DivGeneralNAMPARAMvalues],style=STYLE1),
            		id="NAMPARAMgeneral",
            		is_open=True,
        		)],id="NAMPARAM",is_open=True)],style=STYLE_NAMELIST)

col_allNamelists = html.Div(children=[col_turbn,col_paramn],style=STYLE_COL_NAMELISTS)
col_doc =  html.Div(id='container-userguide',style=DOC_STYLE)

sidebar = html.Div([
        html.H2('Namelist groups', style=TEXT_STYLE),
        html.Hr(),
        html.H4('&NAM_PARAMn',style=TEXT_STYLE, id='NAMPARAM-button'),
        html.H4('&NAM_TURBn',style=TEXT_STYLE, id='NAMTURB-button'),
    ],style=SIDEBAR_STYLE)
    
LineTopStatic = html.Div([
    html.Div(children=[
    html.H4('Keys',style=TEXT_STYLE),
    ], style={'padding': 10, 'flex': 1}),
    html.Div(children=[html.Br()
    ], style={'padding': 10, 'flex': 2}),
    html.Div(children=[
        html.H4('User\'s guide',style=TEXT_STYLE),
    ], style={'padding': 10, 'flex': 3})
    ],
    style=CONTENT_STYLE)

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

# Créations des callbacks boutons
for b in ButtonNamelists:
	ButtonNam(b)

if __name__ == '__main__':
    app.run_server(debug=True,port='8086')
