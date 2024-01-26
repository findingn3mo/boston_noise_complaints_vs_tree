#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import the important information
# !pip install altair if haven't download already
import altair as alt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# In[2]:


# read the excel file
data = pd.read_excel('clean_up_data.xlsx')
data.head()


# In[3]:


data.columns


# In[4]:


# read the data file
tree = pd.read_csv('trees-by-neighborhood-full.csv')
tree = tree.dropna()

mass_ave = ['Dorchester', 'Back Bay','Roxbury', 'South End']
mass_ave_tree = tree[tree["Region"].isin(mass_ave)]
mass_ave_tree


# In[5]:


# set the constraints to be only taking noise complaints data

noise_complaints = data[(data['reason']== 'Noise Disturbance')]
mass_ave_noise_complaints = noise_complaints[noise_complaints["neighborhood"].isin(mass_ave)]
mass_ave_noise_complaints              


# In[6]:


# plot all the trees at the smallest size
tree_points = alt.Chart(mass_ave_tree).mark_point(color = 'green', size =.00001).encode(
    latitude = 'Latitude', 
    longitude = 'Longitude')
alt.data_transformers.disable_max_rows()

tree_points


# In[7]:


# plot all the points with noise complaints
noise_complaints_points = alt.Chart(mass_ave_noise_complaints).mark_point(fill = 'orange', size =40).encode(latitude = 'latitude', longitude = 'longitude', size=alt.value(20),tooltip=['count()','neighborhood'])
noise_complaints_points


# In[8]:


# plot the background of Boston
boston_url = "https://raw.githubusercontent.com/lsouth/DS4200/main/Boston_Neighborhoods.json"
boston = alt.topo_feature(boston_url, feature ='Boston_Neighborhoods')

background =alt.Chart(boston).mark_geoshape(fill='lightgray',stroke='white').encode(tooltip='properties.Name:N').properties(width=500,height=500)
background


# In[24]:


# create the two-way brushing and linking between the noise complaints and the neighboorhood
brush = alt.selection_interval()
bar_brush = alt.selection_point(fields=['neighborhood'])

# create the bar chart that shows the count of noise complaint cases in each neighborhood
neighborhood_bar = alt.Chart(mass_ave_noise_complaints).mark_bar().encode(
    x=alt.X('count()', axis=alt.Axis(title='Count of Noise Complaint Records in 2023')),
    y=alt.Y('neighborhood', axis=alt.Axis(title='Neighborhoods along Mass Ave')),
    color=alt.Color("neighborhood",legend=None),
    opacity=alt.condition(bar_brush, alt.value(1), alt.value(0.2))
).transform_filter(brush
).properties(width=200, height=350).add_params(bar_brush).interactive()

# create the scatterplot that shows the density of tree (in green) and the density of noise complaints in each neighborhood
scatterplot = alt.Chart(mass_ave_noise_complaints).mark_point(filled=True
).encode(
    latitude='latitude',
    longitude='longitude',
    color=alt.condition(brush,"neighborhood",alt.value("lightgray"))
).transform_filter(bar_brush).add_params(brush).interactive()

# create a map with the scatterplot and the tree points above it
background =alt.Chart(boston).mark_geoshape(fill='lightgray',stroke='white').encode(
    tooltip='properties.Name:N'
).properties(
    width=500,
    height=500)

full_chart = background + scatterplot + tree_points

# show one plot next to each other
full_chart | neighborhood_bar


# In[11]:


neighboorhood_bar = alt.Chart(data).mark_bar().encode(
    y="reason",
    x="count()",
).properties(width=200)
neighboorhood_bar


# ### VIZ 1:

# In[12]:


# Convert date columns to datetime format
data['open_dt'] = pd.to_datetime(data['open_dt'])

# Group the data by time intervals (e.g., monthly)
noise_complaints_by_month = data.groupby(pd.Grouper(key='open_dt', freq='M')).size()

# Create the line chart
plt.plot(noise_complaints_by_month.index, noise_complaints_by_month, label='Noise Complaints')

# Rotate x-axis tick labels
plt.xticks(rotation=45)

# Add labels and legends
plt.xlabel('Date')
plt.ylabel('Count of Noise Complaints Record')
plt.title('Temporal Analysis of Noise Complaints along Mass Ave in 2023')
plt.legend()

# Display the chart
plt.show()


# ### VIZ 2

# In[13]:


# divide the area into a 2D grid of 10x10 cells
grid_size = (10, 10)

# binning the geographical data into a grid or using predefined geographic boundary
x_bins = pd.cut(data['latitude'], bins=grid_size[0])
y_bins = pd.cut(data['longitude'], bins=grid_size[1])

# calculate the density of noise complaints within each region
density = data.groupby([x_bins, y_bins]).size().unstack().fillna(0)

# create the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(density, cmap='YlOrRd', square=True, annot=True, fmt='g')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Density of Noise Complaints')

# show the plot
plt.show()


# ### VIZ 3

# In[14]:


data['count'] = data.groupby('subject')['subject'].transform('size')

selection = alt.selection_point(fields=['subject'], bind='legend')

alt.Chart(data).mark_area().encode(
    alt.X('monthdate(open_dt):T', axis=alt.Axis(title='Time', domain=True, format='%m-%d', tickSize=0)),
    alt.Y('sum(count):Q', axis=alt.Axis(title='Time')).stack('center').axis(None),
    alt.Color('subject:N').scale(scheme='category20b'),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_params(
    selection
).properties(
    title="Noise Complaints Subjects Over Time in 2023"
)

