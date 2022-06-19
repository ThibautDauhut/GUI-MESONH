from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import styles as sty
import options as opt
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
            bname = DNamelist['name']+k
            contentdiv.append(html.Label(k, id=bname+'labdoc'))
            contentdiv.append(html.Br())
    return html.Div(children=contentdiv,style=sty.STYLE_KEYS)
    
def create_subDivvalues(DNamelist,icat):
# Function that creates the sub Div values for the 'cat' number icat of DNamelist
    contentdiv=[]
    for k in DNamelist['keys'].keys():
        if DNamelist['keys'][k]['cat'] == icat:
            labelName = DNamelist['name']+k
            if DNamelist['keys'][k]['type'] == 'Input':
                contentdiv.append(dbc.Input(type="number", min=DNamelist['keys'][k]['min'], max=DNamelist['keys'][k]['max'], 
                style={'width':'18%','font-size':'9pt'}, value=DNamelist['keys'][k]['def'], id=labelName+'-sel'))
            elif DNamelist['keys'][k]['type'] == 'L':
                contentdiv.append(create_Lgrp(labelName+'-sel',DNamelist['keys'][k]['def']))
            elif DNamelist['keys'][k]['type'] == 'C':
                contentdiv.append(create_Cgrp(DNamelist['keys'][k]['options'], labelName+'-sel',DNamelist['keys'][k]['def']))
            else:
            	pass
    contentdiv.append(html.Hr()) # Last ligne is a full line
    return html.Div(children=contentdiv)

def create_KeyValuesDiv(DNamelist):
# Function that creates the main Div keys + values

    # Creates first keys divs and values divs à la volée and save it to Options dict
    for n,div in enumerate(DNamelist['divName']):
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
    collapse_general = dbc.Collapse(contentdiv, id=DNamelist['buttonName'][0], is_open=False)
    return html.Div(children=collapse_general, style=sty.STYLE_NAMELIST)

#Automatisation :
#2) valeur par défaut : lire default_desfmn.f90
#3) valeur possible pour les chaines de caractères : lire les appels à TEST_NAM_VAR dans read_exsegn
#4) la fonction d'automatisation a en option : la possibilité d'exclure certaines namelists
#5) coder une fonction qui trie les clé namelist dans Options par ordre alphabétique à la fin
#6) Ajouter le ou les sous-programme associés à chaque namelist

# Get the full options dict
Options = opt.create_options()

# Create key-values namelist divs list
all_namelistdivs = []
for opt in Options.keys():
	Options[opt]['mainDiv'] = create_KeyValuesDiv(Options[opt])
	all_namelistdivs.append(Options[opt]['mainDiv'])

# Particular settings
Options['PARAMn']['divskeys']['NAMPARAMngeneral'].children.insert(5,html.Br())

# Keys-value div
col_allNamelists = html.Div(children=all_namelistdivs,style=sty.STYLE_COL_NAMELISTS)

# Documentation div
col_doc =  html.Div(id='container-userguide',style=sty.DOC_STYLE)

# Sidebar div
sidebar_content = []
sidebar_content.append(html.H2('Namelist groups', style=sty.TEXT_STYLE))
sidebar_content.append(html.Hr())
for nam in Options.keys():
	sidebar_content.append(html.H4('&NAM_'+nam, style=sty.TEXT_STYLE, id=Options[nam]['buttonName'][0]+'-button'))
sidebar = html.Div(sidebar_content, style=sty.SIDEBAR_STYLE)

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
        name_label=Options[nam]['name']+keys
        inputs.append(Input(name_label+suffix_label,'n_clicks'))

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
             name_label = Options[nam]['name']+keys
             if name_label == key_triggered:
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
