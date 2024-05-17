import os
import pandas as pd
from datetime import datetime

def clean_data(data):
    # Remove parentheses and single quotes
    cleaned_data = [line.replace('(', '').replace(')', '').replace("'", "") for line in data]
    return cleaned_data

def create_excel_from_text_files(folder_path):
    # Get the list of files in the folder
    files = os.listdir(folder_path)
    max_number=0
    processdata=[]
    # Get the maximum number from file names
    for file in files :
        if file.endswith('.txt'):
            a=file.split('.')[0]
            b=a.split('_')[1]
            if max_number<int(b):
                max_number=int(b)
                name=file.split('_')[0].split('.')[0]
    
    # Create a new Pandas DataFrame
   
    
    # Iterate through each number
    for number in range(max_number + 1):
        txt_file = f"{name}_{number}.txt"  # Adjust filename pattern as needed
        
        # Check if the file exists
        if txt_file in files:
            file_path = os.path.join(folder_path, txt_file)
            
            # Read data from the text file
            with open(file_path, 'r') as file:
                data = file.read().splitlines()
            
            # Clean the data
            cleaned_data = clean_data(data)
            
            # Create a column with file creation date as header
            creation_date = os.path.getctime(file_path)
           
            for data in cleaned_data:
                 # Split the line into columns
                 columns = data.strip().split(',')

                 # Remove the first column
                 columns = columns[1:]
                 columns.append(str(float(columns[1]) + float(creation_date)))
                 # Add creation time to the columns
                 #columns[1] = datetime.fromtimestamp(float(columns[1])).strftime('%Y-%m-%d %H:%M:%S')

                  # Join the columns back into a string and append to the processed lines
                 processdata.append(columns)
                 #header = datetime.fromtimestamp(creation_date).strftime('%Y-%m-%d')
            
            # Add cleaned data to DataFrame
    df = pd.DataFrame(processdata)        
    # Write DataFrame to Excel file
    excel_file = os.path.join(folder_path, 'output2.xlsx')
    df.to_excel(excel_file, index=False)

# Example usage
if __name__ == "__main__":
    folder_path = "."  # Put your folder path here
    create_excel_from_text_files(folder_path)
