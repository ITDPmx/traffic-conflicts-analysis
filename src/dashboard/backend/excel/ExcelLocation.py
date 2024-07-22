
"""
Given a formated excel, use openpyxl to open the excel, label each cell
with its row and column number, and save the excel with the new labels.

Used to generate Metadata object to know where to place the data in the excel.
"""

import openpyxl 
  
path = "data/gfg.xlsx"
  

wb_obj = openpyxl.load_workbook(path) 
  
sheet_obj = wb_obj.active 

m = 26
for i in range(1, m):
    for j in range(1, m):
        
        cell_obj = sheet_obj.cell(row=i, column=j)
        # print(cell_obj)
        try:
            cell_obj.value = "i = " + str(i) + ", j = " + str(j)
        except Exception as e:
            print(e)

wb_obj.save(filename="data/matrixV.xlsx")

