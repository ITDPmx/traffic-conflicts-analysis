import sys

#Importing path to generic classes
sys.path.append( '../' )

#Actual director class
from System.Director.ProjectDirector import ProjectDirector

#Calling the starter director method
ProjectDirector.go( sys.argv )
