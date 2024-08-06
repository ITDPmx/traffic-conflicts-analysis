
# import openpyxl module 
import openpyxl 
  
# Give the location of the file 
path = "gfg.xlsx"
  
# To open the workbook 
# workbook object is created 
wb_obj = openpyxl.load_workbook(path) 
  
# Get workbook active sheet object 
# from the active attribute 
sheet_obj = wb_obj.active 
  
cell_obj = sheet_obj.cell(row=2, column=1) 
  
cell_obj.value = "Modificado pa"
  
print(cell_obj.value) 

wb_obj.save(filename="out.xlsx")


"""
Celdas a tomar en cuenta:

Observador,
Ciudad,
Intersección
Clima:
[Si/No]: Soleado, Seco, Nublado, Húmedo, Lluvia
Superficie




Rows genéricas:

Datos de entidad (x2):
    1. Nombre, Parte del video, Minuto del video, Hora del evento, Usuario [id], Sexo, edad, 
    velocidad, distancia de punto de colisión, valor tc, acción de evasión, posibilidad de desviar

Descripción del evento.


Make a pydantic class that has the following properties: 
Nombre, Parte del video, Minuto del video, Hora del evento, Usuario [id], Sexo, edad, 
    velocidad, distancia de punto de colisión, valor tc, acción de evasión, posibilidad de desviar
"""

 
