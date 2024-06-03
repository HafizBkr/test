from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Flask
from config import secret_key
import mysql.connector



app = Flask(__name__)
app.secret_key = secret_key # Clé secrète nécessaire pour utiliser flash


# Fonction pour établir la connexion à la base de données MySQL de WAMP
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="budget"
    )
    conn.autocommit = True  # Ajoutez cette ligne
    return conn

# Fonction pour récupérer le solde actuel
def get_current_balance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT montant_produit FROM depenses ORDER BY date DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Fonction pour récupérer les dernières dépenses
def get_last_expenses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nom_categorie, montant_produit FROM depenses ORDER BY date DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fonction pour récupérer les derniers revenus
def get_last_incomes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT source_revenu, montant_revenu FROM revenus ORDER BY date DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/')
def dashboard():
    dernieres_depenses = get_last_expenses()
    derniers_revenus = get_last_incomes()
    solde = get_current_balance()
    return render_template('dashboard.html', dernieres_depenses=dernieres_depenses, derniers_revenus=derniers_revenus, solde=solde)



#INPUT
# Ajoutez cette fonction pour récupérer les catégories depuis la base de données
def get_categories_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nom_categorie FROM categories')  # Changer la requête selon la structure de votre table
    categories = cursor.fetchall()
    conn.close()
    return [category[0] for category in categories]

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        nouvelle_categorie = request.form['nouvelle_categorie']
        
        # Enregistrer les données dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (nom_categorie) VALUES (%s)', (nouvelle_categorie,))
        conn.close()
        
        flash('Catégorie ajoutée avec succès !', 'success')

        return redirect(url_for('categories'))  # Redirige vers la même page pour afficher le message flash

    categories = get_categories_from_db()  # Utilisez la fonction pour obtenir les catégories
    return render_template('categories.html', categories=categories)





@app.route('/budgets', methods=['GET', 'POST'])
def budgets():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        categorie = request.form['categorie']
        montant_budget = request.form['montant_budget']
        
        # Enregistrer les données dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ID de l'utilisateur actuel pour insérer dans la table
        utilisateur_id = None  
        cursor.execute('INSERT INTO budgets (utilisateur_id, categorie_id, montant_budget) VALUES (%s, %s, %s)', (utilisateur_id, categorie, montant_budget))
        conn.close()
        
        flash('Budget défini avec succès !', 'success')

        return redirect(url_for('budgets'))  # Redirige vers la même page pour afficher le message flash

    categories = get_categories_from_db()  # Fetch categories from the database
    return render_template('budgets.html', categories=categories)


@app.route('/parametres', methods=['GET', 'POST'])
def parametres():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']
        
        # Enregistrer les données dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà avec cet email
        cursor.execute('SELECT * FROM utilisateurs WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Cet email est déjà utilisé. Veuillez en choisir un autre.', 'error')
        else:
            # Insertion d'un nouvel utilisateur
            cursor.execute('INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES (%s, %s, %s)', (nom, email, mot_de_passe))
            flash('Nouvel utilisateur enregistré avec succès !', 'success')
        
        conn.close()

        return redirect(url_for('parametres'))  # Redirige vers la même page pour afficher le message flash

    return render_template('parametres.html')




# Données de test pour la visualisation
donnees_graphique = {
    'labels': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai'],
    'donnees': [1000, 1500, 800, 2000, 1200]
}

donnees_tableau = [
    {'categorie': 'Alimentation', 'budget': 500, 'depenses': 400},
    {'categorie': 'Transport', 'budget': 200, 'depenses': 250},
    {'categorie': 'Loisirs', 'budget': 300, 'depenses': 150},
    {'categorie': 'Logement', 'budget': 1000, 'depenses': 900}
]

@app.route('/visualisation')
def visualisation():
    return render_template('visualisation.html', donnees_graphique = donnees_graphique, donnees_tableau=donnees_tableau)

if __name__ == '__main__':
    app.run(debug=True)

