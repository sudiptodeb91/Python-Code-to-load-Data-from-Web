#CSST RE Automation with NA and Indonesia coming from RACE 

import datetime
import sys
import os 
today=datetime.datetime.today().weekday()
today

if today<5:
    print ("Weekday")
else:
    sys.exit("Weekend!")


#Import Libraries
import pandas as pd
import numpy as np
import datetime
import sys
from impala.dbapi import connect
from impala.util import as_pandas
import glob
import re
pd.set_option('display.float_format', '{:.4f}'.format)

IMPALA_HOST = 'peanut-impala.cargill.com'

##BRING IN RACE DATA

import sys
sys.path.append('RACE/')  
from FIBI_CSST_ALL import fibi_data
fibi_positions=fibi_data()   
##FIBI CBI NA, CSST NA CBI BRAZIL, CSST MEXICO, CSST INDONESIA
#Remove on Monday, 2/14
fibi_positions=fibi_positions[fibi_positions['pos_rep_group'].str.contains(('MEXICO'))]

#fibi_positions=fibi_positions[~fibi_positions['pos_rep_group'].str.contains(('CBI'))]
#fibi_positions=fibi_positions[~fibi_positions['pos_rep_group'].str.contains(('INDONESIA'))]
#fibi_positions=fibi_positions[~fibi_positions['pos_rep_group'].str.contains(('NA'))]
#fibi_positions=fibi_positions[~fibi_positions['pos_rep_group'].str.contains(('SWITZERLAND'))]

## Set time_bucket time_bucket_delivery and futures_offering_code manually. 
fibi_positions['trade_price_currency']="USD"
fibi_positions['fixed_price_currency']="USD"
fibi_positions['product_month']=pd.to_datetime(fibi_positions['product_month']).dt.normalize()
fibi_positions['trade_price']=1

fibi_positions['time_bucket_futures_offering']=fibi_positions['product_month']
fibi_positions['time_bucket_delivery']=fibi_positions['product_month']
fibi_positions['time_bucket_delivery']=pd.to_datetime(fibi_positions['time_bucket_delivery'])
fibi_positions['time_bucket_futures_offering']=pd.to_datetime(fibi_positions['time_bucket_futures_offering'])

##Physical and Invetory futures offering
fibi_positions['year'], fibi_positions['month'] = fibi_positions['time_bucket_futures_offering'].dt.year, fibi_positions['time_bucket_futures_offering'].dt.month


conds=[ (fibi_positions['month']==1),(fibi_positions['month']==2),(fibi_positions['month']==3),(fibi_positions['month']==4),
       (fibi_positions['month']==5),(fibi_positions['month']==6),(fibi_positions['month']==7),(fibi_positions['month']==8),
       (fibi_positions['month']==9),(fibi_positions['month']==10),(fibi_positions['month']==11),(fibi_positions['month']==12)]

results=[("F"),("G"),("H"),("J"),
         ("K"),("M"),("N"),("Q"),
          ("U"),("V"),("X"),("Z")]

fibi_positions['month_code']=np.select(conds,results,default=0)

fibi_positions['futures_offering_code'] = fibi_positions['futures_offering_code'].fillna("NOT ESTABLISHED")

fibi_positions.loc[(fibi_positions['position_type']=='Inventory'), 'futures_offering_code'] = fibi_positions['product_commodity'].str.title()+"."+fibi_positions['country']+fibi_positions['year'].astype(str)+fibi_positions['month_code']
fibi_positions.loc[((fibi_positions['position_type']=='Physical') & (fibi_positions['price_type']!='NFE')), 'futures_offering_code'] = fibi_positions['product_commodity'].str.title()+"."+fibi_positions['country']+fibi_positions['year'].astype(str)+fibi_positions['month_code']

#fibi_positions.loc[(fibi_positions['position_type']=='Physical')  & (fibi_positions['price_type']=='NFE')& ((fibi_positions['futures_offering_code'].str.contains('NOT ESTABLISHED'))), 'futures_offering_code'] = fibi_positions['product_commodity'].str.title()+"."+fibi_positions['country']+"."+fibi_positions['exchange_name']+fibi_positions['year'].astype(str)+fibi_positions['month_code']



#Import libraries needed. 
#Note, you may need to install the office365-rest-client on your local machine. 
import datetime as datetime
from office365.sharepoint.client_context import ClientContext;
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.auth.client_credential import ClientCredential
from requests_ntlm import HttpNtlmAuth
from office365.sharepoint.files.file import File

## Get excel from SharePoint 

#Do not change these two lines. 
site_url = "https://cargillonline.sharepoint.com/sites/RiskManagement" #DO NOT CHANGE THIS LINE 
# Auth Info
cID=os.environ['RiskManagement_clientid']
cSecret=os.environ['RiskManagement_secret']

site_url = "https://cargillonline.sharepoint.com/sites/RiskManagement/"
# File Upload Info
credentials = ClientCredential(cID, cSecret)
ctx = ClientContext(site_url).with_credentials(credentials)


web = ctx.web
ctx.load(web)
ctx.execute_query()
print("SharePoint Site Name: {0}".format(web.properties['Title']))

# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay

today = datetime.datetime.today()
report_date=(today - BDay(1))
report_date=pd.to_datetime(report_date).strftime("%Y-%m-%d")




file='CSST Risk Report - Python '+str(report_date)+'.xlsm'
#file='CSST Risk Report - Python '+'2022-02-21'+'.xlsm'


filename = 'Risk_Engine/Positions_Raw/TEST_'+file ##Create file in CDSW 

##Position Data
with open(filename, 'wb') as output_file:
#    response = File.open_binary(ctx, '/sites/RiskManagement/Shared Documents/test.xlsx')
    response = File.open_binary(ctx, '/sites/RiskManagement/Shared Documents/RACE/FIBI/CSST/'+file)

    output_file.write(response.content)

#Read in Source data
#Position Data
data=pd.read_excel(filename,sheet_name='Position Raw', engine='openpyxl')
data
data = data[~data.Volume.isnull()] #drop not populated rows

##REMOVE NA AND INDONESIA 
#data=data[~data['Reporting Group'].str.contains(('CSSTNA'))]
data=data[~data['Country'].str.contains(('Mexico'))]




## 1. Define custom mappings

source_bu_map = {
    'CSST RUSSIA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSSTNA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSSTE' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSSTSA': 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSST METNA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSST INDONESIA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSST INDIA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSST CHINA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CTS' : 'STARCHES, SWEETENERS & TEXTURIZERS',
    'CSST NA' : 'STARCHES, SWEETENERS & TEXTURIZERS',
}

race_country_map = {
    'US' :  'UNITED STATES',
    'UK' :   'UNITED KINGDOM',
}

position_type_map = {
    'BASIS' : 'PHYSICAL',
    'CASH'  : 'PHYSICAL',
    'CORN ON HAND': 'INVENTORY',
    'FLAT' : 'PHYSICAL',
    'FUTURES': 'FUTURE',
    'INVENTORY' : 'INVENTORY',
    'OPTIONS' : 'OPTION'
}

price_type_map = {
    'BASIS' : 'NFE',
    'CASH'  : 'FIXED',
    'CORN ON HAND' : 'FIXED',
    'FLAT' : 'FIXED',
    'FUTURES': 'FIXED',
    'INVENTORY' : 'FIXED',
    'OPTIONS' : 'FIXED'
}

exch_month_num = {1:"F", 2:"G", 3:"H", 4:"J", 5:"K", 6:"M",
                 7:"N", 8:"Q", 9:"U", 10:"V", 11:"X", 12:"Z" }

options_commodity = {'C ':'C-', 'SM':'SM', 'BO':'BO'}

options_cash_comm = {'C-':'CBOT CORN', 'SM':'CBOT SBM', 'BO':'CBOT SBO'}

#options_cak_size = {'C-':5000, 'SM':100, 'BO':60000}
                    
options_uom = {'C-':'BU', 'SM':'ST', 'BO':'LBS'}     



# Removing unseen white spaces
def remove_unseen(df):
    string_col = df.select_dtypes('object')
    for col in string_col:
        df[col] = df[col].str.strip()
    return df

# Uppercase all string (object) columns
def upperize(df):
    string_col = df.select_dtypes('object')
    for col in string_col:
        df[col] = df[col].str.upper()
    return df

# Extracting report date from the report name
match = re.search('\d{4}-\d{2}-\d{2}', str(filename))
report_date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
report_date=report_date.strftime('%Y%m%d')
print(report_date)
positions = data.copy()



#Org info
org_hier=pd.read_excel('Risk_Engine/Reference_Files/Finance DB- prd_internal_artemis.profit_center_reporting_unit_map_vw.xlsx')
org_hier=org_hier[['enterprise_desc','business_group_desc','region_desc','geography_desc']]
org_hier=org_hier.groupby(['enterprise_desc','business_group_desc','region_desc','geography_desc']).count()
org_hier.reset_index(inplace=True)
org_hier.rename(columns={'product_commodity':'product_commodity_org'},inplace=True)

#Load RACE org hierarchy
org_hier = org_hier.drop_duplicates()

org_hier.rename(columns={'enterprise_desc': 'enterprise',
                'business_group_desc':'business_group',
                'region_desc':'geography',
                'geography_desc':'country'},inplace=True)

#d=org_hier.business_group=='STARCHES, SWEETENERS & TEXTURIZERS'
#test=org_hier[d]

prod_hier=pd.read_excel('Risk_Engine/Reference_Files/RACE_CSST_PRODUCT_SIMPLE.xlsx')


### 3. Preprocess loaded data

#### 3.1 Cleaning


positions = remove_unseen(positions)
positions = upperize(positions)


prod_hier = upperize(prod_hier)
prod_hier = remove_unseen(prod_hier)

org_hier = upperize(org_hier)
org_hier = remove_unseen(org_hier)

#UPPERCASE source file columns to differentiate from auxialry tables
positions_col = [x.upper() for x in list(positions.columns)]
positions.columns = positions_col





#### 3.2 Matching to RACE naming standards - physicals (no options)

output = positions.copy()
output = output[~output.VOLUME.isnull()] #drop not populated rows
output['strategy_description'] = output['STRATEGY/EXPOSURE TYPE'].copy() #no changes as not a categorical RACE attribute
output.strategy_description.fillna('NOT ESTABLISHED', inplace = True)
output.drop(columns = ['PRODUCT ORIGIN', 'STRATEGY/EXPOSURE TYPE'], inplace = True) #column is not used by CSST
#assert output.isnull().sum().sum() == 0, "There is missing data in the table!"

output = output.groupby(['GROUP', 'BUSINESS GROUP', 'REPORTING GROUP', 'GEOGRAPHY', 'COUNTRY',
       'LOCATION/PLANT', 'DESK', 'MARKET ACTIVITY', 'SUB-ACTIVITY', 'strategy_description',
       'COMMODITY GROUP', 'COMMODITY', 'PRODUCT', 'TRADE TYPE', 'POSITION TYPE',
       'PURCHASE/SALE', 'PERIOD', 'UNIT OF MEASURE', 'MRC', 'PRICE SOURCE', 'EXCHANGE_NAME', 
       'TRADE_PRICE_CURRENCY','THREE_BOX_DESIGNATION']).sum()

output.reset_index(inplace = True)

a=output.COUNTRY=='BELGIUM'
b=output.DESK=='CORN'
test=output[a&b]
test

output['business_group'] = output['REPORTING GROUP'].map(source_bu_map)
assert output.business_group.isnull().sum() == 0, "Business group names are not properly mapped to RACE names"

output['country'] = output['COUNTRY']
output['country'].replace(race_country_map, inplace = True)
csst_countres = set(output.country.unique())
race_countries = sorted(org_hier.country.unique())
assert csst_countres.issubset(race_countries) , "Some CSST countries are not properly mapped to RACE names"

output = output.merge(org_hier, how = 'left', on = ['business_group', 'country'])



output['technical_reporting_date'] = pd.to_datetime(report_date)
output['position_uom'] = output['UNIT OF MEASURE']
output['market_risk_classification'] = output['MRC']
output['counterparty_legal_name'] = 'NOT ESTABLISHED'
output['grade'] = "NOT ESTABLISHED"
output['book'] = 'NOT ESTABLISHED'
output['product_line'] = 'NOT ESTABLISHED'
output['spread_identification_flag'] = "NOT ESTABLISHED"
output['reference_basis_market'] = "NOT ESTABLISHED"
output['position'] = output.VOLUME.copy()     # NEW RACE ATTRIBUTE TO COME
output['desk_name'] = output['DESK'].copy()    #no changes as not a categorical RACE attribute
output['exchange_name'] = output['EXCHANGE_NAME'].copy()
output['trade_price_currency'] = output['TRADE_PRICE_CURRENCY'].copy()
output['cash_commodity'] = output['PRODUCT'].copy()
output['price_type'] = output['POSITION TYPE'].map(price_type_map)     #use position data to derive price type
output['position_type'] = output['POSITION TYPE'].map(position_type_map)  #use mapping to aling position type
output = output.merge(prod_hier, how = 'left', on = 'cash_commodity')

#PLACEHOLDERS
output['fote_account'] = 'NOT ESTABLISHED'
output['buyer/supplier'] = 'NOT ESTABLISHED'
#output['3-box designation'] = 'NOT ESTABLISHED'
output['spread_identification_flag'] = 'NOT ESTABLISHED'
output['grade'] = 'NOT ESTABLISHED'
output['time_bucket_delivery'] = output['PERIOD']  
output['time_bucket_futures_offering'] = output['PERIOD']
#output['futures_offering_code'] = 'NOT ESTABLISHED'
output['trade_price'] = 1
#output['trade_price_currency'] = 'NOT ESTABLISHED'
output['expiry_date'] = 'NOT ESTABLISHED'
output['fixed_price'] = output['trade_price']
output['fixed_price_currency'] = output['trade_price_currency']
output['basis_price_currency']="NULL"
output['futures_price_currency']="NULL"
output['basis_price_uom']="NULL"
output['futures_price_uom']="NULL"
output['basis_component_price']="NULL"
output['futures_component_price']="NULL"


#options placehodlers
output['delta_factor'] = 'NOT ESTABLISHED'
output['underlying_instrument'] = 'NOT ESTABLISHED'
output['trade_quantity'] = 'NOT ESTABLISHED'
output['option_exercise_style'] = 'NOT ESTABLISHED'
output['option_implied_volatility'] = 'NOT ESTABLISHED'
output['put_call'] = 'NOT ESTABLISHED'
output['strike_price'] = 'NOT ESTABLISHED'
output['basis_market_region']='NOT ESTABLISHED'
output['last_trading_date']='NOT ESTABLISHED'

output['purchase_sale'] = 'PURCHASE'
output.loc[output.position <= 0.0, 'purchase_sale'] = 'SALE'




# Assign PriceHub-like CAK for L1 positions
#output.loc[output.market_risk_classification != 1, 'PRICE SOURCE'] = np.nan
output['PRICE SOURCE'].replace('NOT_DEFINED', 'NOT ESTABLISHED', inplace = True)

output['Position_cak'] = output['PRICE SOURCE']+ output.PERIOD.dt.year.astype('str')+ output.PERIOD.dt.month.map(exch_month_num)


PH_commodities = list(output['PRICE SOURCE'].unique())
PH_commodities = [x for x in PH_commodities if x == x]

cdp_date = "'" + str(report_date) + "'"

cdp_date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
cdp_date=cdp_date.strftime('%Y-%m-%d')
cdp_date = "'" + str(cdp_date) + "'"



# Creating the list of unique commodities
fut_list = "'%s'" %"','".join(list(PH_commodities))

#CDP Query to pull unique futures list for all CPS commodities
query = f"SELECT DISTINCT (full_symbol_code) \
FROM prd_product_pconn_vendor.quotes_raw \
WHERE symbol_type = 'FUT' \
AND source_code = 'CRB' \
AND symbol_primary in ({fut_list}) \
AND quote_date_time = {cdp_date}"

#print(query)


def prices()->pd.DataFrame:

    conn =connect(host=IMPALA_HOST,
              port=21050,
              auth_mechanism='GSSAPI',
              use_ssl=True, 
              database="prd_product_pconn_vendor")
    cursor = conn.cursor()
    df = pd.read_sql_query(query,conn)

    conn.close()
    return df

cdp_df=prices()

# Making the list of unique CDP CAK
cdp_cak = list(cdp_df.full_symbol_code.unique())

# Making the list of unique position CAK
pos_cak = list(output[~output.Position_cak.isnull()].Position_cak.unique())

# Making a mapping dictionary of cash to future months
cak_map_dict = {}
for cak in pos_cak:
    commod = cak[:-5]
    if len(commod) > 0:
        commod_cak = [contr for contr in cdp_cak if contr.startswith(commod)]
        if len(commod_cak)>0:
            fut_cak = [x for x in commod_cak if x >=cak]
            fut_cak = [x for x in commod_cak if x >=cak]
            if len(fut_cak)>0:
                min_cak = min(fut_cak)
            else: 
                min_cak = max(commod_cak)
            cak_map_dict[cak] = min_cak
            
output.loc[output['PRICE SOURCE'].isin(PH_commodities), 'reference_futures_offering'] = output.Position_cak.replace(cak_map_dict)
output.loc[output['PRICE SOURCE'].isin(PH_commodities), 'futures_offering_code'] = output.Position_cak.replace(cak_map_dict)

output['legal_entity']='CARGILL, INC'

flat_pos = output[['technical_reporting_date', 'enterprise', 'geography', 'country',
       'business_group', 'legal_entity', 'product_line', 'desk_name',
       'book', 'strategy_description', 'market_sector', 'market_class',
       'marketsub_class', 'commodity_group', 'product_commodity', 'grade',
       'cash_commodity', 'market_risk_classification',
       'counterparty_legal_name', 'buyer/supplier',
       'spread_identification_flag', 'THREE_BOX_DESIGNATION', 'position_type',
       'position_uom', 'price_type', 'reference_basis_market',
       'time_bucket_futures_offering',
       'time_bucket_delivery', 'option_exercise_style',
       'option_implied_volatility', 'put_call', 'strike_price',
       'underlying_instrument', 'trade_quantity', 'delta_factor',
       'fote_account', 'purchase_sale', 'position', 'futures_offering_code', 
       'trade_price', 'trade_price_currency', 'exchange_name', 'expiry_date','basis_market_region',
       'last_trading_date','fixed_price','fixed_price_currency',
                  'basis_price_currency','futures_price_currency','basis_price_uom','futures_price_uom','basis_component_price','futures_component_price']].copy()



##Physical and Invetory futures offering
flat_pos['year'], flat_pos['month'] = flat_pos['time_bucket_futures_offering'].dt.year, flat_pos['time_bucket_futures_offering'].dt.month


conds=[ (flat_pos['month']==1),(flat_pos['month']==2),(flat_pos['month']==3),(flat_pos['month']==4),
       (flat_pos['month']==5),(flat_pos['month']==6),(flat_pos['month']==7),(flat_pos['month']==8),
       (flat_pos['month']==9),(flat_pos['month']==10),(flat_pos['month']==11),(flat_pos['month']==12)]

results=[("F"),("G"),("H"),("J"),
         ("K"),("M"),("N"),("Q"),
          ("U"),("V"),("X"),("Z")]

flat_pos['month_code']=np.select(conds,results,default=0)

flat_pos['futures_offering_code'] = flat_pos['futures_offering_code'].fillna("NOT ESTABLISHED")

#flat_pos.loc[(flat_pos['position_type']=='Physical' | flat_pos['position_type']=='Inventory') && (flat_pos['futures_offering_code'] && flat_pos['price_type']!='NFE', 'reference_futures_offering'] = output.Position_cak.replace(cak_map_dict)
flat_pos.loc[(flat_pos['position_type']=='INVENTORY') & (flat_pos['futures_offering_code'].str.contains('NOT ESTABLISHED')), 'futures_offering_code'] = flat_pos['product_commodity'].str.title()+"."+flat_pos['country']+flat_pos['year'].astype(str)+flat_pos['month_code']
flat_pos.loc[(flat_pos['position_type']=='PHYSICAL') & ((flat_pos['futures_offering_code'].str.contains('NOT ESTABLISHED')) & (flat_pos['price_type']!='NFE')), 'futures_offering_code'] = flat_pos['product_commodity'].str.title()+"."+flat_pos['country']+flat_pos['year'].astype(str)+flat_pos['month_code']

flat_pos.loc[(flat_pos['position_type']=='PHYSICAL')  & (flat_pos['price_type']=='NFE')& ((flat_pos['futures_offering_code'].str.contains('NOT ESTABLISHED'))), 'futures_offering_code'] = flat_pos['product_commodity'].str.title()+"."+flat_pos['country']+"."+flat_pos['exchange_name']+flat_pos['year'].astype(str)+flat_pos['month_code']

#Remove options coming through in file
flat_pos=flat_pos.loc[ (flat_pos['position_type'] != 'OPTION' )]

flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('CS')),'futures_offering_code'] = 'cs' + flat_pos['time_bucket_futures_offering'].apply(lambda x: x.strftime('%y'))+flat_pos['time_bucket_futures_offering'].apply(lambda x: x.strftime('%m'))
flat_pos.loc[flat_pos.fixed_price_currency=='Null', 'fixed_price_currency'] = 'NOT ESTABLISHED'

##Trade Price Currency and fixed price currency 
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Corn Gluten Feed.BRAZIL')), 'fixed_price_currency'] = "BRL"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Corn Gluten Feed.BRAZIL')), 'trade_price_currency'] = "BRL"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Corn Oil.BRAZIL')), 'fixed_price_currency'] = "BRL"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Corn Oil.BRAZIL')), 'trade_price_currency'] = "BRL"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Corn Gluten Meal.BRAZIL')), 'fixed_price_currency'] = "BRL"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Corn Gluten Meal.BRAZIL')), 'trade_price_currency'] = "BRL"

flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Sugar.MEXICO')), 'fixed_price_currency'] = "USD"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Sugar.Mexico')), 'trade_price_currency'] = "USD"

flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Yellow Corn.INDONESIA')), 'fixed_price_currency'] = "USD"
flat_pos.loc[(flat_pos['futures_offering_code'].str.contains('Yellow Corn.INDONESIA')), 'trade_price_currency'] = "USD"

                                 

#RACE Options
options_date="""
select technical_reporting_date,contract_date,enterprise,geography,
        country,business_group,desk_name,book,strategy_description,fote_account,
        legal_entity,    market_sector, market_class, marketsub_class,
        commodity_group,product_commodity,grade,cash_commodity, market_risk_classification,
        counterparty_legal_name,spread_identification_flag, position_type,
        position_uom,   price_type, plant,time_bucket_delivery, option_exercise_style,
        option_implied_volatility,put_call, strike_price,underlying_instrument,
        purchase_sale,basis_component_price,fixed_price,futures_component_price,
        futures_offering_code,trade_price,trade_price_currency,
        exchange_name,counterparty_internal_external,
        basis_price_currency,futures_price_currency,`position`,open_position_original_commodity,
        fixed_price_currency, basis_market_region,last_trading_date,
        CASE WHEN position_type="Option" 
                THEN product_month
            ELSE `time_bucket_futures_offering`
            END AS `time_bucket_futures_offering`,
        CASE
            WHEN position_type='Option' THEN
                product_month
            ELSE maturity_date
            END AS expiry_date,delta_factor

From prd_product_artemis.combined_global_position_all_business_dates_vw
Where business_group = "STARCHES, SWEETENERS & TEXTURIZERS"
and technical_reporting_date='2022-02-21'
And source_system = "OPTIONS DB";

"""

options="""
select technical_reporting_date,contract_date,enterprise,geography,
        country,business_group,desk_name,book,strategy_description,fote_account,
        legal_entity,    market_sector, market_class, marketsub_class,
        commodity_group,product_commodity,grade,cash_commodity, market_risk_classification,
        counterparty_legal_name,spread_identification_flag, position_type,
        position_uom,   price_type, plant,time_bucket_delivery, option_exercise_style,
        option_implied_volatility,put_call, strike_price,underlying_instrument,
        purchase_sale,basis_component_price,fixed_price,futures_component_price,
        futures_offering_code,trade_price,trade_price_currency,
        exchange_name,counterparty_internal_external,
        basis_price_currency,futures_price_currency,`position`,open_position_original_commodity,
        fixed_price_currency, basis_market_region,last_trading_date,
        CASE WHEN position_type="Option" 
                THEN product_month
            ELSE `time_bucket_futures_offering`
            END AS `time_bucket_futures_offering`,
        CASE
            WHEN position_type='Option' THEN
                product_month
            ELSE maturity_date
            END AS expiry_date,delta_factor

From prd_product_artemis.combined_global_position_current_day_vw
Where business_group = "STARCHES, SWEETENERS & TEXTURIZERS"
And source_system = "OPTIONS DB";

"""
def options_data()->pd.DataFrame:

    conn =connect(host=IMPALA_HOST,
              port=21050,
              auth_mechanism='GSSAPI',
              use_ssl=True, 
              database="prd_product_artemis")
    cursor = conn.cursor()
    df = pd.read_sql_query(options ,conn)
    df.fillna(0)

    conn.close()
        
    
    return df
race_options=options_data()

race_options.loc[(race_options['product_commodity'] == 'Soybean Oil'),'exchange_name'] = 'XCBT'
race_options.loc[(race_options['product_commodity'] == 'Soybean Oil'),'desk_name'] = 'Oil'
race_options.loc[(race_options['product_commodity'] == 'Soybean Meal'),'exchange_name'] = 'XCBT'
race_options.loc[(race_options['product_commodity'] == 'Soybean Meal'),'desk_name'] = 'Protein'
race_options.loc[(race_options['cash_commodity'] == 'CBOT Corn Options'),'exchange_name'] = 'XCBT'
race_options.loc[(race_options['cash_commodity'] == 'CBOT Corn Options Weekly 1'),'exchange_name'] = 'XCBT'
race_options.loc[(race_options['cash_commodity'] == 'CBOT Corn Options'),'desk_name'] = 'Corn'
race_options.loc[(race_options['cash_commodity'] == 'CBOT Corn Options Weekly 1'),'desk_name'] = 'Corn'



race_options['buyer/supplier'] = 'NOT ESTABLISHED'
race_options['THREE_BOX_DESIGNATION'] = 'Discretionary'
race_options['THREE_BOX_DESIGNATION'] = race_options['THREE_BOX_DESIGNATION'].str.upper()
race_options.fillna("NOT ESTABLISHED",inplace=True)
race_options['last_trading_date'] = race_options['last_trading_date'].fillna('NOT ESTABLISHED')
race_options['basis_market_region'] = 'NOT ESTABLISHED'
race_options['reference_futures_offering'] = 'NOT ESTABLISHED'
race_options['reference_basis_market'] = 'NOT ESTABLISHED'
race_options['market_risk_classification'] = race_options['market_risk_classification'].astype(int)
race_options.head(5)
flat_pos=flat_pos.append(race_options)


##ADD IN RACE DATA 

flat_pos=flat_pos.append(fibi_positions,ignore_index=True)
flat_pos.loc[(flat_pos['country'] == 'MEXICO'),'THREE_BOX_DESIGNATION'] = 'Asset Optimization'



flat_pos['product_line']=flat_pos['product_line'].str.title()
flat_pos['desk_name']=flat_pos['desk_name'].str.title()
flat_pos['market_sector']=flat_pos['market_sector'].str.title()
flat_pos['marketsub_class']=flat_pos['marketsub_class'].str.title()
flat_pos['commodity_group']=flat_pos['commodity_group'].str.title()
flat_pos['product_commodity']=flat_pos['product_commodity'].str.title()
flat_pos['cash_commodity']=flat_pos['cash_commodity'].str.title()
flat_pos['position_type']=flat_pos['position_type'].str.title()
flat_pos['exchange_name']=flat_pos['exchange_name'].str.upper()
flat_pos['THREE_BOX_DESIGNATION']=flat_pos['THREE_BOX_DESIGNATION'].str.upper()
#flat_pos['exchange_name'].replace('Nymex','NYMEX' ,inplace = True)
#flat_pos['exchange_name'].replace('Euronext','EURONEXT' ,inplace = True)
#flat_pos['exchange_name'].replace('Bmf','BMF' ,inplace = True)
#flat_pos['exchange_name'].replace('Cbot','CBOT' ,inplace = True)
flat_pos['market_risk_classification'] = flat_pos['market_risk_classification'].fillna(4)
#flat_pos['market_risk_classification'] = flat_pos['market_risk_classification'].astype(int)
flat_pos['futures_offering_code'] = flat_pos['futures_offering_code'].fillna("NOT ESTABLISHED")
flat_pos = flat_pos.replace(',','', regex=True)
flat_pos['contract_date'] =flat_pos['contract_date'].fillna("NOT ESTABLISHED") 
flat_pos['trade_price_currency']=flat_pos['trade_price_currency'].fillna('NOT ESTABLISHED')


flat_pos=flat_pos.loc[ (flat_pos.market_risk_classification != "NOT ESTABLISHED" )]
flat_pos=flat_pos.loc[ (flat_pos.market_risk_classification != "NotProvided" )]
flat_pos['market_risk_classification'] = flat_pos['market_risk_classification'].astype(int)

#flat_pos=flat_pos.loc[ (flat_pos.market_risk_classification < 3 )]

#flat_pos.drop(columns={'year','month','month_code'},inplace=True)

flat_pos=flat_pos.loc[ (flat_pos.price_type != "NFE" )]


flat_pos = flat_pos[['technical_reporting_date', 'enterprise', 'geography', 'country',
       'business_group', 'legal_entity', 'product_line', 'desk_name',
       'book', 'strategy_description', 'market_sector', 'market_class',
       'marketsub_class', 'commodity_group', 'product_commodity', 'grade',
       'cash_commodity', 'market_risk_classification',
       'counterparty_legal_name', 'buyer/supplier',
       'spread_identification_flag', 'THREE_BOX_DESIGNATION', 'position_type',
       'position_uom', 'price_type', 'reference_basis_market',
       'time_bucket_futures_offering',
       'time_bucket_delivery', 'option_exercise_style',
       'option_implied_volatility', 'put_call', 'strike_price',
       'underlying_instrument', 'trade_quantity', 'delta_factor',
       'fote_account', 'purchase_sale', 'position','open_position_original_commodity', 'futures_offering_code', 
       'trade_price', 'trade_price_currency', 'exchange_name', 'expiry_date','basis_market_region',
       'last_trading_date','contract_date','fixed_price','fixed_price_currency',
        'basis_price_currency','futures_price_currency','basis_price_uom','futures_price_uom','basis_component_price','futures_component_price']]


flat_pos.rename(columns={'THREE_BOX_DESIGNATION':'three_box_designation'},inplace=True)
flat_pos.loc[((flat_pos['position_type']=='Option')  & (flat_pos['product_commodity']=='Soybean Meal')), 'three_box_designation'] = 'ASSET OPTIMIZATION'
##Remove India Corn--TEMP 
#flat_pos=flat_pos.loc[~(flat_pos['futures_offering_code'].str.contains('Yellow Corn.INDIA'))]


## SAVE FILES

#positions = "Risk_Engine/RE_Data_Upload/POSITIONS_FIBI_CSST_POS_TEST"+report_date+'.csv'
#flat_pos.to_csv(positions,index=False)
#flat_pos.to_csv('Risk_Engine/RE_Data_Upload/POSITIONS_FIBI_CSST_POS_TEST.csv',index=False)

positions = 'Risk_Engine/RE_Data_Upload/VOLUMETRIC_POSITIONS_FIBI_CSST.csv'
#flat_pos.to_csv(positions,index=False)
flat_pos.to_csv('Risk_Engine/RE_Data_Upload/VOLUMETRIC_POSITIONS_FIBI_CSST.csv',index=False)





import os

import datetime as datetime
#pip install office365-rest-client --user
#pip install requests_ntlm --user
from office365.sharepoint.client_context import ClientContext;
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.auth.client_credential import ClientCredential
from requests_ntlm import HttpNtlmAuth

#Set proxies!
import os
import datetime as datetime


#Do not change these two lines. 
site_url = "https://cargillonline.sharepoint.com/sites/RiskManagement" #DO NOT CHANGE THIS LINE 
# Auth Info
import os
cID=os.environ['RiskManagement_clientid']
cSecret=os.environ['RiskManagement_secret']
site_url = "https://cargillonline.sharepoint.com/sites/RiskManagement/"
# File Upload Info
credentials = ClientCredential(cID, cSecret)
ctx = ClientContext(site_url).with_credentials(credentials)


web = ctx.web
ctx.load(web)
ctx.execute_query()
print("SharePoint Site Name: {0}".format(web.properties['Title']))



#Local file Path--set location where you want the file


#fileLocalPath = positions

#Set upload folder
documentLibraryName = "Shared Documents/RACE/FIBI/CSST_Volumetric_Positions/"

#for CSST, change to CSST
target_folder =site_url+documentLibraryName

target_folder

# Auth Info
import os
cID=os.environ['RiskManagement_clientid']
cSecret=os.environ['RiskManagement_secret']
site_url = "https://cargillonline.sharepoint.com/sites/RiskManagement/"

credentials = ClientCredential(cID, cSecret)
ctx = ClientContext(site_url).with_credentials(credentials)

web = ctx.web
ctx.load(web)
ctx.execute_query()
print("SharePoint Site Name: {0}".format(web.properties['Title']))



target_folder = ctx.web.folders.add(documentLibraryName)
ctx.execute_query()


fileLocalPath = positions
#Uploading the file to SharePoint
with open(fileLocalPath, 'rb') as content_file:
    file_content = content_file.read()
    targetFolder = target_folder
    fileName = os.path.basename(fileLocalPath)
    targetFile = targetFolder.upload_file(fileName, file_content)
    ctx.execute_query()
    print(fileName + " saved to RE SharePoint")
    

    
    
    
    

    

    


