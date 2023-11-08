import paramiko
import time

# Parametres de connexion SSH
host = '127.0.0.1'
port = 22
username = 'root'
password = 'root'

# Lecture des regles iptables a partir du fichier "iptables_rules"
with open('iptables_rules', 'r') as rules_file:
    iptables_rules = rules_file.readlines()

# Creation de l'instance SSHClient
ssh = paramiko.SSHClient()

# Configuration de la strategie
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connexion au serveur distant
    ssh.connect(host, port, username, password)

    # Execution des regles iptables sur le serveur
    for rule in iptables_rules:
        # Ignorer les lignes vides ou commencant par #
        if rule.strip() == '' or rule.strip().startswith('#'):
            continue

        # Ajoutez "sudo" pour executer la commande en tant que root
        command = f'sudo {rule.strip()}'
        stdin, stdout, stderr = ssh.exec_command(command)
        time.sleep(1)  # Attendez un moment pour permettre l'execution de la commande

        # Affichage du resultat de chaque regle
        print(f'Resultat de la regle "{rule.strip()}":')
        result = stdout.read().decode('utf-8')
        print(result)

        # Afficher si la regle a ete appliquee avec succes ou non
        if "Bad argument" in result:
            print("La regle n'a pas ete appliquee correctement.")
        else:
            print("La regle a ete appliquee avec succes.")

        # Enregistrement des resultats dans un fichier de logs
        with open('results.log', 'a') as log_file:
            log_file.write(f'Resultat de la regle "{rule.strip()}":\n')
            log_file.write(result)
            log_file.write('\n')

        # Enregistrez egalement les erreurs
        errors = stderr.read().decode('utf-8')
        if errors:
            with open('results.log', 'a') as log_file:
                log_file.write(f'Erreurs pour la regle "{rule.strip()}":\n')
                log_file.write(errors)
                log_file.write('\n')

finally:
    # Fermeture de la connexion SSH
    ssh.close()
