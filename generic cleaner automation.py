import pandas as pd 
import os 
from pathlib import Path 

# CONFIG 
INPUT_DIR='before_files'
OUTPUT_DIR='after_files'
REPORTS_DIR='reports'

MISSING_MARKERS=['',' ','?','-','--','NA','N/A','null']
ID_HINTS=['id','uuid','code']
NUMBER_HINTS=['cost','price','amount','fee','fees','total','qty','quantity','age']
ALLOW_NEGATIVE_HINTS = ['balance','profit','loss','net','change']
DATE_HINTS=['date','time','datetime','timestamp']
PICKUP_HINTS=['pickup','start','pick_up']
DROPOFF_HINTS=['dropoff','end','drop_off']

# SETUP
os.makedirs(OUTPUT_DIR,exist_ok=True)
os.makedirs(REPORTS_DIR,exist_ok=True)
os.makedirs(INPUT_DIR,exist_ok=True)

# DETECT HEADERS
def has_header(path):
    sample=pd.read_csv(path,nrows=1,header=None,sep=None,engine='python')
    first_row=sample.iloc[0].astype(str)
    alpha_ratio = first_row.str.match(r'^[A-Za-z_ ]+$').mean()
    numeric_ratio = first_row.str.match(r'^-?\d+(\.\d+)?$').mean()
    return alpha_ratio > numeric_ratio
    
# HELPERS
def load_files(path):
    if path.lower().endswith(('.csv','.data')):
        if has_header(path):
            return pd.read_csv(path,sep=None,engine='python')
        else:
            df=pd.read_csv(path,header=None,sep=None,engine='python')
            df.columns=[f'col_{i}' for i in range(df.shape[1])]
            return df
    elif path.lower().endswith('.parquet'):
        return pd.read_parquet(path)
    elif path.lower().endswith(('.xls','.xlsx')):
        return pd.read_excel(path)
    else:
        raise ValueError('FORMAT NOT SUPPORT')

def save_files(df,path):
    if path.lower().endswith('.csv'):
        outpath=os.path.join(OUTPUT_DIR,Path(path).stem+'_after_clean.csv') 
        df.to_csv(outpath,index=False)
    elif path.lower().endswith('.parquet'):
        outpath=os.path.join(OUTPUT_DIR,Path(path).stem+'_after_clean.parquet')
        df.to_parquet(outpath)
    else:
        outpath=os.path.join(OUTPUT_DIR,Path(path).stem+'_after_clean.xlsx')
        df.to_excel(outpath,index=False)
        
def standardize_cols(df):
    df.columns=(
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ','')
        .str.replace(r'[^\w_]','',regex=True)
    )
    return df 

def standardize_cols_values(df):
    for col in df.select_dtypes(include='object'):
        df[col]=df[col].str.strip()
    return df 

def is_number(col):
    return any(hint in col for hint in NUMBER_HINTS)

def is_id(col):
    return any(hint in col for hint in ID_HINTS)

def is_date(col):
    return any(hint in col for hint in DATE_HINTS)

def is_date_pickup(col):
    return any(hint in col for hint in PICKUP_HINTS) and is_date(col)

def is_date_dropoff(col):
    return any(hint in col for hint in DROPOFF_HINTS) and is_date(col)

# PIPELINE
def cleaning_pipeline(path):
    report={}
    # LOAD FILES
    df=load_files(path)
    report['ROWS BEFORE CLEANING']=len(df)
    # STANDARDIZE COLUMNS AND VALUES
    df=standardize_cols(df)
    df=standardize_cols_values(df)
    # HANDELING MISSING MARKERS
    df=df.replace(MISSING_MARKERS,pd.NA)
    # COERCED AND NEGATIVE VALUES HANDELING
    total_coerced=0
    total_negative=0
    for col in df.columns:
        if is_number(col):
            before_coerced=df[col].isna().sum()
            df[col]=pd.to_numeric(df[col],errors='coerce')
            after_coerced=df[col].isna().sum()
            total_coerced+=(after_coerced-before_coerced)
            
            # NEGATIVE VALUE FIXING
            if not any(h in col for h in ALLOW_NEGATIVE_HINTS):
                before_negative=(df[col]<0).sum()
                df.loc[df[col]<0,col]=pd.NA
                after_negative=(df[col]<0).sum()
                total_negative+=(before_negative-after_negative)
            
    report['COERCED VALUES']=total_coerced
    report['NEGATIVE FIXED']=total_negative
    
    # COERCED WRONG DATE
    total_date_coerced=0
    for col in df.columns:
        if is_date(col):
            before_date=df[col].isna().sum()
            df[col]=pd.to_datetime(df[col],errors='coerce')
            after_date=df[col].isna().sum()
            total_date_coerced+=(after_date-before_date)
    if total_date_coerced>0:
        report['DATE COERCED']=total_date_coerced
    
    # PUCKUP AND DROPOFF DATE FIX
    total_invalid_date=0
    date_dropoff_cols=[c for c in df.columns if is_date_dropoff(c)]
    date_pickup_cols=[c for c in df.columns if is_date_pickup(c)]
    for dropoff in date_dropoff_cols:
        for pickup in date_pickup_cols:
            count=(df[dropoff]<df[pickup]).sum()
            if count >0:
                df.loc[(df[dropoff]<df[pickup]),[dropoff,pickup]]=pd.NA
                total_invalid_date+=count
    if total_invalid_date>0:
        report['INVALID DATE TIME ROWS']=total_invalid_date
    
    # DROP ROWS WITH MISSING IMPORTANT VALUES
    important_cols=[c for c in df.columns if is_number(c) or is_id(c)]
    if important_cols:
        before_droped=len(df)
        df=df.dropna(subset=important_cols)
        after_droped=len(df)
        total_droped=before_droped-after_droped
        report['ROWS WITH IMPORTANT VALUES MISSING DROPPED']=total_droped
    
    # DROP DUPLICATES
    before_dup=df.duplicated().sum()
    df=df.drop_duplicates()
    report['DUPLICATES REMOVED']=before_dup
    report['ROWS AFTER CLEANING']=len(df)
    return df,report

# MAIN AUTOMATION
def main():
    files=os.listdir(INPUT_DIR)
    print('----CLEANING AUTOMATION STARTED-----')
    for file in files:
        print('------NEW FILE DETECTED------')
        print(f'PROCESSING FILE->{file}')
        if not file.lower().endswith(('.csv','.xlsx','.xls','.parquet','.data')):
            print(f'FILE SKIPPED->{file}')
            continue
        inputpath=os.path.join(INPUT_DIR,file)
        cleaned_df,report=cleaning_pipeline(inputpath)
        
        # SAVING FILE
        outpath=os.path.join(OUTPUT_DIR,file)
        save_files(cleaned_df,outpath)
        print(f'FILE SAVED->{file}')
        
        # CREATING REPORT
        reportpath=os.path.join(REPORTS_DIR,Path(file).stem+'_report.txt') 
        with open(reportpath,'w') as f:
            for k,v in report.items():
                f.write(f'{k}={v}\n')
        print(f'REPORT SAVED->{Path(file).stem}_report.txt\n')
    print('----CLEANING AUTOMATION COMLETED----')
    
# ENTRY POINT
if __name__=='__main__':
    main()