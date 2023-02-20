from dash import html
# enlever l'argument fromFile et lister tous les .tex dispo et ajouter une boucle si non trouvé dans un .tex, faire les suivants : et vérifier si pas trop long
def KEYdoc(fromFile, namelistgrp, key):
	fin = open(fromFile, 'r')
	contentbyline = fin.readlines()
	ncurrline = 0
	NAM=namelistgrp
	NAMfound=False
	
	def check_for_last_i_ofNAM(i):
		if '\index{NAM\_' in i:
			return i
		else: 
			return '0'
	# Look for start and end line with description of NAM
	for i in contentbyline:
		ncurrline+=1
		if NAMfound:
			last_i_ofNAM=check_for_last_i_ofNAM(i)
			if last_i_ofNAM != '0':
				last_i_ofNAM=ncurrline
				break
		if not NAMfound and '\index{'+NAM in i:
			first_i_ofNAM=ncurrline
			NAMfound=True
	
	ncurrline=first_i_ofNAM
	KEY=key
	KEYfound=False
	IsItemList=False
	msg=[]
	fin = open(fromFile, 'r')
	contentbyline = fin.readlines()
	for i in contentbyline[first_i_ofNAM+1:last_i_ofNAM]:
		ncurrline+=1
		if KEYfound:
			if not IsItemList and ('\item' in i or i=='' or '\end{itemize}' in i or 'begin{itemize}' in i):
				if 'begin{itemize}' in i:
					IsItemList=True
				else:
					break
			elif IsItemList:
				if '\end{itemize}' in i:
					break
				else:
					msg.append(i)
			else:
				msg.append(i)
		if not KEYfound:
			if '\index{'+KEY in i:
				KEY_i = ncurrline
				KEYfound = True
	msgfinal=[]
	alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	for j in msg:
		print(j)
		j = j.replace('\_','_') #Replace \_ of latex by _
		j = j + ' ' # add extra blank in case of linebreak in the latex doc for very long lines (which are not real linebreak)
		if '\item' in j:
			j = j.replace('\item','')
			if any((c in alphabet) for c in j): # If characters other than \item (could be better coded...)
				msgfinal.append(html.Br()) # Remove \item latex string and place Dash.html linebreak
				msgfinal.append(html.Br()) # Add a second Br() for an effective new line
				msgfinal.append('- ')      # Add instead a string
				msgfinal.append(j.replace('\n','')) # Remove \n occurence
			else: # only \item
				msgfinal.append(html.Br()) # Remove \item latex string and place Dash.html linebreak
				msgfinal.append(html.Br()) # Add a second Br() for an effective new line
				msgfinal.append('- ')      # Add instead a string
		else:
			msgfinal.append(j.replace('\n','')) # Remove \n occurence
	return msgfinal
