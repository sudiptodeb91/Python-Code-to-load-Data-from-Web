#!/usr/bin/env python
# coding: utf-8

# In[38]:


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


# In[39]:


#Detecting user
user =  os.getlogin()
user


# In[40]:


#Detecting user mail (last user log in into Outlook) + asking DS password
outlook = win32com.client.Dispatch('outlook.application')
mapi = outlook.GetNamespace("MAPI")

for account in mapi.Accounts:
    email_account = account.DeliveryStore.DisplayName
email_account
mail_password = getpass.getpass()


# In[41]:


#Paths
Dollar_Exposure_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Dollar Exposure_SD_TC.csv"
PnL_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_PnL_SD_TC.csv"
VaR_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_VaR Limit_SD.csv"
CBOT_VaR_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_CBOT VaR Limit_SD.csv"
Regional_VaR_Limits = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Regional VaR Limits_SD.csv"
Oil_Protein_Sugar_VaR_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Oil,Protein,Sugar VaR Limit_SD.csv"
Ethanol_VaR_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Ethanol VaR Limit_SD.csv"
Dollar_Gamma_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Dollar Gamma Limit_SD.csv"
Stress_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Stress_SD_TC.csv"
Options = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Options_SD.csv"
Test_CSST_VaR_1 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\test_CSST_VaR_1_SD.csv"
Test_CSST_VaR_2 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\test_CSST_VaR_2_SD.csv"
Test_CSST_VaR_3 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\test_CSST_VaR_3_SD.csv"
Test_CSST_VaR_4 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\test_CSST_VaR_4_SD.csv"
Test_CSST_VaR_5 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\test_CSST_VaR_5_SD.csv"
Test_CSST_VaR_6 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\test_CSST_VaR_6_SD.csv"
VaR = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_VaR_SD.csv"
CBOT_Drawdown_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_CBOT Drawdown_SD_TC.csv"
Oil_Protein_Sugar_Drawdown_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Oil,Protein,Sugar Drawdown_SD_TC.csv"
Regional_Drawdown_Limits_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Regional Drawdown Limits_SD_TC.csv"
Ethanol_Drawdown_Limit_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Ethanol Drawdown Limit_SD_TC.csv"
PnL_Flag_Limit_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_PnL Flag Limit_SD_TC.csv"
Drawdown_Limit_TC = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Drawdown Limit_SD_TC.csv"
Vega_Scaled_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Vega Scaled Limit_SD.csv"
Dollar_Exposure_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Dollar Exposure Limit_SD.csv"
Correlated_Stress_Limit = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST_Correlated Stress Limit_SD.csv"
CSST_1 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST-1.csv"
CSST_2 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST-2.csv"
CSST_3 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST-3.csv"
CSST_4 = "C:\\Users\\" + user + "\\Cargill Inc\\RMG Risk Engine - CSST Data\\CSST-4.csv"


# In[42]:


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


# In[43]:


#Queries needed 

CSST_queries = ['CSST_Dollar Exposure_SD_TC','CSST_PnL_SD_TC','CSST_VaR Limit_SD','CSST_CBOT VaR Limit_SD','CSST_Regional VaR Limits_SD',
'CSST_Oil,Protein,Sugar VaR Limit_SD','CSST_Ethanol VaR Limit_SD','CSST_Dollar Gamma Limit_SD','CSST_Stress_SD_TC',
'CSST_Options_SD','test_CSST_VaR_1_SD','test_CSST_VaR_2_SD','test_CSST_VaR_3_SD','test_CSST_VaR_4_SD','test_CSST_VaR_5_SD',
'test_CSST_VaR_6_SD','CSST_VaR_SD','CSST_CBOT Drawdown_SD_TC','CSST_Oil,Protein,Sugar Drawdown_SD_TC',
                'CSST_Regional Drawdown Limits_SD_TC','CSST_Ethanol Drawdown Limit_SD_TC','CSST_PnL Flag Limit_SD_TC',
'CSST_Drawdown Limit_SD_TC','CSST_Vega Scaled Limit_SD','CSST_Dollar Exposure Limit_SD','CSST_Correlated Stress Limit_SD',
               'CSST-1','CSST-2','CSST-3','CSST-4']

queries = CSST_queries


# In[44]:


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


# In[45]:


#Saving Dollar Exposure TC df as .csv file
dollar_exposure_tc = dict_df['CSST_Dollar Exposure_SD_TC']
dollar_exposure_tc.to_csv(Dollar_Exposure_TC, index=False)
print('Dollar Exposure TC Saved')


# In[46]:


#Saving Dollar Exposure TC df as .csv file
pnl_tc = dict_df['CSST_PnL_SD_TC']
pnl_tc.to_csv(PnL_TC, index=False)
print('PnL TC Saved')


# In[47]:


#Saving VaR Limit df as .csv file
var_limit = dict_df['CSST_VaR Limit_SD']
var_limit.to_csv(VaR_Limit, index=False)
print('VaR Limit Saved')


# In[48]:


#Saving CBOT VaR Limit df as .csv file
cbot_var_limit = dict_df['CSST_CBOT VaR Limit_SD']
cbot_var_limit.to_csv(CBOT_VaR_Limit, index=False)
print('CBOT VaR Limit Saved')


# In[49]:


#Saving Regional VaR Limits df as .csv file
regional_var_limits = dict_df['CSST_Regional VaR Limits_SD']
regional_var_limits.to_csv(Regional_VaR_Limits, index=False)
print('Regional VaR Limits Saved')


# In[50]:


#Saving Oil,Protein,Sugar VaR Limit df as .csv file
oil_protein_sugar_var_limit = dict_df['CSST_Oil,Protein,Sugar VaR Limit_SD']
oil_protein_sugar_var_limit.to_csv(Oil_Protein_Sugar_VaR_Limit, index=False)
print('Oil,Protein,Sugar VaR Limit Saved')


# In[51]:


#Saving Ethanol VaR Limit df as .csv file
ethanol_var_limit = dict_df['CSST_Ethanol VaR Limit_SD']
ethanol_var_limit.to_csv(Ethanol_VaR_Limit, index=False)
print('Ethanol VaR Limit Saved')


# In[52]:


#Saving Dollar Gamma Limit df as .csv file
dollar_gamma_limit = dict_df['CSST_Dollar Gamma Limit_SD']
dollar_gamma_limit.to_csv(Dollar_Gamma_Limit, index=False)
print('Dollar Gamma Limit Saved')


# In[53]:


#Saving Stress TC df as .csv file
stress_tc = dict_df['CSST_Stress_SD_TC']
stress_tc.to_csv(Stress_TC, index=False)
print('Stress TC Saved')


# In[54]:


#Saving Options df as .csv file
options = dict_df['CSST_Options_SD']
options.to_csv(Options, index=False)
print('Options Saved')


# In[55]:


#Saving test_CSST_VaR_1 df as .csv file
test_CSST_VaR_1 = dict_df['test_CSST_VaR_1_SD']
test_CSST_VaR_1.to_csv(Test_CSST_VaR_1, index=False)
print('test_CSST_VaR_1 Saved')


# In[56]:


#Saving test_CSST_VaR_2 df as .csv file
test_CSST_VaR_2 = dict_df['test_CSST_VaR_2_SD']
test_CSST_VaR_2.to_csv(Test_CSST_VaR_2, index=False)
print('test_CSST_VaR_2 Saved')


# In[57]:


#Saving test_CSST_VaR_3 df as .csv file
test_CSST_VaR_3 = dict_df['test_CSST_VaR_3_SD']
test_CSST_VaR_3.to_csv(Test_CSST_VaR_3, index=False)
print('test_CSST_VaR_3 Saved')


# In[58]:


#Saving test_CSST_VaR_4 df as .csv file
test_CSST_VaR_4 = dict_df['test_CSST_VaR_4_SD']
test_CSST_VaR_4.to_csv(Test_CSST_VaR_4, index=False)
print('test_CSST_VaR_4 Saved')


# In[59]:


#Saving test_CSST_VaR_5 df as .csv file
test_CSST_VaR_5 = dict_df['test_CSST_VaR_5_SD']
test_CSST_VaR_5.to_csv(Test_CSST_VaR_5, index=False)
print('test_CSST_VaR_5 Saved')


# In[60]:


#Saving test_CSST_VaR_6 df as .csv file
test_CSST_VaR_6 = dict_df['test_CSST_VaR_6_SD']
test_CSST_VaR_6.to_csv(Test_CSST_VaR_6, index=False)
print('test_CSST_VaR_6 Saved')


# In[61]:


#Saving VaR df as .csv file
var = dict_df['CSST_VaR_SD']
var.to_csv(VaR, index=False)
print('VaR Saved')


# In[62]:


#Saving CBOT Drawdown TC df as .csv file
cbot_drawdown_tc = dict_df['CSST_CBOT Drawdown_SD_TC']
cbot_drawdown_tc.to_csv(CBOT_Drawdown_TC, index=False)
print('CBOT Drawdown TC Saved')


# In[63]:


#Saving Oil,Protein,Sugar Drawdown TC df as .csv file
oil_protein_sugar_drawdown_tc = dict_df['CSST_Oil,Protein,Sugar Drawdown_SD_TC']
oil_protein_sugar_drawdown_tc.to_csv(Oil_Protein_Sugar_Drawdown_TC, index=False)
print('Oil,Protein,Sugar Drawdown TC Saved')


# In[64]:


#Saving Regional Drawdown Limits TC df as .csv file
regional_drawdown_limits_tc = dict_df['CSST_Regional Drawdown Limits_SD_TC']
regional_drawdown_limits_tc.to_csv(Regional_Drawdown_Limits_TC, index=False)
print('Regional Drawdown Limits TC Saved')


# In[65]:


#Saving Ethanol Drawdown Limit TC df as .csv file
ethanol_drawdown_limit_tc = dict_df['CSST_Ethanol Drawdown Limit_SD_TC']
ethanol_drawdown_limit_tc.to_csv(Ethanol_Drawdown_Limit_TC, index=False)
print('Ethanol Drawdown Limit TC Saved')


# In[66]:


#Saving PnL Flag Limit TC df as .csv file
pnl_flag_limit_tc = dict_df['CSST_PnL Flag Limit_SD_TC']
pnl_flag_limit_tc.to_csv(PnL_Flag_Limit_TC, index=False)
print('PnL Flag Limit TC Saved')


# In[67]:


#Saving Drawdown Limit TC df as .csv file
drawdown_limit_tc = dict_df['CSST_Drawdown Limit_SD_TC']
drawdown_limit_tc.to_csv(Drawdown_Limit_TC, index=False)
print('Drawdown Limit TC Saved')


# In[68]:


#Saving Vega Scaled Limit df as .csv file
vega_scaled_limit = dict_df['CSST_Vega Scaled Limit_SD']
vega_scaled_limit.to_csv(Vega_Scaled_Limit, index=False)
print('Vega Scaled Limit Saved')


# In[69]:


#Saving Dollar Exposure Limit df as .csv file
dollar_exposure_limit = dict_df['CSST_Dollar Exposure Limit_SD']
dollar_exposure_limit.to_csv(Dollar_Exposure_Limit, index=False)
print('Dollar Exposure Limit Saved')


# In[70]:


#Saving Correlated Stress Limit df as .csv file
correlated_stress_limit = dict_df['CSST_Correlated Stress Limit_SD']
correlated_stress_limit.to_csv(Correlated_Stress_Limit, index=False)
print('Correlated Stress Limit Saved')


# In[71]:


#Saving CSST-1 df as .csv file
csst_1 = dict_df['CSST-1']
csst_1.to_csv(CSST_1, index=False)
print('CSST-1 Saved')


# In[72]:


#Saving CSST-2 df as .csv file
csst_2 = dict_df['CSST-2']
csst_2.to_csv(CSST_2, index=False)
print('CSST-2 Saved')


# In[73]:


#Saving CSST-3 df as .csv file
csst_3 = dict_df['CSST-3']
csst_3.to_csv(CSST_3, index=False)
print('CSST-3 Saved')


# In[74]:


#Saving CSST-4 df as .csv file
csst_4 = dict_df['CSST-4']
csst_4.to_csv(CSST_4, index=False)
print('CSST-4 Saved')


# In[ ]:




