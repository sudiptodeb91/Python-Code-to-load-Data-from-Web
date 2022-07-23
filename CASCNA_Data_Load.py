#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Importing needed libraries
#import cx_Oracle
import pandas as pd
#import pyodbc
#from datetime import datetime, timedelta, date
import requests
#import json
import os
from io import StringIO
import urllib.request as urllib2

import selenium
import getpass
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 

import win32com.client

#pd.set_option('display.max_columns', 30)
#pd.set_option('display.max_rows', 1000)
#pd.set_option('display.float_format', '{:.4f}'.format)


# In[2]:


#Detecting user
user =  os.getlogin()
user


# In[3]:


#Detecting user mail (last user log in into Outlook) + asking DS password
outlook = win32com.client.Dispatch('outlook.application')
mapi = outlook.GetNamespace("MAPI")

for account in mapi.Accounts:
    email_account = account.DeliveryStore.DisplayName
email_account
mail_password = getpass.getpass()


# In[4]:


#Paths
VaR = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_VaR_SD.csv"
VaR_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_VaR_SD_TC.csv"
VaR_II = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_VaR-II_SD.csv"
VaR_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_VaR Limit_SD.csv"
Drawdown_PnL_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Drawdown PnL_SD_TC.csv"
Drawdown_VaR = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Drawdown VaR_SD.csv"
Drawdown_PnL = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Drawdown PnL_SD.csv"
Drawdown_and_Drawdown_Limit_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Drawdown and Drawdown Limit_SD_TC.csv"
VaR_Enterprise = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_VaR Enterprise_SD.csv"
Drawdown_Enterprise_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Drawdown Enterprise_SD_TC.csv"
Stress_Enterprise = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Stress Enterprise_SD.csv"
PnL_Flag_Enterprise_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_PnL Flag Enterprise_SD_TC.csv"
VaR_Streams_Enterprise = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_VaR Streams Enterprise_SD.csv"
Option_Sensitivity = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC_Option Sensitivity_SD.csv"
CASC_1 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC-1.csv"
CASC_2 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC-2.csv"
CASC_3 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC-3.csv"
CASC_4 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC-4.csv"
CASC_5 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CASCNA Data\\CASC-5.csv"


# In[5]:


#Open Chrome and log in into Risk Engine to extract token

def login(user, passwd):
    #Ids of the buttons userName, Password, Next button
    un_field = (By.ID, "i0116")
    pw_field = (By.ID, "i0118")
    next_button = (By.ID, "idSIButton9")

    #Wait till the userName field is available then send the userName
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(un_field)).send_keys(user)

    #click on the Next button
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(next_button)).click()

    #Wait till the userName field is available then send the userName
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(pw_field)).send_keys(passwd)

    #click on the Login button, has the same ID as the next button.
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(next_button)).click()

    #click on the Login button, has the same ID as the next button.
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(next_button)).click()
    
    #Wait till the url is the dashboard
    WebDriverWait(driver, 20).until(EC.url_to_be("https://cargill-prod-aer.fisglobal.com/riskui/#/dashboard/home"))
    return driver

driver = webdriver.Chrome()
driver.get('https://cargill-prod-aer.fisglobal.com/riskui')
page = driver.page_source
print("Microsoft Log In")
wait = WebDriverWait(driver, 10000).until(EC.url_contains("https://login.microsoftonline.com/"))
try:
    print('Authorizing')
    login(email_account, mail_password)
except Exception as error:
    print('Error', error)
else:
    print('Authorized')
token = driver.execute_script("return window.sessionStorage.getItem('access_token');")
print("Token acquired")
print(token)
print('Closing Chrome')
driver.close()
print('Chrome Close')


# In[6]:


#Queries needed 

CASCNA_queries = ['CASC_VaR_SD','CASC_VaR_SD_TC','CASC_VaR-II_SD','CASC_VaR Limit_SD','CASC_Drawdown PnL_SD_TC',
'CASC_Drawdown VaR_SD','CASC_Drawdown PnL_SD','CASC_Drawdown and Drawdown Limit_SD_TC','CASC_VaR Enterprise_SD',
'CASC_Drawdown Enterprise_SD_TC','CASC_Stress Enterprise_SD','CASC_PnL Flag Enterprise_SD_TC','CASC_VaR Streams Enterprise_SD',
'CASC_Option Sensitivity_SD','CASC-1','CASC-2','CASC-3','CASC-4','CASC-5']

queries = CASCNA_queries


# In[7]:


#Download one by one the Queries and put the data into a df
dict_df = {}

for queries_names in queries:
    url_1 = "https://cargill-prod-aer.fisglobal.com//"
    # url_1 = "https://cargill-uat-aer.fisglobal.com//"
    url_2 = '/AdaptivFusionInvestigationService/api/Calculations/RiskService/Calculate/Results/{}'.format(queries_names)
    myUrl = url_1 + url_2
    head = {'Authorization': 'Bearer {}'.format(token)}

    response = requests.get(myUrl, headers=head, verify=True)
    #print('Server status :',response.status_code)
    print(f'Server status:{queries_names} {response.status_code}')
    
    result = str(response.content, 'utf-8')
    data = StringIO(result)
    data_df = pd.read_csv(data)
     
    dict_df[queries_names] = data_df


# In[9]:


#Saving VaR df as .csv file
var = dict_df['CASC_VaR_SD']
var.to_csv(VaR, index=False)
print('VaR Saved')


# In[10]:


#Saving VaR TC df as .csv file
var_tc = dict_df['CASC_VaR_SD_TC']
var_tc.to_csv(VaR_TC, index=False)
print('VaR TC Saved')


# In[11]:


#Saving VaR-II df as .csv file
var_II = dict_df['CASC_VaR-II_SD']
var_II.to_csv(VaR_II, index=False)
print('VaR-II Saved')


# In[12]:


#Saving VaR Limit df as .csv file
var_limit = dict_df['CASC_VaR Limit_SD']
var_limit.to_csv(VaR_Limit, index=False)
print('VaR Limit Saved')


# In[13]:


#Saving Drawdown PnL TC df as .csv file
drawdown_pnl_tc = dict_df['CASC_Drawdown PnL_SD_TC']
drawdown_pnl_tc.to_csv(Drawdown_PnL_TC, index=False)
print('Drawdown PnL TC Saved')


# In[14]:


#Saving Drawdown VaR df as .csv file
drawdown_var = dict_df['CASC_Drawdown VaR_SD']
drawdown_var.to_csv(Drawdown_VaR, index=False)
print('Drawdown VaR Saved')


# In[15]:


#Saving Drawdown PnL df as .csv file
drawdown_pnl = dict_df['CASC_Drawdown PnL_SD']
drawdown_pnl.to_csv(Drawdown_PnL, index=False)
print('Drawdown PnL Saved')


# In[16]:


#Saving Drawdown and Drawdown Limit TC df as .csv file
drawdown_and_drawdown_limit_tc = dict_df['CASC_Drawdown and Drawdown Limit_SD_TC']
drawdown_and_drawdown_limit_tc.to_csv(Drawdown_and_Drawdown_Limit_TC, index=False)
print('Drawdown and Drawdown Limit TC Saved')


# In[17]:


#Saving VaR Enterprise df as .csv file
var_enterprise = dict_df['CASC_VaR Enterprise_SD']
var_enterprise.to_csv(VaR_Enterprise, index=False)
print('VaR Enterprise Saved')


# In[18]:


#Saving Drawdown Enterprise df as .csv file
drawdown_enterprise_tc = dict_df['CASC_Drawdown Enterprise_SD_TC']
drawdown_enterprise_tc.to_csv(Drawdown_Enterprise_TC, index=False)
print('Drawdown Enterprise TC Saved')


# In[19]:


#Saving Stress Enterprise df as .csv file
stress_enterprise = dict_df['CASC_Stress Enterprise_SD']
stress_enterprise.to_csv(Stress_Enterprise, index=False)
print('Stress Enterprise Saved')


# In[20]:


#Saving PnL Flag Enterprise df as .csv file
pnl_flag_enterprise_tc = dict_df['CASC_PnL Flag Enterprise_SD_TC']
pnl_flag_enterprise_tc.to_csv(PnL_Flag_Enterprise_TC, index=False)
print('PnL Flag Enterprise TC Saved')


# In[21]:


#Saving VaR Streams Enterprise df as .csv file
var_streams_enterprise = dict_df['CASC_VaR Streams Enterprise_SD']
var_streams_enterprise.to_csv(VaR_Streams_Enterprise, index=False)
print('VaR Streams Enterprise Saved')


# In[22]:


#Saving Option Sensitivity df as .csv file
option_sensitivity = dict_df['CASC_Option Sensitivity_SD']
option_sensitivity.to_csv(Option_Sensitivity, index=False)
print('Option Sensitivity Saved')


# In[28]:


#Saving CASC-1 df as .csv file
casc_1 = dict_df['CASC-1']
casc_1.to_csv(CASC_1, index=False)
print('CASC-1 Saved')


# In[24]:


#Saving CASC-2 df as .csv file
casc_2 = dict_df['CASC-2']
casc_2.to_csv(CASC_2, index=False)
print('CASC-2 Saved')


# In[25]:


#Saving CASC-3 df as .csv file
casc_3 = dict_df['CASC-3']
casc_3.to_csv(CASC_3, index=False)
print('CASC-3 Saved')


# In[26]:


#Saving CASC-4 df as .csv file
casc_4 = dict_df['CASC-4']
casc_4.to_csv(CASC_4, index=False)
print('CASC-4 Saved')


# In[27]:


#Saving CASC-5 df as .csv file
casc_5 = dict_df['CASC-5']
casc_5.to_csv(CASC_5, index=False)
print('CASC-5 Saved')


# In[ ]:




