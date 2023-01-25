from flask import *
import db
from functools import wraps
from flask_session import Session
app = Flask(__name__)
app.config['DATABASE'] = 'bdd/bdd.sqlite'
app.config['SECRET_KEY'] = 'ea77e3762774bfa237e25fabedc1194b392e8059f7b02e3ed3c3da08780dfece'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.teardown_appcontext(db.close_db)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')
    if db.check_login(login, password):
        flash("Connexion réussie")
        session['login'] = login
        return redirect(url_for('accueil'))
    flash("Identifiants invalides")
    return redirect(url_for('login'))
# Function to logout a user
@app.route('/logout')
def logout():
    if 'login' in session:
        session.pop('login')
        flash('Déconnexion réussie')
    return redirect(url_for('login'))



# Home page displaying various informations
@app.route('/', methods=['GET', 'POST'])
@db.login_required
def accueil():
    login = session['login']
    if db.get_table(login) is not None:
        return render_template('accueil.html', user=session['login'], mission=db.get_mission())
    else:
        if request.method == 'GET':
            return render_template('add_infos.html', user=session['login'])
        else:
            user = {
                'secu': request.form.get('secu'),
                'nom': request.form.get('nom'),
                'prenom': request.form.get('prenom'),
                'naissance': request.form.get('naissance'),
                'email': request.form.get('email'),
                'tel': request.form.get('tel'),
                'urgence': request.form.get('urgence'),
                'login': request.form.get('login'),
            }
            db.add_infos(user)
            return redirect(url_for('accueil'))


# Function to add a user
@app.route('/comptes/add', methods=['GET', 'POST'])
@db.login_required
def comptes_add():
    if request.method == 'GET':
        return render_template('comptes_add.html')
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'login': request.form.get('login'),
            'mdp': db.password_hash(request.form.get('mdp')),
            'role': request.form.get('role'),
        }
        db.add_user(user)
        return redirect(url_for('admin'))

# Adds personal infos to a newly created user
@app.route('/infos/add/<login>', methods=['GET', 'POST'])
@db.login_required
def infos_add(login):
    if request.method == 'GET':
        return render_template('infos_add.html',login=login)
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'secu': request.form.get('secu'),
            'nom': request.form.get('nom'),
            'prenom': request.form.get('prenom'),
            'naissance': request.form.get('naissance'),
            'email': request.form.get('email'),
            'tel': request.form.get('tel'),
            'urgence': request.form.get('urgence'),
            'login': request.form.get('login'),
        }
        db.add_user(user)
        return redirect(url_for('comptes'))


# Function to delete a user from the database
@app.route('/comptes/del/<login>')
@db.login_required
def comptes_del(login):
    db.del_user(login)
    return redirect(url_for('admin'))

# Fetches and displays the 'mesdemandes' page
@app.route('/mesdemandes/del/<id>')
@db.login_required
def demandes_del(id):
    db.del_mesdeamndes(id)
    return redirect(url_for('mesdemandes'))


# Edit a users information
@app.route('/comptes/edit/<login>',methods=['GET', 'POST'])
def comptes_edit(login):
    if request.method == 'GET':
        return render_template('comptes_edit.html',user=login)
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'login': request.form.get('login'),
            'mdp': db.password_hash(request.form.get('mdp')),
            'role': request.form.get('role'),
        }
        db.user_update(user)
        return redirect(url_for('admin'))





@app.route('/mesinfos', methods=['GET', 'POST'])
@db.login_required
def mesinfos():
    return render_template('mesinfos.html',user=session['login'], infos=db.get_infos(session['login']))

@app.route('/mesdemandes', methods=['GET', 'POST'])
@db.login_required
def mesdemandes():
    infos = db.get_infos(session['login'])
    return render_template('mesdemandes.html',user=session['login'], infos=db.get_demande(infos["secu"]))




@app.route('/mesdemandes/infos/<login>',methods=['GET', 'POST'])
@db.login_required
def update_infos(login):
    if request.method == 'GET':
        secu = db.get_infos(login)
        return render_template('update_infos.html',user=login,secu=secu['secu'])
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'secu': request.form.get('secu'),
            'nom': request.form.get('nom'),
            'prenom': request.form.get('prenom'),
            'naissance': request.form.get('naissance'),
            'email': request.form.get('email'),
            'tel': request.form.get('tel'),
            'urgence': request.form.get('urgence'),
            'login': request.form.get('login'),
        }
        db.update_infos(user)
        return redirect(url_for('mesinfos'))


@app.route('/mesdemandes/add/<login>', methods=['GET', 'POST'])
@db.login_required
def demandes_add(login):
    if request.method == 'GET':
        return render_template('add_demandes.html',login=login, secu=db.get_infos(login)['secu'])
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        missions = {
            'typealler': request.form.get('typealler'),
            'numeroaller': request.form.get('numeroaller'),
            'coutaller': request.form.get('coutaller'),
            'debutaller': request.form.get('debutaller'),
            'typeretour': request.form.get('typeretour'),
            'numeroretour': request.form.get('numeroretour'),
            'coutretour': request.form.get('coutretour'),
            'debutretour': request.form.get('debutretour'),
        }
        db.add_transportaller(missions)
        db.add_transportretour(missions)
        return redirect(url_for(f'demandes_add1', login=login,missions=missions))

@app.route('/mesdemandes/add1/<login>', methods=['GET', 'POST'])
@db.login_required
def demandes_add1(login):
        if request.method == 'GET':
            return render_template('add_demandes1.html', login=login, secu=db.get_infos(login)['secu'])
        else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
            missions1 = {
                'type': request.form.get('type'),
                'nom': request.form.get('nom'),
                'adresse': request.form.get('adresse'),
                'code': db.get_code(request.form.get('code'))['code'],
                'cout': request.form.get('cout'),
            }
            db.add_hebergement(missions1)
            return redirect(url_for(f'demandes_add2', login=login))

@app.route('/mesdemandes/add2/<login>', methods=['GET', 'POST'])
@db.login_required
def demandes_add2(login):
        if request.method == 'GET':
            return render_template('add_demandes2.html', login=login, secu=db.get_infos(login)['secu'])
        else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
            missions2 = {
                'motif': request.form.get('motif'),
                'code': db.get_code(request.form.get('code'))['code'],
                'debut': request.form.get('debut'),
                'fin': request.form.get('fin'),
                'repas': request.form.get('repas'),
                'etat': request.form.get('etat'),
                'secu': request.form.get('secu'),
                'id_aller': db.get_transport()[0]["id"],
                'id_retour': db.get_transport()[1]["id"],
                'id_hebergement': db.get_hebergement()[0]["id"],
            }
            db.add_mission(missions2)
            return redirect(url_for(f'mesdemandes', login=login))









@app.route('/anuaire', methods=['GET', 'POST'])
@db.login_required
def comptesanuaire():
    return render_template('comptes_anuaire.html',user=session['login'], comptes=db.get_comptes(),admin=db.get_admin(),administratif=db.get_administratif())

@app.route('/admin')
@db.login_required
@db.admin_required
def admin():
    return render_template('comptes.html',user=session['login'], comptes=db.get_comptes1(),admin=db.get_admin(),administratif=db.get_administratif())


@app.route('/admindemandes')
@db.login_required
@db.admin_required
def admindemandes():
    return render_template('admindemandes.html',mission=db.get_mission(),login=db.get_loginsecu())


@app.route('/demandes/edit/<id>',methods=['GET', 'POST'])
def demandesedit(id):
    if request.method == 'GET':
        return render_template('demandesedit.html',id=id)
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'id': request.form.get('id'),
            'etat': request.form.get('etat'),
        }
        db.updatesatatut(user)
        return redirect(url_for('admindemandes'))

@app.route('/depenses', methods=['GET', 'POST'])
@db.login_required
@db.administratif_required
def depenses():
    return render_template('depenses.html',user=session['login'],mission=db.get_mission(), depenses=db.get_depense(),admin=db.get_admin(),administratif=db.get_administratif())



@app.route('/add/depenses', methods=['GET', 'POST'])
@db.login_required
@db.administratif_required
def add_depenses():
    if request.method == 'GET':
        return render_template('add_depenses.html',missions=db.get_mission1())
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        depenses = {
            'id_mission': request.form.get('id_mission'),
            'nature': request.form.get('nature'),
            'cout': request.form.get('cout'),
        }
        db.add_depenses(depenses)
        return redirect(url_for('depenses'))

@app.route('/depenses/del/<id>')
@db.login_required
@db.administratif_required
def depenses_del(id):
    db.del_depenses(id)
    return redirect(url_for('depenses'))

@app.route('/depenses/edit/<id>',methods=['GET', 'POST'])
def depenses_edit(id):
    if request.method == 'GET':
        return render_template('depenses_edit.html',id=id,id_mission=db.get_id_mission(id)['id_mission'])
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'id': request.form.get('id'),
            'id_mission': request.form.get('id_mission'),
            'nature': request.form.get('nature'),
            'cout': request.form.get('cout'),
        }
        db.depenses_update(user)
        return redirect(url_for('depenses'))

@app.route('/demande/edit/<id>', methods=['GET', 'POST'])
def demande_edit(id):
    if request.method == 'GET':
        return render_template('edit_demande.html', id=id,secu=db.get_infos(session['login'])['secu'] )
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {

            'id': request.form.get('id'),
            'motif': request.form.get('motif'),
            'code': db.get_code(request.form.get('code'))['code'],
            'debut': request.form.get('debut'),
            'fin': request.form.get('fin'),
            'repas': request.form.get('repas'),

        }
        db.demande_update(user)
        return redirect(url_for('admin'))

@app.route('/transports/edit/<id>', methods=['GET', 'POST'])
def transports_edit(id):
    if request.method == 'GET':
        return render_template('edit_transports.html', id=id,secu=db.get_infos(session['login'])['secu'] )
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'id': request.form.get('id'),
            'type': request.form.get('type'),
            'debut': request.form.get('debut'),
            'numero': request.form.get('numero'),
            'cout': request.form.get('cout'),

        }
        db.demande_update1(user)
        return redirect(url_for('mesdemandes'))


@app.route('/hebergement/edit/<id>', methods=['GET', 'POST'])
def hebergement_edit(id):
    if request.method == 'GET':
        return render_template('edit_hebergement.html', id=id,secu=db.get_infos(session['login'])['secu'] )
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {
            'id': request.form.get('id'),
            'type': request.form.get('type'),
            'nom': request.form.get('nom'),
            'adresse': request.form.get('adresse'),
            'code': request.form.get('code'),
            'cout': request.form.get('cout'),
        }
        db.demande_update2(user)
        return redirect(url_for('mesdemandes'))


@app.route('/demande/edit11/<id>', methods=['GET', 'POST'])
def demande_edit11(id):
    if request.method == 'GET':
        return render_template('edit_demande1.html', id=id,secu=db.get_infos(session['login'])['secu'] )
    else:  # request.method == 'POST' |request.args.get('login') request.args.get('name') request.args.get('mdp et date')
        user = {

            'id': request.form.get('id'),
            'motif': request.form.get('motif'),
            'code': db.get_code(request.form.get('code'))['code'],
            'debut': request.form.get('debut'),
            'fin': request.form.get('fin'),
            'repas': request.form.get('repas'),
            'secu': request.form.get('secu'),

        }
        db.demande_update(user)
        return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True, port=5005)