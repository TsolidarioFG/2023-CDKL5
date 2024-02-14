#funciones automatizadas para tareas periodicas
from django.utils import timezone
from login import models
from login.services import deleteUserData, deleteOrphanSocios 
def delete_incomplete_users():
    f = open("/home/cdkl5app/logFile.txt", "a")
    f.write("Deleted Data at " + str(timezone.now()) + "\n")
    toDeleteUsers = models.Users.objects.filter(incomplete=True)
    for user in toDeleteUsers:
        f.write("  -  user " + str(user.id) + " isObsolete=" + str(user.is_obsolete) + "\n")
        if user.is_obsolete: 
            deleteUserData(user.id) # borrar todos los usuarios con un registro incompleto
    f.write("----------------------------------------------------------" + "\n")
    f.close()
    deleteOrphanSocios() #borrar socios sin usuario que se hayan podido colar
