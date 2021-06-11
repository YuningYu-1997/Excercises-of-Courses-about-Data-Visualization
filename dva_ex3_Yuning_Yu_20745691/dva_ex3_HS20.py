import numpy as np
from bokeh.models import ColumnDataSource, Button, Select, Div
from bokeh.sampledata.iris import flowers
from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row
import pandas as pd
import random
import math

import time
# Important: You must also install pandas for the data import.


# calculate the cost of the current medoid configuration
# The cost is the sum of all minimal distances of all points to the closest medoids
def get_cost(data,medoids,k):
    length=data.shape[0]
    distance=np.zeros((length,k))
    for i in range(length):
        for j in range(k):
            distance[i,j]=np.array((abs(data.iloc[i]['sepal_length']-data.iloc[medoids[j]]['sepal_length'])+
            abs(data.iloc[i]['sepal_width']-data.iloc[medoids[j]]['sepal_width'])+
            abs(data.iloc[i]['petal_length']-data.iloc[medoids[j]]['petal_length'])+
            abs(data.iloc[i]['petal_width']-data.iloc[medoids[j]]['petal_width']))
            )#Manhattan distance
    distance_min=np.amin(distance, axis=1)
    return distance,sum(distance_min)

# implement the k-medoids algorithm in this function and hook it to the callback of the button in the dashboard
# check the value of the select widget and use random medoids if it is set to true and use the pre-defined medoids
# if it is set to false.

def k_medoids(data,method,optimal):
    # number of clusters:
    k = 3
    # Use the following medoids if random medoid is set to false in the dashboard. These numbers are indices into the
    # data array.
    if method == 'False':
        #medoids_initial = np.array([24, 74, 124])
        medoids_initial = np.array([65,79,101])
        best_distance,best_cost=get_cost(data,medoids_initial,k)
    elif method == 'Random':
        #generate 3 points randomly.
        medoids_initial = np.random.randint(0,data.shape[0],3)
        medoids_initial.sort()
        best_distance,best_cost=get_cost(data,medoids_initial,k)
    if optimal=='Y':
        print('The medoids are:',end='')
        print(medoids_initial)
        time_start=time.time()
        best_medoids=np.array(medoids_initial)
        cost_min=np.array(best_cost)
        print('Initial cost:',end='')
        print(cost_min)
        while 1:
            flag_for=False
            for i in range(data.shape[0]):
                for j in range(k):
                    if i not in best_medoids:
                        medoids=np.array(best_medoids)
                        medoids[j]=i
                        distance,cost=get_cost(data,medoids,k)
                        if cost < cost_min:
                            cost_min=cost
                            best_medoids_temp=np.array(medoids)
                            best_distance_temp=np.array(distance)
                            flag_for=True  
                #if flag_for:
                    #break
            if not flag_for:
                break
            else:
                best_medoids=np.array(best_medoids_temp)
                best_distance=np.array(best_distance_temp)
                print('The medoids change to:',end='')
                print(best_medoids)
                print('The cost is:',end='')
                print(cost_min)
        best_distance,best_cost=get_cost(data,best_medoids,k)
        time_end=time.time()
        print('Timecost:',time_end-time_start)
    max=np.zeros(k)
    index=np.argmin(best_distance, axis=1)
    best_distance_min=np.amin(best_distance, axis=1)
    for i in range(index.shape[0]):#caculate the max distance of each points in order to caculate the alpha
        for j in range(k):
            if index[i]==j:
                if best_distance_min[i] >max[j]:
                    max[j]=best_distance_min[i]
    data['color']=index#define the color and alpha of each points
    data['color']=data['color'].map({0:'red',1:'green',2:'blue'})
    for i in range(data.shape[0]):
            data.loc[i,'alpha']=(max[2]-0.7*best_distance_min[i])/max[2]
    return best_cost

# read and store the dataset
data = flowers.copy(deep=True)
data = data.drop(['species'], axis=1)
#_=k_medoids(data,'Random')
# create a color column in your dataframe and set it to gray on startup
data['color']='gray'
data['alpha']=1
# Create a ColumnDataSource from the data
source=ColumnDataSource(data=data)
p1 = figure(plot_width = 500, plot_height = 500, 
            title="Scatterplot of flower ditribution by petal length and sepal length", 
            y_axis_label='Sepal length',x_axis_label='Petal length')
p1.scatter('petal_length','sepal_length',color='color',alpha='alpha',source=source)
p2 = figure(plot_width = 500, plot_height = 500, 
            title="Scatterplot of flower ditribution by petal width and petal length", 
            y_axis_label='Petal length',x_axis_label='Petal width')
p2.scatter('petal_width','petal_length',color='color',alpha='alpha',source=source)
# Create a select widget, a button, a DIV to show the final clustering cost and two figures for the scatter plots.
select1=Select(value='False', options=['Random','False'], title="Random method")
select2=Select(value='N', options=['Y','N'], title="Need optimal?")
button=Button(label='Cluster data',default_size=12)
div=Div(text="The final cost is:",width=200, height=100)

def event(event):
    cost=k_medoids(data,select1.value,select2.value)
    cost=np.around(cost,decimals=3)
    text="The final cost is: "+str(cost)
    source.data=ColumnDataSource.from_df(data) 
    div.text=text

button.on_click(event)
it=row([column([select1,select2,button,div]),p1,p2])
# use curdoc to add your widgets to the document
curdoc().add_root(it)
curdoc().title = "DVA_ex_3"

# use on of the commands below to start your application
# bokeh serve --show dva_ex3_skeleton_HS20.py
# python -m bokeh serve --show dva_ex3_skeleton_HS20.py
# bokeh serve --dev --show dva_ex3_skeleton_HS20.py
# python -m bokeh serve --dev --show dva_ex3_skeleton_HS20.py