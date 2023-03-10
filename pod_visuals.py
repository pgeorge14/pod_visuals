import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mplsoccer.pitch import Pitch, VerticalPitch
import matplotlib as mpl
from highlight_text import fig_text
import numpy as np
from sklearn.cluster import KMeans
mpl.rcParams['figure.dpi'] = 400

import seaborn as sns

lfont = {'fontname':'Bahnschrift'}
hfont = {'fontname':'Rockwell Nova'}


from matplotlib.patches import Rectangle

import streamlit as st


#Variables
team = 175

comp = 'Championship'
season = '2022/23'

games = pd.read_csv('WBA23Games.csv')



options = st.sidebar.radio('Pages',
	options = ['Home',
	'Pass Map',
	'Passes Received',
	'Pass Comparison',
	'Defensive'
	])

if options =='Home':
	st.title('Post Match Visual Tool')
	st.markdown('**Use the side tabs to decide what visual you want, then use the drop-down boxes to select player and game.**')

oppo = st.selectbox('Select the opposition:',options = games['opposition'].unique())

venue_choice = st.selectbox('Home or away:',options = ['Home','Away'])

if venue_choice.lower() == 'home':
	venue = 'h'
elif venue_choice.lower() =='away':
	venue = 'a'

games_filtered = games[(games['opposition']==oppo)&(games['venue']==venue)].reset_index()
del games_filtered['index']

file = games_filtered['file'][0]

df = pd.read_csv(file+'.csv')

df = df[df['teamId']==team].reset_index()
del df['index']


df['xThreat'] = df['xThreat'].astype(float)


df['progDist'] = df['dist']
for x in range(len(df['x'])):
    if df['dist'][x]<0:
        df['progDist'][x] = 0
        

for x in range(len(df['x'])):
    if df['len'][x]<0:
        df['len'][x]  = df['len'][x]* -1
    
df_reset = df






if options == 'Pass Map':
	playername = st.selectbox('Select the player:',options = df['playerName'].unique())


	df_horizontal = df_reset

	df_horizontal['x'] = df_horizontal['x']*1.2
	df_horizontal['y'] = df_horizontal['y']*.8
	df_horizontal['endX'] = df_horizontal['endX']*1.2
	df_horizontal['endY'] = df_horizontal['endY']*.8

	df_horizontal=df_horizontal[(df_horizontal['y']>1) & (df_horizontal['y']<79)].reset_index()
	del df_horizontal['index']




	for x in range(len(df_horizontal['x'])):
	    if df_horizontal['playerName'][x] == playername:
	        playerno = df_horizontal['playerId'][x]

	df_passes = df_horizontal[(df_horizontal['playerName'] == playername)&(df_horizontal['teamId']==team)&
	              (df_horizontal['type']=='Pass')].reset_index()
	del df_passes['index']



	passes_attempted = len(df_passes)
	if passes_attempted==0:
	    pass_suc_rate = 0
	    suc_passes = 0
	else:
	    suc_passes = len(df_passes[df_passes['outcome']=='Successful'])
	    pass_suc_rate = suc_passes / passes_attempted *100


	xT =  df_passes.loc[df_passes['outcome'] == 'Successful', 'xThreat'].sum()
	xT_per_pass = xT / suc_passes

	suc_prog_passes = len(df_passes[(df_passes['prog']=='y')&(df_passes['outcome']=='Successful')])
	prog_passes_attempted = len(df_passes[df_passes['prog']=='y'])

	if prog_passes_attempted == 0:
	    prog_suc_rate = 0
	    prog_dist = 0
	    prog_dist_per_pass = 0
	else:
	    prog_suc_rate = suc_prog_passes / prog_passes_attempted *100
	    prog_dist = df_passes.loc[df_passes['outcome'] == 'Successful', 'progDist'].sum()
	    prog_dist_per_pass = prog_dist / suc_passes
	    pass_len = (df_passes.loc[df_passes['outcome'] == 'Successful', 'len'].sum()) / suc_passes

	suc_passes_to_box = len(df_passes[(df_passes['zone']!=27) & (df_passes['zone']!=28) & (df_passes['zone']!=29) & 
	                                  ((df_passes['endZone']==27)|(df_passes['endZone']==28)|(df_passes['endZone']==29))
	                                  & (df_passes['outcome']=='Successful')])

	suc_z14_passes = len(df_passes[(df_passes['zone']==23)&(df_passes['outcome']=='Successful')])

	suc_passes_to_z14 = len(df_passes[(df_passes['zone']!=23) & (df_passes['endZone']==23) & 
	                                  (df_passes['outcome']=='Successful')])

	crosses_attempted = len(df_passes[df_passes['cross']=='y'])
	if crosses_attempted == 0:
	    cross_suc_rate = 0
	else:
	    suc_crosses = len(df_passes[(df_passes['cross']=='y')&(df_passes['outcome']=='Successful')])
	    cross_suc_rate = suc_crosses / crosses_attempted *100


	friend = df_passes[df_passes['outcome']=='Successful'].groupby('recipientName').agg({'x':'count'})
	friend.columns = ['passCount']
	friend = friend.sort_values(by='passCount',ascending=False)
	friend = friend.reset_index()

	#dropping any rows that aren't player names
	friend['recipientName'] = friend['recipientName'].astype(str) 
	friend = friend[~friend.recipientName.str.contains(".0")]

	#getting the rank from the index and reordering the table
	friend = friend.reset_index()
	del friend['index']
	friend = friend.reset_index()
	friend['rank'] = friend['index']+1
	del friend['index']
	friend = friend[['rank','recipientName','passCount']]
	max_friend = friend['rank'].max()



	fig,ax = plt.subplots(figsize=(13.5, 8))
	fig.set_facecolor('#b1e1b7')
	ax.patch.set_facecolor('#b1e1b7')

	#creating the pitch
	pitch = Pitch(pitch_type='statsbomb', orientation='horizontal',
	              pitch_color='#b1e1b7', line_color='white', figsize=(16, 11),
	              constrained_layout=True, tight_layout=False)

	#draw the pitch on the ax figure, as well as inverting the y-axis
	pitch.draw(ax=ax)
	plt.gca().invert_yaxis()



	# #create the heat map
	# kde = sns.kdeplot(
	#     df_passes['endX'],
	#     df_passes['endY'],
	#     shade = True,
	#     shade_lowest  =False,
	#     alpha=.4,
	#     n_levels=10,
	#     cmap = 'mako'
	    
	# )

	    
	pitch.arrows(10,40,110,40,ax=ax,width=30, headwidth=5, color ='#2A6D32',zorder=1,alpha=.1)

	#use a loop to plot each pass
	for x in range(len(df_passes['x'])):
	    if df_passes['outcome'][x] == 'Successful':

	        pitch.lines(xstart=df_passes['x'][x],ystart=df_passes['y'][x],xend=df_passes['endX'][x],yend=df_passes['endY'][x],
	                    color='#4b3ea2',comet=True,alpha_start = 0.9, alpha_end = 0.5, transparent=True,ax=ax,zorder=12)
	        plt.scatter(df_passes['endX'][x],df_passes['endY'][x],color='#b1e1b7',edgecolor = '#4b3ea2',s=100,zorder=13) 
	        

	    if df_passes['outcome'][x] == 'Unsuccessful':

	        pitch.lines(xstart=df_passes['x'][x],ystart=df_passes['y'][x],xend=df_passes['endX'][x],yend=df_passes['endY'][x],
	                    color='#a44c3f',comet=True,alpha_start = 0.5, alpha_end = 0.2, transparent=True,ax=ax,zorder=10)
	        plt.scatter(df_passes['endX'][x],df_passes['endY'][x],color='#b1e1b7',edgecolor = '#a44c3f',s=100,zorder=11) 
	        
	plt.xlim(-0.01,155.01)
	plt.ylim(-20,81)
	        

	#title
	plt.text(0,87,str(df_passes['playerName'][0])+' Passes',c='#7b2f72',size=35,**hfont,ha='left',va='bottom')
	plt.text(2,81,'v '+oppo+ ', '+comp+' '+str(season),c='#2A6D32',size=25,**hfont,ha='left',va='bottom')



	#hex stats
	plt.scatter(10,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(10,-10,str(passes_attempted),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(10,-18,'Passes\nattempted',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(30,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(30,-10,str(round(pass_suc_rate,1)),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(30,-18,'Pass\nsuccess, %',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(50,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(50,-10,str(suc_prog_passes),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(50,-18,'Progressive\npasses',c='#2A6D32',size=15,ha='center',va='top',**lfont)
	    
	plt.scatter(70,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(70,-10,str(suc_passes_to_box),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(70,-18,'Passes into\nbox',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(90,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(90,-10,str(round(xT,3)),c='#7b2f72',size=20,ha='center',va='center',**lfont)
	plt.text(90,-18,'Expected\nThreat',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(110,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(110,-10,str(round(xT_per_pass*10,3)),c='#7b2f72',size=20,ha='center',va='center',**lfont)
	plt.text(110,-18,'xT per\n10 passes',c='#2A6D32',size=15,ha='center',va='top',**lfont)



	#passed to table
	plt.text(122,79.2,'Passed to:',ha='left',va='top',**lfont,size=15,c='#7b2f72')

	pass_height = 74.2
	for x in range(0,max_friend):
	    plt.text(123,pass_height,str(friend['recipientName'][x]),c='#4b3ea2',size=12,**lfont,ha='left',va='top')
	    plt.text(153,pass_height,friend['passCount'][x],c='#7b2f72',size=12,**lfont,ha='right',va='top')
	    plt.plot([121,155],[pass_height+0.8,pass_height+0.8], c='w',lw=1)

	    pass_height = pass_height - 4
	    
	plt.plot([121,155],[80,80], c='w',lw=1)
	plt.plot([121,155],[pass_height+0.8,pass_height+0.8], c='w',lw=1)

	plt.plot([121,121],[80,pass_height+0.8], c='w',lw=1)
	plt.plot([155,155],[80,pass_height+0.8], c='w',lw=1)
	plt.plot([149.5,149.5],[75,pass_height+0.8], c='w',lw=1)


	st.pyplot(fig)






if options == 'Passes Received':


	df_horizontal = df_reset

	df_horizontal['x'] = df_horizontal['x']*1.2
	df_horizontal['y'] = df_horizontal['y']*.8
	df_horizontal['endX'] = df_horizontal['endX']*1.2
	df_horizontal['endY'] = df_horizontal['endY']*.8

	df_horizontal=df_horizontal[(df_horizontal['y']>1) & (df_horizontal['y']<79)].reset_index()
	del df_horizontal['index']

		

	recipientname = st.selectbox('Select the recipient:',options = df_horizontal['playerName'].unique())

	for x in range(len(df_horizontal['x'])):
	    if df_horizontal['recipientName'][x] == recipientname:
	        playerno = df_horizontal['recipient'][x]

	df_recs = df_horizontal[(df_horizontal['recipientName'] == recipientname) & (df_horizontal['teamId']==team) &
	                  (df_horizontal['type']=='Pass') & (df_horizontal['outcome']=='Successful')].reset_index()


	del df_recs['index']

	rec_passes = len(df_recs)

	rec_xT = sum(df_recs['xThreat'])
	rec_xT_per_pass = rec_xT / rec_passes

	rec_prog_passes = len(df_recs[df_recs['prog']=='y'])

	rec_prog_dist = sum(df_recs['progDist'])
	rec_prog_dist_per_pass = rec_prog_dist / rec_passes

	rec_pass_len = sum(df_recs['len']) / rec_passes

	rec_box = len(df_recs[(df_recs['endZone']==27) | (df_recs['endZone']==28) | (df_recs['endZone']==29)])
	rec_break_box = len(df_recs[((df_recs['endZone']==27) | (df_recs['endZone']==28) | (df_recs['endZone']==29)) &
	                            (df_recs['zone']!=27) & (df_recs['zone']!=28) & (df_recs['zone']!=29)])

	rec_z14 = len(df_recs[df_recs['endZone']==23])
	rec_break_z14 = len(df_recs[(df_recs['endZone']==23) & (df_recs['zone']!=23)])

	rec_crosses = len(df_recs[df_recs['cross']=='y'])   

	giver = df_recs[df_recs['outcome']=='Successful'].groupby('playerName').agg({'x':'count'})
	giver.columns = ['passCount']
	giver = giver.sort_values(by='passCount',ascending=False)
	giver = giver.reset_index()

	#dropping any rows that aren't player names
	giver['playerName'] = giver['playerName'].astype(str) 
	giver = giver[~giver.playerName.str.contains(".0")]

	#getting the rank from the index and reordering the table
	giver = giver.reset_index()
	del giver['index']
	giver = giver.reset_index()
	giver['rank'] = giver['index']+1
	del giver['index']
	giver = giver[['rank','playerName','passCount']]
	max_giver = giver['rank'].max()


	fig,ax = plt.subplots(figsize=(13.5, 8))
	fig.set_facecolor('#b1e1b7')
	ax.patch.set_facecolor('#b1e1b7')

	#creating the pitch
	pitch = Pitch(pitch_type='statsbomb', orientation='horizontal',
	              pitch_color='#b1e1b7', line_color='white', figsize=(16, 11),
	              constrained_layout=True, tight_layout=False)

	#draw the pitch on the ax figure, as well as inverting the y-axis
	pitch.draw(ax=ax)
	plt.gca().invert_yaxis()



	#create the heat map
	my_cmap = mpl.colors.LinearSegmentedColormap.from_list("",['#b1e1b7','#9288d2'])

	#create the heat map
	kde = sns.kdeplot(
	    df_recs['endX'],
	    df_recs['endY'],
	    shade = True,
	    shade_lowest  =False,
	    alpha=.4,
	    n_levels= 200,
	    cmap = my_cmap, 
	    thresh=0,
	    zorder=2
	    
	)


	    
	pitch.arrows(10,40,110,40,ax=ax,width=30, headwidth=5, color ='w',zorder=1,alpha=.1)

	for x in range(len(df_recs['x'])):
	    if df_recs['prog'][x]=='y':
	        plt.scatter(df_recs['endX'][x],df_recs['endY'][x],color='#4b3ea2',edgecolor='w',s=200,lw=1,alpha = 1,zorder=12)       
	        pitch.lines(xstart=df_recs['x'][x],ystart=df_recs['y'][x],xend=df_recs['endX'][x],yend=df_recs['endY'][x],
	                    color='#4b3ea2',comet=True,alpha_start = 0.6, alpha_end = 0.3, transparent=True,ax=ax,zorder=10)
	        
	    if df_recs['prog'][x]=='n':
	        plt.scatter(df_recs['endX'][x],df_recs['endY'][x],color='#9288d2',s=75,edgecolor='#4b3ea2',alpha = 1,zorder=11)
	        pitch.lines(xstart=df_recs['x'][x],ystart=df_recs['y'][x],xend=df_recs['endX'][x],yend=df_recs['endY'][x],
	                    color='#9288d2',comet=True,alpha_start = 0.4, alpha_end = 0.1, transparent=True,ax=ax,zorder=9)
	        
	#     plt.text(df_recs['x'][x],df_recs['y'][x],int(df_recs['playerId'][x]),size=15,ha='center',va='center',**lfont,
	#                 c='w',zorder=16)
	        


	plt.xlim(-0.01,155.01)
	plt.ylim(-20,81)
	        

	#title
	plt.text(0,87,str(df_recs['recipientName'][0])+' Passes Received',c='#7b2f72',size=35,**hfont,ha='left',va='bottom')
	plt.text(2,81,'v '+oppo+ ', '+comp+' '+str(season),c='#2A6D32',size=25,**hfont,ha='left',va='bottom')


	plt.scatter(10,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32',zorder=3)
	plt.text(10,-10,str(rec_passes),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(10,-18,'Passes\nreceived',c='#2A6D32',size=15,ha='center',va='top',**lfont)


	plt.scatter(30,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32',zorder=3)
	plt.text(30,-10,str(round(rec_pass_len,1)),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(30,-18,'Average\nlength\n(yards)',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(50,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32',zorder=3)
	plt.text(50,-10,str(rec_prog_passes),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(50,-18,'Progressive\npasses\nreceived',c='#2A6D32',size=15,ha='center',va='top',**lfont)
	    
	plt.scatter(70,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32',zorder=3)
	plt.text(70,-10,str(rec_z14),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(70,-18,'Zone 14\nreceptions',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(90,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32',zorder=3)
	plt.text(90,-10,str(rec_box),c='#7b2f72',size=25,ha='center',va='center',**lfont)
	plt.text(90,-18,'Box\nreceptions',c='#2A6D32',size=15,ha='center',va='top',**lfont)

	plt.scatter(110,-10,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32',zorder=3)
	plt.text(110,-10,str(round(rec_xT,3)),c='#7b2f72',size=20,ha='center',va='center',**lfont)
	plt.text(110,-18,'Expected\nThreat\nreceived',c='#2A6D32',size=15,ha='center',va='top',**lfont)




	#passed to table
	plt.text(122,79.2,'Received from:',ha='left',va='top',**lfont,size=15,c='#7b2f72')

	rec_height = 74.2
	for x in range(0,max_giver):
	    plt.text(123,rec_height,str(giver['playerName'][x]),c='#4b3ea2',size=12,**lfont,ha='left',va='top')
	    plt.text(153,rec_height,giver['passCount'][x],c='#7b2f72',size=12,**lfont,ha='right',va='top')
	    plt.plot([121,155],[rec_height+0.8,rec_height+0.8], c='w',lw=1)

	    rec_height = rec_height - 4
	    
	plt.plot([121,155],[80,80], c='w',lw=1)
	plt.plot([121,155],[rec_height+0.8,rec_height+0.8], c='w',lw=1)

	plt.plot([121,121],[80,rec_height+0.8], c='w',lw=1)
	plt.plot([155,155],[80,rec_height+0.8], c='w',lw=1)
	plt.plot([149.5,149.5],[75,rec_height+0.8], c='w',lw=1)




	ax.add_patch(Rectangle((0,-0.8), 120, -20,
	             alpha = 1,
	             edgecolor = '#b1e1b7',
	             facecolor = '#b1e1b7',
	             fill=True,
	             lw=5,zorder=2))

	st.pyplot(fig)







if options =='Pass Comparison':
	playername1 = st.selectbox('Select the first player:',options = df['playerName'].unique())
	playername2 = st.selectbox('Select the second player:',options = df['playerName'].unique())

	df_vertical = df_reset

	df_vertical['x2'] = 80 - (df_vertical['y']*0.8)
	df_vertical['endX2'] = 80 - (df_vertical['endY']*0.8)

	df_vertical['y2'] = df_vertical['x']*1.2
	df_vertical['endY2'] = df_vertical['endX']*1.2

	df_vertical['x'] = df_vertical['x2']
	df_vertical['endX'] = df_vertical['endX2']
	df_vertical['y'] = df_vertical['y2']
	df_vertical['endY'] = df_vertical['endY2']

	df_vertical=df_vertical[(df_vertical['x']>1) & (df_vertical['x']<79)].reset_index()
	del df_vertical['index']

	df_comp = df_vertical
	df_comp['x_start'] = 0
	df_comp['x_add'] = 0

	df_comp['y_start'] = 0
	df_comp['y_add'] = 0



	for x in range(len(df_comp['zone'])):
	    if df_comp['zone'][x] == 5:  
	        df_comp['x_start'][x] = 0
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 0
	        df_comp['y_add'][x] = 18
	        
	    elif df_comp['zone'][x] == 4:  
	        df_comp['x_start'][x] = 18
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 0
	        df_comp['y_add'][x] = 18
	        
	    elif df_comp['zone'][x] == 3:  
	        df_comp['x_start'][x] = 30
	        df_comp['x_add'][x] = 20

	        df_comp['y_start'][x] = 0
	        df_comp['y_add'][x] = 18
	        
	    elif df_comp['zone'][x] == 2:  
	        df_comp['x_start'][x] = 50
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 0
	        df_comp['y_add'][x] = 18
	        
	        
	    elif df_comp['zone'][x] == 1:  
	        df_comp['x_start'][x] = 62
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 0
	        df_comp['y_add'][x] = 18
	    
	    
	       
	        
	    elif df_comp['zone'][x] == 10:  
	        df_comp['x_start'][x] = 0
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 18
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 9:  
	        df_comp['x_start'][x] = 18
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 18
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 8:  
	        df_comp['x_start'][x] = 30
	        df_comp['x_add'][x] = 20

	        df_comp['y_start'][x] = 18
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 7:  
	        df_comp['x_start'][x] = 50
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 18
	        df_comp['y_add'][x] = 21
	        
	        
	    elif df_comp['zone'][x] == 6:  
	        df_comp['x_start'][x] = 62
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 18
	        df_comp['y_add'][x] = 21      

	        
	        
	        
	        
	
	    elif df_comp['zone'][x] == 15:  
	        df_comp['x_start'][x] = 0
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 39
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 14:  
	        df_comp['x_start'][x] = 18
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 39
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 13:  
	        df_comp['x_start'][x] = 30
	        df_comp['x_add'][x] = 20

	        df_comp['y_start'][x] = 39
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 12:  
	        df_comp['x_start'][x] = 50
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 39
	        df_comp['y_add'][x] = 21
	        
	        
	    elif df_comp['zone'][x] == 11:  
	        df_comp['x_start'][x] = 62
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 39
	        df_comp['y_add'][x] = 21
	        
	        

	

	    elif df_comp['zone'][x] == 20:  
	        df_comp['x_start'][x] = 0
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 60
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 19:  
	        df_comp['x_start'][x] = 18
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 60
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 18:  
	        df_comp['x_start'][x] = 30
	        df_comp['x_add'][x] = 20

	        df_comp['y_start'][x] = 60
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 17:  
	        df_comp['x_start'][x] = 50
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 60
	        df_comp['y_add'][x] = 21
	        
	        
	    elif df_comp['zone'][x] == 16:  
	        df_comp['x_start'][x] = 62
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 60
	        df_comp['y_add'][x] = 21
	        
	        
	        


	    elif df_comp['zone'][x] == 25:  
	        df_comp['x_start'][x] = 0
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 81
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 24:  
	        df_comp['x_start'][x] = 18
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 81
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 23:  
	        df_comp['x_start'][x] = 30
	        df_comp['x_add'][x] = 20

	        df_comp['y_start'][x] = 81
	        df_comp['y_add'][x] = 21
	        
	    elif df_comp['zone'][x] == 22:  
	        df_comp['x_start'][x] = 50
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 81
	        df_comp['y_add'][x] = 21
	        
	        
	    elif df_comp['zone'][x] == 21:  
	        df_comp['x_start'][x] = 62
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 81
	        df_comp['y_add'][x] = 21
	        
	        
	        
	

	    elif df_comp['zone'][x] == 30:  
	        df_comp['x_start'][x] = 0
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 102
	        df_comp['y_add'][x] = 18
	        
	    elif df_comp['zone'][x] == 29:  
	        df_comp['x_start'][x] = 18
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 102
	        df_comp['y_add'][x] = 18
	        
	    elif df_comp['zone'][x] == 28:  
	        df_comp['x_start'][x] = 30
	        df_comp['x_add'][x] = 20

	        df_comp['y_start'][x] = 102
	        df_comp['y_add'][x] = 18
	        
	    elif df_comp['zone'][x] == 27:  
	        df_comp['x_start'][x] = 50
	        df_comp['x_add'][x] = 12

	        df_comp['y_start'][x] = 102
	        df_comp['y_add'][x] = 18
	        
	        
	    elif df_comp['zone'][x] == 26:  
	        df_comp['x_start'][x] = 62
	        df_comp['x_add'][x] = 18

	        df_comp['y_start'][x] = 102
	        df_comp['y_add'][x] = 18



	df_comp['x_end_start'] = 0
	df_comp['x_end_add'] = 0

	df_comp['y_end_start'] = 0
	df_comp['y_end_add'] = 0



	for x in range(len(df_comp['endZone'])):
	    if df_comp['endZone'][x] == 5:  
	        df_comp['x_end_start'][x] = 0
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 0
	        df_comp['y_end_add'][x] = 18
	        
	    elif df_comp['endZone'][x] == 4:  
	        df_comp['x_end_start'][x] = 18
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 0
	        df_comp['y_end_add'][x] = 18
	        
	    elif df_comp['endZone'][x] == 3:  
	        df_comp['x_end_start'][x] = 30
	        df_comp['x_end_add'][x] = 20

	        df_comp['y_end_start'][x] = 0
	        df_comp['y_end_add'][x] = 18
	        
	    elif df_comp['endZone'][x] == 2:  
	        df_comp['x_end_start'][x] = 50
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 0
	        df_comp['y_end_add'][x] = 18
	        
	        
	    elif df_comp['endZone'][x] == 1:  
	        df_comp['x_end_start'][x] = 62
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 0
	        df_comp['y_end_add'][x] = 18
	    
	    
       
	        
	    elif df_comp['endZone'][x] == 10:  
	        df_comp['x_end_start'][x] = 0
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 18
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 9:  
	        df_comp['x_end_start'][x] = 18
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 18
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 8:  
	        df_comp['x_end_start'][x] = 30
	        df_comp['x_end_add'][x] = 20

	        df_comp['y_end_start'][x] = 18
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 7:  
	        df_comp['x_end_start'][x] = 50
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 18
	        df_comp['y_end_add'][x] = 21
	        
	        
	    elif df_comp['endZone'][x] == 6:  
	        df_comp['x_end_start'][x] = 62
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 18
	        df_comp['y_end_add'][x] = 21      

	        
	        
	        
	        

	    elif df_comp['endZone'][x] == 15:  
	        df_comp['x_end_start'][x] = 0
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 39
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 14:  
	        df_comp['x_end_start'][x] = 18
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 39
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 13:  
	        df_comp['x_end_start'][x] = 30
	        df_comp['x_end_add'][x] = 20

	        df_comp['y_end_start'][x] = 39
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 12:  
	        df_comp['x_end_start'][x] = 50
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 39
	        df_comp['y_end_add'][x] = 21
	        
	        
	    elif df_comp['endZone'][x] == 11:  
	        df_comp['x_end_start'][x] = 62
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 39
	        df_comp['y_end_add'][x] = 21
	        
	        



	    elif df_comp['endZone'][x] == 20:  
	        df_comp['x_end_start'][x] = 0
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 60
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 19:  
	        df_comp['x_end_start'][x] = 18
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 60
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 18:  
	        df_comp['x_end_start'][x] = 30
	        df_comp['x_end_add'][x] = 20

	        df_comp['y_end_start'][x] = 60
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 17:  
	        df_comp['x_end_start'][x] = 50
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 60
	        df_comp['y_end_add'][x] = 21
	        
	        
	    elif df_comp['endZone'][x] == 16:  
	        df_comp['x_end_start'][x] = 62
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 60
	        df_comp['y_end_add'][x] = 21
	        
	        
	        


	    elif df_comp['endZone'][x] == 25:  
	        df_comp['x_end_start'][x] = 0
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 81
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 24:  
	        df_comp['x_end_start'][x] = 18
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 81
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 23:  
	        df_comp['x_end_start'][x] = 30
	        df_comp['x_end_add'][x] = 20

	        df_comp['y_end_start'][x] = 81
	        df_comp['y_end_add'][x] = 21
	        
	    elif df_comp['endZone'][x] == 22:  
	        df_comp['x_end_start'][x] = 50
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 81
	        df_comp['y_end_add'][x] = 21
	        
	        
	    elif df_comp['endZone'][x] == 21:  
	        df_comp['x_end_start'][x] = 62
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 81
	        df_comp['y_end_add'][x] = 21
	        
	        
	        
	

	    elif df_comp['endZone'][x] == 30:  
	        df_comp['x_end_start'][x] = 0
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 102
	        df_comp['y_end_add'][x] = 18
	        
	    elif df_comp['endZone'][x] == 29:  
	        df_comp['x_end_start'][x] = 18
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 102
	        df_comp['y_end_add'][x] = 18
	        
	    elif df_comp['endZone'][x] == 28:  
	        df_comp['x_end_start'][x] = 30
	        df_comp['x_end_add'][x] = 20

	        df_comp['y_end_start'][x] = 102
	        df_comp['y_end_add'][x] = 18
	        
	    elif df_comp['endZone'][x] == 27:  
	        df_comp['x_end_start'][x] = 50
	        df_comp['x_end_add'][x] = 12

	        df_comp['y_end_start'][x] = 102
	        df_comp['y_end_add'][x] = 18
	        
	        
	    elif df_comp['endZone'][x] == 26:  
	        df_comp['x_end_start'][x] = 62
	        df_comp['x_end_add'][x] = 18

	        df_comp['y_end_start'][x] = 102
	        df_comp['y_end_add'][x] = 18	

	for x in range(len(df_comp['x'])):
		if df_comp['playerName'][x] == playername1:
			playerno1 = df_comp['playerId'][x]

	for x in range(len(df_comp['x'])):
		if df_comp['playerName'][x] == playername2:
			playerno2 = df_comp['playerId'][x]

	df_passes_comp = df_comp[((df_comp['playerName'] == playername1)|(df_comp['playerName'] == playername2))&(df_comp['teamId']==team)&(df_comp['type']=='Pass')].reset_index()

	del df_passes_comp['index']

	df_passes_comp_1 = df_passes_comp[df_passes_comp['playerName']==playername1].reset_index()
	del df_passes_comp_1['index']

	df_passes_comp_2 = df_passes_comp[df_passes_comp['playerName']==playername2].reset_index()
	del df_passes_comp_2['index']

	passes_attempted_1 = len(df_passes_comp_1)
	if passes_attempted_1==0:
	    pass_suc_rate_1 = 0
	    suc_passes_1 = 0
	else:
	    suc_passes_1 = len(df_passes_comp_1[df_passes_comp_1['outcome']=='Successful'])
	    pass_suc_rate_1 = suc_passes_1 / passes_attempted_1 *100


	xT_1 =  df_passes_comp_1.loc[df_passes_comp_1['outcome'] == 'Successful', 'xThreat'].sum()
	xT_per_pass_1 = xT_1 / suc_passes_1

	suc_prog_passes_1 = len(df_passes_comp_1[(df_passes_comp_1['prog']=='y')&(df_passes_comp_1['outcome']=='Successful')])
	prog_passes_attempted_1 = len(df_passes_comp_1[df_passes_comp_1['prog']=='y'])

	if prog_passes_attempted_1 == 0:
	    prog_suc_rate_1 = 0
	    prog_dist_1 = 0
	    prog_dist_per_pass_1 = 0
	else:
	    prog_suc_rate_1 = suc_prog_passes_1 / prog_passes_attempted_1 *100
	    prog_dist_1 = df_passes_comp_1.loc[df_passes_comp_1['outcome'] == 'Successful', 'progDist'].sum() 
	    prog_dist_per_pass_1 = prog_dist_1 / suc_passes_1
	    pass_len = (df_passes_comp_1.loc[df_passes_comp_1['outcome'] == 'Successful', 'len'].sum()) / suc_passes_1

	suc_passes_to_box_1 = len(df_passes_comp_1[(df_passes_comp_1['zone']!=27) & (df_passes_comp_1['zone']!=28) & (df_passes_comp_1['zone']!=29) & 
	                                  ((df_passes_comp_1['endZone']==27)|(df_passes_comp_1['endZone']==28)|(df_passes_comp_1['endZone']==29))
	                                  & (df_passes_comp_1['outcome']=='Successful')])

	suc_z14_passes_1 = len(df_passes_comp_1[(df_passes_comp_1['zone']==23)&(df_passes_comp_1['outcome']=='Successful')]) 

	suc_passes_to_z14_1 = len(df_passes_comp_1[(df_passes_comp_1['zone']!=23) & (df_passes_comp_1['endZone']==23) & 
	                                  (df_passes_comp_1['outcome']=='Successful')]) 

	crosses_attempted_1 = len(df_passes_comp_1[df_passes_comp_1['cross']=='y']) 
	if crosses_attempted_1 == 0:
	    cross_suc_rate_1 = 0
	else:
	    suc_crosses_1 = len(df_passes_comp_1[(df_passes_comp_1['cross']=='y')&(df_passes_comp_1['outcome']=='Successful')]) 
	    cross_suc_rate_1 = suc_crosses_1 / crosses_attempted_1 *100


	passes_attempted_2 = len(df_passes_comp_2)
	if passes_attempted_2==0:
	    pass_suc_rate_2 = 0
	    suc_passes_2 = 0
	else:
	    suc_passes_2 = len(df_passes_comp_2[df_passes_comp_2['outcome']=='Successful'])
	    pass_suc_rate_2 = suc_passes_2 / passes_attempted_2 *100


	xT_2 =  df_passes_comp_2.loc[df_passes_comp_2['outcome'] == 'Successful', 'xThreat'].sum()
	xT_per_pass_2 = xT_2 / suc_passes_2

	suc_prog_passes_2 = len(df_passes_comp_2[(df_passes_comp_2['prog']=='y')&(df_passes_comp_2['outcome']=='Successful')])
	prog_passes_attempted_2 = len(df_passes_comp_2[df_passes_comp_2['prog']=='y'])

	if prog_passes_attempted_2 == 0:
	    prog_suc_rate_2 = 0
	    prog_dist_2 = 0
	    prog_dist_per_pass_2 = 0
	else:
	    prog_suc_rate_2 = suc_prog_passes_2 / prog_passes_attempted_2 *100
	    prog_dist_2 = df_passes_comp_2.loc[df_passes_comp_2['outcome'] == 'Successful', 'progDist'].sum() 
	    prog_dist_per_pass_2 = prog_dist_2 / suc_passes_2
	    pass_len = (df_passes_comp_2.loc[df_passes_comp_2['outcome'] == 'Successful', 'len'].sum()) / suc_passes_2

	suc_passes_to_box_2 = len(df_passes_comp_2[(df_passes_comp_2['zone']!=27) & (df_passes_comp_2['zone']!=28) & (df_passes_comp_2['zone']!=29) & 
	                                  ((df_passes_comp_2['endZone']==27)|(df_passes_comp_2['endZone']==28)|(df_passes_comp_2['endZone']==29))
	                                  & (df_passes_comp_2['outcome']=='Successful')])

	suc_z14_passes_2 = len(df_passes_comp_2[(df_passes_comp_2['zone']==23)&(df_passes_comp_2['outcome']=='Successful')]) 

	suc_passes_to_z14_2 = len(df_passes_comp_2[(df_passes_comp_2['zone']!=23) & (df_passes_comp_2['endZone']==23) & 
	                                  (df_passes_comp_2['outcome']=='Successful')]) 

	crosses_attempted_2 = len(df_passes_comp_2[df_passes_comp_2['cross']=='y']) 
	if crosses_attempted_2 == 0:
	    cross_suc_rate_2 = 0
	else:
	    suc_crosses_2 = len(df_passes_comp_2[(df_passes_comp_2['cross']=='y')&(df_passes_comp_2['outcome']=='Successful')]) 
	    cross_suc_rate_2 = suc_crosses_2 / crosses_attempted_2 *100



	df_suc_passes_1 = df_passes_comp_1[df_passes_comp_1['outcome']=='Successful'].reset_index()
	del df_suc_passes_1['index']

	df_suc_passes_2 = df_passes_comp_2[df_passes_comp_2['outcome']=='Successful'].reset_index()
	del df_suc_passes_2['index']


	zones_1 = df_suc_passes_1.groupby('zone').agg({'zone':'count','x_start':'mean','x_add':'mean','y_start':'mean','y_add':'mean'})
	zones_1.columns = ['passes','x_start','x_add','y_start','y_add']
	zones_1 = zones_1.sort_values(by='zone',ascending=True)
	zones_1 = zones_1.reset_index()

	passes_1 = sum(zones_1['passes'])
	zones_1['passes, %'] = round(zones_1['passes'] / passes_1 *100,1)

	zones_2 = df_suc_passes_2.groupby('zone').agg({'zone':'count','x_start':'mean','x_add':'mean','y_start':'mean','y_add':'mean'})
	zones_2.columns = ['passes','x_start','x_add','y_start','y_add']
	zones_2 = zones_2.sort_values(by='zone',ascending=True)
	zones_2 = zones_2.reset_index()

	passes_2 = sum(zones_2['passes'])
	zones_2['passes, %'] = round(zones_2['passes'] / passes_2 *100,1)

	s_min = 0
	s_max = 12

	passes_max_1 = zones_1['passes, %'].max()
	passes_max_2 = zones_2['passes, %'].max()


	if passes_max_1 > s_max:
	    s_max = passes_max_1
	if passes_max_2 > s_max:
	    s_max = passes_max_2
	

	my_cmap = mpl.colors.LinearSegmentedColormap.from_list("",['#b1e1b7','#4b3ea2'])

	cmap = plt.cm.autumn.reversed()
	norm = mpl.colors.Normalize(vmin=s_min, vmax=s_max,clip = True)
	mapper = plt.cm.ScalarMappable(norm=norm, cmap=my_cmap)
	                               
	zones_1['colour'] = ' '

	zones_1['colour'] = zones_1['passes, %'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))


	zones_2['colour'] = ' '

	zones_2['colour'] = zones_2['passes, %'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))


	fig,axes=plt.subplots(1,2,figsize=(15,20))
	ax1 = plt.subplot2grid((1,2), (0,0))
	ax2 = plt.subplot2grid((1,2), (0,1))

	plt.subplots_adjust(left=0.1,
	                        bottom=0.1, 
	                        right=0.9, 
	                        top=0.9, 
	                        wspace=0.1, 
	                        hspace=0.1)





	fig,axes=plt.subplots(1,2,figsize=(15,20))
	ax1 = plt.subplot2grid((1,2), (0,0))
	ax2 = plt.subplot2grid((1,2), (0,1))

	plt.subplots_adjust(left=0.1,
	                        bottom=0.1, 
	                        right=0.9, 
	                        top=0.9, 
	                        wspace=0.1, 
	                        hspace=0.1)





	fig.set_facecolor('#b1e1b7')
	ax1.patch.set_facecolor('#b1e1b7')
	ax2.patch.set_facecolor('#b1e1b7')



	#creating the pitch
	pitch = VerticalPitch(pitch_type='statsbomb',
	              pitch_color='#b1e1b7', line_color='#2A6D32', figsize=(16, 11),
	              constrained_layout=True, tight_layout=True)

	#draw the pitch on the ax figure, as well as inverting the y-axis
	pitch.draw(ax=ax1)
	#plt.gca().invert_yaxis()

	#vertical lines
	ax1.plot([18,18],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([30,30],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([50,50],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([62,62],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)


	# #horizontal lines
	ax1.plot([0,80],[18,18],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([0,80],[39,39],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([0,80],[60,60],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([0,80],[81,81],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax1.plot([0,80],[102,102],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)



	for x in range(len(df_passes_comp_1['x'])):
	    if df_passes_comp_1['outcome'][x] == 'Successful':

	        pitch.lines(xstart=df_passes_comp_1['y'][x],ystart=df_passes_comp_1['x'][x],xend=df_passes_comp_1['endY'][x],yend=df_passes_comp_1['endX'][x],
	                    color='#4b3ea2',comet=True,alpha_start = 0.9, alpha_end = 0.5, transparent=True,ax=ax1,zorder=12)
	        ax1.scatter(df_passes_comp_1['endX'][x],df_passes_comp_1['endY'][x],color='#b1e1b7',edgecolor = '#4b3ea2',s=100,zorder=13) 
	        

	    if df_passes_comp_1['outcome'][x] == 'Unsuccessful':

	        pitch.lines(xstart=df_passes_comp_1['y'][x],ystart=df_passes_comp_1['x'][x],xend=df_passes_comp_1['endY'][x],yend=df_passes_comp_1['endX'][x],
	                    color='#a44c3f',comet=True,alpha_start = 0.5, alpha_end = 0.2, transparent=True,ax=ax1,zorder=10)
	        ax1.scatter(df_passes_comp_1['endX'][x],df_passes_comp_1['endY'][x],color='#b1e1b7',edgecolor = '#a44c3f',s=100,zorder=11) 
	        
	        
	        
	        
	for x in range(len(zones_1['zone'])):
	    ax1.add_patch(Rectangle((zones_1['x_start'][x],zones_1['y_start'][x]), zones_1['x_add'][x], zones_1['y_add'][x],
	                 alpha = 0.4,
	                 edgecolor = None,
	                 facecolor = zones_1['colour'][x],
	                 fill=True,
	                 lw=1, 
	                 zorder=3))    
	        
	        
	ax1.scatter((80/14)*1,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax1.text((80/14)*1,-10,round(passes_attempted_1,1),c='#7b2f72',size=29,ha='center',va='center',**lfont,zorder=5)
	ax1.text((80/14)*1,-20,'Passes\nattempted',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	ax1.scatter((80/14)*5,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax1.text((80/14)*5,-10,round(pass_suc_rate_1,1),c='#7b2f72',size=29,ha='center',va='center',**lfont,zorder=5)
	ax1.text((80/14)*5,-20,'Pass\nsuccess, %',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	ax1.scatter((80/14)*9,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax1.text((80/14)*9,-10,round(suc_prog_passes_1,1),c='#7b2f72',size=29,ha='center',va='center',**lfont,zorder=5)
	ax1.text((80/14)*9,-20,'Progressive\npasses\ncompleted',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	ax1.scatter((80/14)*13,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax1.text((80/14)*13,-10,round(xT_1,3),c='#7b2f72',size=25,ha='center',va='center',**lfont,zorder=5)
	ax1.text((80/14)*13,-20,'Expected\nThreat',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	        
	    
	ax1.text(40,121,playername1,c='#7b2f72',size=25,**lfont,ha='center',va='bottom')

	ax1.set_xlim(-10,90)
	ax1.set_ylim(-25,125)        
	        
	        
	pitch.draw(ax=ax2)
	#plt.gca().invert_yaxis()

	#vertical lines
	ax2.plot([18,18],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([30,30],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([50,50],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([62,62],[0,120],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)


	# #horizontal lines
	ax2.plot([0,80],[18,18],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([0,80],[39,39],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([0,80],[60,60],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([0,80],[81,81],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)
	ax2.plot([0,80],[102,102],c='#2A6D32',lw=1,linestyle = 'dashed',alpha=0.5,zorder=5)




	for x in range(len(df_passes_comp_2['x'])):
	    if df_passes_comp_2['outcome'][x] == 'Successful':

	        pitch.lines(xstart=df_passes_comp_2['y'][x],ystart=df_passes_comp_2['x'][x],xend=df_passes_comp_2['endY'][x],yend=df_passes_comp_2['endX'][x],
	                    color='#4b3ea2',comet=True,alpha_start = 0.9, alpha_end = 0.5, transparent=True,ax=ax2,zorder=12)
	        ax2.scatter(df_passes_comp_2['endX'][x],df_passes_comp_2['endY'][x],color='#b1e1b7',edgecolor = '#4b3ea2',s=100,zorder=13) 
	        

	    if df_passes_comp_2['outcome'][x] == 'Unsuccessful':

	        pitch.lines(xstart=df_passes_comp_2['y'][x],ystart=df_passes_comp_2['x'][x],xend=df_passes_comp_2['endY'][x],yend=df_passes_comp_2['endX'][x],
	                    color='#a44c3f',comet=True,alpha_start = 0.5, alpha_end = 0.2, transparent=True,ax=ax2,zorder=10)
	        ax2.scatter(df_passes_comp_2['endX'][x],df_passes_comp_2['endY'][x],color='#b1e1b7',edgecolor = '#a44c3f',s=100,zorder=11) 
	        
	        
	    
	    
	for x in range(len(zones_2['zone'])):
	    ax2.add_patch(Rectangle((zones_2['x_start'][x],zones_2['y_start'][x]), zones_2['x_add'][x], zones_2['y_add'][x],
	                 alpha = 0.4,
	                 edgecolor = None,
	                 facecolor = zones_2['colour'][x],
	                 fill=True,
	                 lw=1, 
	                 zorder=3))    
	    
	    
	    
	ax2.text(40,121,playername2,c='#7b2f72',size=25,**lfont,ha='center',va='bottom')

	ax2.scatter((80/14)*1,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax2.text((80/14)*1,-10,round(passes_attempted_2,1),c='#7b2f72',size=29,ha='center',va='center',**lfont,zorder=5)
	ax2.text((80/14)*1,-20,'Passes\nattempted',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	ax2.scatter((80/14)*5,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax2.text((80/14)*5,-10,round(pass_suc_rate_2,1),c='#7b2f72',size=29,ha='center',va='center',**lfont,zorder=5)
	ax2.text((80/14)*5,-20,'Pass\nsuccess, %',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	ax2.scatter((80/14)*9,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax2.text((80/14)*9,-10,round(suc_prog_passes_2,1),c='#7b2f72',size=29,ha='center',va='center',**lfont,zorder=5)
	ax2.text((80/14)*9,-20,'Progressive\npasses\ncompleted',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)

	ax2.scatter((80/14)*13,-10,marker='h',s=5000,facecolors='none',edgecolors='#2A6D32',lw=1,zorder=5)
	ax2.text((80/14)*13,-10,round(xT_2,3),c='#7b2f72',size=25,ha='center',va='center',**lfont,zorder=5)
	ax2.text((80/14)*13,-20,'Expected\nThreat',c='#2A6D32',size=15,ha='center',va='top',**lfont,zorder=5)




	ax2.set_xlim(-10,90)
	ax2.set_ylim(-25,125)

	ax1.text(-10,139,'Pass Maps', color='#7b2f72', size=55,**hfont,va='bottom',ha='left')
	ax1.text(-6,129,'v '+oppo+', '+comp+' '+str(season),c='#2A6D32',size=35,**hfont,ha='left',va='bottom')

	st.pyplot(fig)






if options =='Defensive':
	playername = st.selectbox('Select the player:',options = df['playerName'].unique())


	df_horizontal = df_reset

	df_horizontal['x'] = df_horizontal['x']*1.2
	df_horizontal['y'] = df_horizontal['y']*.8
	df_horizontal['endX'] = df_horizontal['endX']*1.2
	df_horizontal['endY'] = df_horizontal['endY']*.8

	df_horizontal=df_horizontal[(df_horizontal['y']>1) & (df_horizontal['y']<79)].reset_index()
	del df_horizontal['index']

	df_def = df_horizontal

	df_def = df_def[df_def['playerName']==playername].reset_index()
	del df_def['index']

	df_def = df_def[(df_def['type'] == 'Tackle') | (df_def['type']=='Aerial') | 
			(df_def['type']=='Interception')].reset_index()

	interceptions = len(df_def[(df_def['type']=='Interception')&(df_def['outcome']=='Successful')])
	tackles =len(df_def[(df_def['type']=='Tackle')&(df_def['outcome']=='Successful')])
	sucAerials = len(df_def[(df_def['type']=='Aerial')&(df_def['outcome']=='Successful')])
	aerials = len(df_def[df_def['type']=='Aerial'])
	if sucAerials == 0:
		aerial_pc = 0
	else:
		aerial_pc = round((sucAerials/aerials*100),1)



	fig,ax = plt.subplots(figsize=(13.5, 8))
	fig.set_facecolor('#b1e1b7')
	ax.patch.set_facecolor('#b1e1b7')

	#creating the pitch
	pitch = Pitch(pitch_type='statsbomb', orientation='horizontal',
	              pitch_color='#b1e1b7', line_color='white', figsize=(16, 11),
	              constrained_layout=True, tight_layout=False)

	#draw the pitch on the ax figure, as well as inverting the y-axis
	pitch.draw(ax=ax)
	plt.gca().invert_yaxis()


	pitch.arrows(10,40,110,40,ax=ax,width=30, headwidth=5, color ='w',zorder=1,alpha=.1)

	for x in range(len(df_def['x'])):

		if df_def['type'][x]=='Tackle':
			if df_def['outcome'][x] == 'Successful':
				plt.scatter(df_def['x'][x],df_def['y'][x], marker = 'X', color='#7b2f72',edgecolor='w', s=400, alpha = 0.8,zorder=7)
	            
			if df_def['outcome'][x] == 'Unsuccessful':
				plt.scatter(df_def['x'][x],df_def['y'][x], marker = 'X', color='#c72929',edgecolor='w', s=300,alpha = 0.2,zorder=5)

		if df_def['type'][x]=='Aerial':
			if df_def['outcome'][x] == 'Successful':
				plt.scatter(df_def['x'][x],df_def['y'][x], marker = '^', facecolor='#2939C7',edgecolor='w', s=400, alpha = 0.8,zorder=7)
	            
			if df_def['outcome'][x] == 'Unsuccessful':
				plt.scatter(df_def['x'][x],df_def['y'][x], marker = '^', facecolor='#c72929',edgecolor='w', s=300,alpha = 0.2,zorder=5) 

		if df_def['type'][x]=='Interception':
			if df_def['outcome'][x] == 'Successful':
				plt.scatter(df_def['x'][x],df_def['y'][x], color='#c7b729', s=400, alpha = 0.8,zorder=7)
	            
			if df_def['outcome'][x] == 'Unsuccessul':
				plt.scatter(df_def['x'][x],df_def['y'][x], color='#c72929', s=300,alpha = 0.2,zorder=5)  


	plt.xlim(-0.01,120.01)
	plt.ylim(-20,81)
	        

	#title
	plt.text(0,87,str(df_def['playerName'][0])+' Defensive Actions',c='#7b2f72',size=35,**hfont,ha='left',va='bottom')
	plt.text(2,81,'v '+oppo+ ', '+comp+' '+str(season),c='#2A6D32',size=25,**hfont,ha='left',va='bottom')

	plt.scatter(33,-8,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(33,-8,str(tackles),c='#7b2f72',size=30,ha='center',va='center',**lfont)
	plt.text(33,-16,'Tackles',c='#2A6D32',size=12,ha='center',va='top',**lfont)


	plt.scatter(51,-8,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(51,-8,str(interceptions),c='#c7b729',size=30,ha='center',va='center',**lfont)
	plt.text(51,-16,'Interceptions',c='#2A6D32',size=12,ha='center',va='top',**lfont)

	plt.scatter(69,-8,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(69,-8,str(sucAerials),c='#2939C7',size=30,ha='center',va='center',**lfont)
	plt.text(69,-16,'Aerials won',c='#2A6D32',size=12,ha='center',va='top',**lfont)
	    
	plt.scatter(87,-8,marker='h',s=4000,facecolors='none',edgecolors='#2A6D32')
	plt.text(87,-8,str(aerial_pc),c='#2939C7',size=25,ha='center',va='center',**lfont)
	plt.text(87,-16,'Aerials won,\n%',c='#2A6D32',size=12,ha='center',va='top',**lfont)

	st.pyplot(fig)
