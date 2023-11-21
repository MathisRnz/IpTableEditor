import paramiko
import time
import getpass  # Module pour masquer la saisie du mot de passe

def get_connection_details():
    ip_address = input("Entrez l'adresse IP : ")
    port = input("Entrez le numéro de port : ")
    username = input("Entrez le nom d'utilisateur administrateur : ")
    password = getpass.getpass("Entrez le mot de passe : ")
    return ip_address, port, username, password

# Obtention des détails de connexion
host, port, username, password = get_connection_details()
'''Prétraitement des règles: on récupérer les règles à appliquer, une fois la connexion SSH établie
le script procèdera directement à l'exécution de ces règles sur le serveur distant.
Lecture des règles iptables à partir du fichier "iptables_rules"'''

with open('iptables_rules', 'r') as rules_file:
    iptables_rules = rules_file.readlines()

# Création de l'instance SSHClient
ssh = paramiko.SSHClient()

# Configuration de la stratégie
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

accepted_rules = 0
rejected_rules = 0

try:
    # Connexion au serveur distant avec les détails obtenus
    ssh.connect(host, port, username, password)

    # Exécution des règles iptables sur le serveur
    for rule in iptables_rules:
        # Ignorer les lignes vides ou commençant par #
        if rule.strip() == '' or rule.strip().startswith('#'):
            continue

        # Ajoutez "sudo" pour exécuter la commande en tant que root
        command = f'{rule.strip()}'
        stdin, stdout, stderr = ssh.exec_command(command)
        time.sleep(1)  # Attendez un moment pour permettre l'exécution de la commande

        # Nom du fichier pour enregistrer les résultats
        log_filename = 'results.log'

        # Ouvrir le fichier de logs en mode 'a' pour ajouter des résultats à la fin du fichier
        with open(log_filename, 'a') as log_file:
            log_file.write("#----------------\n")
            log_file.write(f"## Règle : {rule.strip()} ##\n")

            # Affichage du résultat de chaque règle
            log_file.write(f"[Résultat : ")
            errors = stderr.read().decode('utf-8')
            if errors:
                log_file.write("Refusé - erreur]\n")
                log_file.write(errors)
                rejected_rules += 1
            else:
                log_file.write("Accepté]\n")
                accepted_rules += 1

            log_file.write("#----------------\n\n")


# Gestion des exceptions
except Exception as e:
    print(f"Une erreur s'est produite : {e}")

# Finally pour fermer la connexion SSH
finally:
    ssh.close()

# Affichage des résultats à la fin de l'exécution
print(f"Les résultats se trouvent dans le fichier : {log_filename}")
print(f"Nombre de règles acceptées : {accepted_rules}")
print(f"Nombre de règles refusées : {rejected_rules}")


 

