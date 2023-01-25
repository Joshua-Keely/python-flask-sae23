import sqlite3
from flask import *
import bcrypt
from functools import wraps

# Connects to database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        current_app.logger.info(f'Connexion à la BDD')
    return g.db
# Closes the conection to the database
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        current_app.logger.info(f'Déconnexion de la BDD')

# Fetches 'missions' from the database and inner joins with 'villes' table
def get_mission():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT id,id_aller,id_retour,id_hebergement, motif, strftime("%d/%m/%Y", debut) AS debut, strftime("%d/%m/%Y", fin) AS fin,etat,ville,x.secu,login
                      FROM missions x INNER JOIN enseignants y ON x.secu = y.secu INNER JOIN villes ON x.code = villes.code """)
    return cursor.fetchall()

# Fetches 'missions' from the database
def get_mission1():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT id, motif, strftime("%d/%m/%Y", debut) AS debut, strftime("%d/%m/%Y", fin) AS fin,etat,x.secu,login
                      FROM missions x INNER JOIN enseignants y ON x.secu = y.secu""")
    return cursor.fetchall()
# Fetchs users from the database and inner joins with the login table
def get_comptes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT x.login,nom,prenom, role AS role
                      FROM comptes x INNER JOIN enseignants y ON x.login = y.login""")
    return cursor.fetchall()
# Fetchs users from the database
def get_comptes1():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login,role AS role
                      FROM comptes """)
    return cursor.fetchall()

# Deletes a user from the database
def del_user(login):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM comptes WHERE login = :login', {'login': login})
    db.commit()
    if cursor.rowcount == 1:
        current_app.logger.info(f"Utilisateur {login=} supprimé")
        flash(f"Utilisateur {login=} supprimé")
    else:
        current_app.logger.info(f"Utilisateur {login=} pas supprimé (n'existe pas)")
        flash(f"Utilisateur {login=} pas supprimé (n'existe pas)")
    return

# Adds a user to the database
def add_user(user):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO comptes (login,mdp,role)
                        VALUES (:login, :mdp, :role)""",
                       user)
        db.commit()
        flash(f"Ajout de {user=}")
        current_app.logger.info(f"Ajout de {user=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {user=}")
        current_app.logger.info(f"Impossible d'ajouter {user=}")

# Updates users infos
def user_update(user):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE comptes SET login = :login,mdp = :mdp, role = :role WHERE login = :login""", user)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {user=}")
        current_app.logger.info(f"Modification de {user=}")
    else:
        flash(f"Impossible d'de modifier {user=}")
        current_app.logger.info(f"Impossible de modifier {user=}")




# Hashes passwords
def password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

def password_verify(password, hash):
    return bcrypt.checkpw(password.encode('utf-8'),
                          hash.encode('utf-8') if isinstance(hash, str) else hash)

def get_login(login):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login,mdp FROM comptes
                      WHERE login = :login""",
                   {'login': login})
    return cursor.fetchone()


def check_login(login, password):
    user = get_login(login)
    return user is not None and password_verify(password, user['mdp'])


# Requires a valid session to view page
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        flash("Veuillez vous identifier")
        return redirect(url_for('login'))
    return wrap

def get_infos(login):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT secu,login,prenom,nom,strftime("%d/%m/%Y", naissance) AS naissance,email,tel,urgence FROM enseignants WHERE login = :login""",{'login': login})
    return cursor.fetchone()


def get_demande(secu):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT id,motif,code,strftime("%d/%m/%Y", debut) AS debut, strftime("%d/%m/%Y", fin) AS fin,repas,id_aller,id_retour,id_hebergement,etat,secu FROM missions WHERE secu = :secu""",{'secu': secu})
    return cursor.fetchall()


def update_infos(user):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE enseignants SET secu = :secu, nom = :nom,prenom = :prenom,naissance = :naissance,email= :email,tel = :tel,urgence = :urgence  WHERE login = :login""", user)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {user=}")
        current_app.logger.info(f"Modification de {user=}")
    else:
        flash(f"Impossible d'de modifier {user=}")
        current_app.logger.info(f"Impossible de modifier {user=}")

def get_table(login):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login FROM enseignants
                      WHERE login = :login""",
                   {'login': login})
    return cursor.fetchone()

def get_admin():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login FROM comptes WHERE role = 'chef'""")
    return cursor.fetchall()


def get_administratif():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login FROM comptes WHERE role = 'administratif'""")
    return cursor.fetchall()

def get_adminlogin(login):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login FROM comptes WHERE role = 'chef' AND login=:login""",{'login': login})
    return cursor.fetchone()

def get_depense():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM depenses """)
    return cursor.fetchall()

def get_administratiflogin(login):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login FROM comptes WHERE role = 'administratif' AND login=:login""",{'login': login})
    return cursor.fetchone()


def add_infos(user):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO enseignants (login,secu,nom,prenom,naissance,email,tel,urgence)
                        VALUES (:login, :secu, :nom,:prenom,:naissance,:email,:tel,:urgence)""",
                       user)
        db.commit()
        flash(f"Ajout de {user=}")
        current_app.logger.info(f"Ajout de {user=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {user=}")
        current_app.logger.info(f"Impossible d'ajouter {user=}")



def get_loginsecu():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT login
                      FROM enseignants INNER JOIN missions ON enseignants.secu = missions.secu""")
    return cursor.fetchall()

# Requires an admin role to view page
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if get_adminlogin(session['login']) is not None:
            return f(*args, **kwargs)
        flash("Page non autorisée")
        return redirect(url_for('accueil'))
    return wrap

def administratif_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if get_administratiflogin(session['login']) is not None:
            return f(*args, **kwargs)
        flash("Page non autorisée")
        return redirect(url_for('accueil'))
    return wrap


def updatesatatut(user):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE missions SET etat = :etat WHERE id = :id""", user)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {user=}")
        current_app.logger.info(f"Modification de {user=}")
    else:
        flash(f"Impossible de modifier {user=}")
        current_app.logger.info(f"Impossible de modifier {user=}")



def del_mesdeamndes(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM missions WHERE id = :id', {'id': id})
    db.commit()
    if cursor.rowcount == 1:
        current_app.logger.info(f"Utilisateur {id=} supprimé")
        flash(f"Utilisateur {id=} supprimé")
    else:
        current_app.logger.info(f"Utilisateur {id=} pas supprimé (n'existe pas)")
        flash(f"Utilisateur {id=} pas supprimé (n'existe pas)")
    return

def add_transportaller(mission):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO transports (type,debut,numero,cout)
                        VALUES (:typealler, :debutaller, :numeroaller,:coutaller)""",
                       mission)
        db.commit()
        flash(f"Ajout de {mission=}")
        current_app.logger.info(f"Ajout de {mission=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {mission=}")
        current_app.logger.info(f"Impossible d'ajouter {mission=}")

def add_transportretour(mission):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO transports (type,debut,numero,cout)
                        VALUES (:typeretour, :debutretour, :numeroretour,:coutretour)""",
                       mission)
        db.commit()
        flash(f"Ajout de {mission=}")
        current_app.logger.info(f"Ajout de {mission=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {mission=}")
        current_app.logger.info(f"Impossible d'ajouter {mission=}")

def add_hebergement(mission):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO hebergements (type,nom,adresse,code,cout)
                        VALUES (:type, :nom, :adresse,:code, :cout)""",
                       mission)
        db.commit()
        flash(f"Ajout de {mission=}")
        current_app.logger.info(f"Ajout de {mission=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {mission=}")
        current_app.logger.info(f"Impossible d'ajouter {mission=}")

def add_mission(mission):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO missions (motif,code,debut,fin,etat,secu,id_aller,id_retour,id_hebergement,repas)
                        VALUES (:motif, :code, :debut,:fin, :etat, :secu, :id_aller, :id_retour, :id_hebergement, :repas)""",
                       mission)
        db.commit()
        flash(f"Ajout de {mission=}")
        current_app.logger.info(f"Ajout de {mission=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {mission=}")
        current_app.logger.info(f"Impossible d'ajouter {mission=}")

def get_transport():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM transports ORDER BY id DESC""")
    return cursor.fetchall()

def get_hebergement():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM hebergements ORDER BY id DESC""")
    return cursor.fetchall()

def add_depenses(depenses):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO depenses (id_mission,nature,cout)
                        VALUES (:id_mission, :nature, :cout)""",
                       depenses)
        db.commit()
        flash(f"Ajout de {depenses=}")
        current_app.logger.info(f"Ajout de {depenses=}")
    except sqlite3.Error as e:
        flash(f"Impossible d'ajouter {depenses=}")
        current_app.logger.info(f"Impossible d'ajouter {depenses=}")



def del_depenses(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM depenses WHERE id = :id', {'id': id})
    db.commit()
    if cursor.rowcount == 1:
        current_app.logger.info(f"Utilisateur {id=} supprimé")
        flash(f"Utilisateur {id=} supprimé")
    else:
        current_app.logger.info(f"Utilisateur {id=} pas supprimé (n'existe pas)")
        flash(f"Utilisateur {id=} pas supprimé (n'existe pas)")
    return


def depenses_update(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE depenses SET nature = :nature,cout = :cout,id_mission = :id_mission,id = :id WHERE id = :id""", id)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {id=}")
        current_app.logger.info(f"Modification de {id=}")
    else:
        flash(f"Impossible d'de modifier {id=}")
        current_app.logger.info(f"Impossible de modifier {id=}")


def get_id_mission(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT id_mission FROM depenses WHERE id = :id""",{'id': id})
    return cursor.fetchone()


def get_code(postal):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT code FROM villes WHERE postal = :postal""",{'postal': postal})
    return cursor.fetchone()

def demande_update(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE missions SET motif = :motif,code = :code,debut = :debut,fin = :fin,repas = :repas WHERE id = :id""", id)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {id=}")
        current_app.logger.info(f"Modification de {id=}")
    else:
        flash(f"Impossible d'de modifier {id=}")
        current_app.logger.info(f"Impossible de modifier {id=}")


def demande_update1(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE transports SET type = :type,debut = :debut,numero = :numero,cout = :cout WHERE id = :id""", id)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {id=}")
        current_app.logger.info(f"Modification de {id=}")
    else:
        flash(f"Impossible d'de modifier {id=}")
        current_app.logger.info(f"Impossible de modifier {id=}")

def demande_update2(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE hebergements SET type = :type,nom = :nom,adresse = :adresse,code = :code,cout = :cout WHERE id = :id""", id)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {id=}")
        current_app.logger.info(f"Modification de {id=}")
    else:
        flash(f"Impossible d'de modifier {id=}")
        current_app.logger.info(f"Impossible de modifier {id=}")

def demande_update11(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""UPDATE missions SET motif = :motif,secu = :secu,code = :code,debut = :debut,fin = :fin,repas = :repas WHERE id = :id""", id)
    db.commit()
    if cursor.rowcount == 1:
        flash(f"Modification de {id=}")
        current_app.logger.info(f"Modification de {id=}")
    else:
        flash(f"Impossible d'de modifier {id=}")
        current_app.logger.info(f"Impossible de modifier {id=}")
