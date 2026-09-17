import pandas as pd

print('Parsing Engine Deck...')

# Load CSV
file_dir = "C:\\Users\\cchurko3\\OneDrive - Georgia Institute of Technology\\Desktop\\Project_5_Files\\Project_5_NPSS_Release1\\"
file_path = file_dir+"engine_deck.csv"       
df = pd.read_csv(file_path,header = None)
df = df.drop(0, axis=0) # drop first row
delim = '\s+'
df = df[0].str.split(delim, expand=True)
last_col = len(df.columns)-1
df = df.drop([0,last_col],axis=1) # remove first/last whitespace columns
df.columns = df.iloc[0]         # set first row as header
df = df[1:]                     # remove first row from data
df = df.reset_index(drop=True)  # reset index
df['Case'] = range(1,len(df['Case'])+1) #reset case indices

# Save Output
output_path = file_dir+"engine_deck.csv"
df.to_csv(output_path, index=False)

print('Parsing Complete: Engine Deck Saved.')