import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from plotly.subplots import make_subplots
import plotly.graph_objects as go



import requests
import io
from io import BytesIO

from datetime import datetime


################################################################################################################################################
################################################   HELPER FUNCTIONS  ###########################################################################
################################################################################################################################################



#@st.cache
def load_data():

    
    cci = pd.read_csv('https://stats.oecd.org/sdmx-json/data/DP_LIVE/.CCI.../OECD?contentType=csv&detail=code&separator=comma&csv-lang=en', parse_dates=['TIME'])
    cci.drop(columns=['SUBJECT','FREQUENCY','MEASURE','Flag Codes','INDICATOR'], inplace=True)
    cci.set_index(keys=['TIME'], inplace=True)
    cci = cci.pivot_table(index=cci.index,columns=['LOCATION'],values=['Value'])
    cci = cci.droplevel(level=0, axis=1)



    
    bci = pd.read_csv('https://stats.oecd.org/sdmx-json/data/DP_LIVE/.BCI.../OECD?contentType=csv&detail=code&separator=comma&csv-lang=en', parse_dates=['TIME'])
    bci.drop(columns=['SUBJECT','FREQUENCY','MEASURE','Flag Codes','INDICATOR'], inplace=True)
    bci.set_index(keys=['TIME'], inplace=True)
    bci = bci.pivot_table(index=bci.index,columns=['LOCATION'],values=['Value'])
    bci = bci.droplevel(level=0, axis=1)
    
    
    return cci, bci




#@st.cache
def load_ciss(country_code):
    
    
    
    ''' Function to fetch data from ECB Datawarehouse'''
    
    
    country =  {'IE':'Ireland','DE':'Germany','GB':'United Kingdom','NL':'Netherlands','US':'United States','IT':'Italy','FR':'France','U2':'Europe' }
    
    if not isinstance(country_code,str):
        print('Country code not a string')
        return 
    
    if country_code not in country.keys():
        print('Coutry code not available or wrong. Check https://sdw.ecb.europa.eu/browseSelection.do?node=9689686')
        return
    
    
        
    
    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data/'           # The resource for data queries is always'data'
    flowRef ='CISS/'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    
    
    key = 'D.'+country_code+'.Z0Z.4F.EC.SS_CIN.IDX'    # Defining the dimension values, explained below

    #For more coutnries go to https://sdw.ecb.europa.eu/browseSelection.do?node=9689686

    date_today = str(datetime.today()).split()[0]

    parameters = {
        'startPeriod': '2000-01-01',  # Start date of the time series
        'endPeriod': date_today     # End of the time series
    }


    # Construct the URL: https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.CHF.EUR.SP00.A
    request_url = entrypoint + resource + flowRef + key

    # Make the HTTP request
    response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})


    data = pd.read_csv(io.StringIO(response.text))
    data = data[['TIME_PERIOD','OBS_VALUE']]
    data.rename(columns={'TIME_PERIOD':'date','OBS_VALUE':country[country_code]}, inplace=True)
    data.index = pd.to_datetime(data.date)
    
    
    return data



################################################################################################################################################
################################################   DASHBOARD DESIGN  ###########################################################################
################################################################################################################################################



#Define Layout
st.set_page_config(page_title="Economic Dashboard",page_icon=":dollar:",layout="centered")


#TITLE
st.title('ECONOMIC DASHBOARD')



#####################################################################################################################################
###################################### DOWNLOAD AND SHOW DATA FOR BCI AND CCI #######################################################
#####################################################################################################################################



#Load CCI and BCI data
data_load_state = st.text('Loading data...')
cci, bci = load_data()
data_load_state.text('Loading data...done!')

st.header('Business and Consumer Confidence')

#headers for month
latest_month = cci.loc['2019':,'IRL'].index[-1].strftime("%B-%Y")



# Define Dictioary with list of interesting countries
country_dict = {'IRL':'Ireland','DEU':'Germany','GBR':'United Kingdom','NLD':'Netherlands','POL':'Poland','ITA':'Italy','FRA':'France','OECDE':'OECD Europe' }



num_col_metric = int(len(country_dict)/2)

row1 = st.columns(num_col_metric)
row_chart1 = st.columns(num_col_metric)

row2 = st.columns(num_col_metric)
row_chart2 = st.columns(num_col_metric)



### METRICS ####
for country_code in list(country_dict.keys())[:4]:
    counter = list(country_dict).index(country_code)
    row1[counter].metric(label=country_dict[country_code], value=  np.round(cci.loc['2019':,country_code][-1],1), delta = np.round(cci.loc['2019':,country_code].diff(1)[-1],1))
    
### CHARTS ####    

fig, ax  = plt.subplots(1,4, figsize=(12,3))
fig.tight_layout()
for country_code in list(country_dict.keys())[:4]:
    counter = list(country_dict).index(country_code)
    ax[counter].plot(cci.loc['2019':,country_code],  label = 'CCI', c='purple')
    ax[counter].plot(bci.loc['2019':,country_code], label = 'BCI', c='palevioletred')
    ax[counter].axhline(100, c='k')
    ax[counter].set_ylim(90,107)
    ax[counter].legend(loc='lower right')
    ax[counter].set_title(country_dict[country_code])
    ax[counter].tick_params(axis='x',rotation=45)
      

st.pyplot(fig)
   

### METRICS ####
for country_code in list(country_dict.keys())[4:]:
    
    counter = list(country_dict).index(country_code) -4
    row2[counter].metric(label=country_dict[country_code], value=  np.round(cci.loc['2019':,country_code][-1],1), delta = np.round(cci.loc['2019':,country_code].diff(1)[-1],1))
    
    
   
fig, ax  = plt.subplots(1,4, figsize=(12,3))
fig.tight_layout()

for country_code in list(country_dict.keys())[4:]:
    counter = list(country_dict).index(country_code) -4
    ax[counter].plot(cci.loc['2019':,country_code],  label = 'CCI', c='purple')
    ax[counter].plot(bci.loc['2019':,country_code], label = 'BCI', c='palevioletred')
    ax[counter].axhline(100, c='k')
    ax[counter].set_ylim(90,107)
    ax[counter].legend(loc='lower right')
    ax[counter].set_title(country_dict[country_code])
    ax[counter].tick_params(axis='x',rotation=45)
    
st.pyplot(fig)
 
    
st.write("Latest Release: " + latest_month.title())    
    
#####################################################################################################################################
######################################## DOWNLOAD DATA CISS INDICATORS ##############################################################
#####################################################################################################################################
   
    
st.header('ECB Systematic Stress Indicators')    

country_dict = {'U2':'Europe','IE':'Ireland','DE':'Germany','GB':'United Kingdom','NL':'Netherlands','US':'United States','FR':'France' }


mosaic = """
AABCD
AAEFG

"""


fig_gauge = make_subplots(rows=2, cols=3,specs=[[{'type' : 'indicator'}]*3,[{'type' : 'indicator'}]*3])


fig, axs = plt.subplot_mosaic(mosaic, figsize=(30, 10))
fig.subplots_adjust(hspace = 0.4, wspace=0.3)
fig.suptitle('Composite Indicator of Systemic Stress', size=35)




fig_gauge = make_subplots(rows=2, cols=3,specs=[[{'type' : 'indicator'}]*3,[{'type' : 'indicator'}]*3])


count=0
for country_code in country_dict.keys():
    key = list(axs.keys())[count]
    data = load_ciss(country_code)
    
    
    
    
    
    #PLot 2
    axs[key].plot(data.loc['2000':,country_dict[country_code]], label = country_dict[country_code], c='navy')

    mean = data.loc['2005':,country_dict[country_code]].mean()
    std = data.loc['2005':,country_dict[country_code]].std()
    axs[key].axhline(mean, label = 'mean: ' + str(round(mean,2)) , c='crimson')
    
    
    axs[key].axhspan(max(0, mean-std), mean ,0,1,color='green',alpha=0.2, label = 'mean +/- 1 std')
    axs[key].axhspan(mean, mean + std,0,1,color='red',alpha=0.2, label = 'mean +/- 1 std')
    
    

    axs[key].legend(loc='upper right')
    axs[key].set_title(country_dict[country_code], size=20)
    axs[key].tick_params(axis='x',rotation=90)
    
    
    #Plot 1
    if country_code != 'FR':
        trace = go.Indicator(
                domain = {'x': [0, 1], 'y': [0, 1]},
                value = data[country_dict[country_code]].values[-1],
                mode = "gauge+number+delta",
                title = {'text': country_dict[country_code].title() },
                delta = {'reference': mean},
                gauge = {'axis': {'range': [0, 1]},
                         'steps' : [
                             {'range': [0, mean], 'color': "lightgray"},
                             {'range': [mean+std, mean+2*std], 'color': "lightsalmon"},
                             {'range': [mean+2*std, 0.8], 'color': "red"},
                             {'range': [0.8, 1], 'color': "darkred"}]                        
                        })
        
        
        
        fig_gauge.append_trace(trace, row=count//3+1, col=count%3+1)
    
    
    count +=1 
    
    
#Show Plot1   
fig_gauge.update_layout(height=600, width=770)  
st.plotly_chart(fig_gauge)
    
    
#Show Plot2
st.pyplot(fig)
st.write('Latest Update: ' + str(data.index[-1].strftime("%d-%B-%Y")))

                

#####################################################################################################################################
##################################### Custom Plot and Download of CISS data #########################################################
#####################################################################################################################################
                
country_select = st.selectbox(label='Select Country to Download data',options=country_dict.keys())


data = load_ciss(country_select)


pd.options.plotting.backend = "plotly"


fig = data[[country_dict[country_select]]].plot()

mean = data.loc['2005':,country_dict[country_select]].mean()
std = data.loc['2005':,country_dict[country_select]].std()

fig.add_hline(y=mean, line_width=1, line_color="black", opacity=1)
fig.add_hrect(y0=max(0, mean-std), y1=mean, line_width=0, fillcolor="red", opacity=0.2)
fig.add_hrect(y0=mean, y1= mean + std, line_width=0, fillcolor="green", opacity=0.2)

st.plotly_chart(fig, use_container_width=False, sharing="streamlit")


#Download CISS Data
st.download_button('Download Composite Indicator', data=data.to_csv().encode('utf-8'),file_name=country_dict[country_select]+'_ciss_ecb_'+ str(datetime.today()).split()[0]+'.csv', mime='text/csv',)


