# about

This prototype is one of results of the research No.  1.2.1.1/18/A/003 “Use of artificial intelligence for optimization of e-mobility solutions” (https://www.itkc.lv/services). Study No.  1.2.1.1/18/A/003 is devoted to the development of an algorithm to optimize relocation and maintenance operations of shared e-vehicles. The prototype implements algorithm for the placement of transport equipment.

# content
app - python executables  
data - sample data fieles:  
  * car rental history file
  * file with sectors of sharder service territory 
  * list of relocators
  * list of vehicles

# hot to run
The prototype may be started ar Doceker Container:
1) data files should be updated with actual info (car rental history, sectors, list of relocators and list of vehicles)
2) if Doceker Desktop is installed the prototype may be loaded using
``` docker build -t fiqsy-optim-new . ```
3) when docker execution is finished, resulting output data (relocator and vehicle movements) are available in container output

# contacts
Ivo Oditis  
ivo.oditis[at]di.lv  
SIA Divi Grupa  
