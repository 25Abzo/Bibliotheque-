from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Fonction pour se connecter à la base de données MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="biblio_user",
        password="password",
        database="bibliotheque"
    )

# Route principale
@app.route('/')
def index():
    return render_template('index.html')


# Gestion des livres
@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        editeur = request.form['editeur']
        annee = request.form['annee']
        genre = request.form['genre']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Livre (titre, auteur, editeur, annee_publication, genre) VALUES (%s, %s, %s, %s, %s)',
                       (titre, auteur, editeur, annee, genre))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Livre ajouté avec succès!", "success")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Livre')
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('books.html', books=books)

# Gestion des utilisateurs
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Utilisateur (nom, prenom, email, role) VALUES (%s, %s, %s, %s)',
                       (nom, prenom, email, role))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Utilisateur ajouté avec succès!", "success")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Utilisateur')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)

# Gestion des emprunts
@app.route('/borrowings', methods=['GET'])
def borrowings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.id_emprunt, u.nom AS utilisateur, l.titre AS livre, e.date_emprunt, e.date_retour_prevue
            FROM Emprunt e
            JOIN Utilisateur u ON e.id_utilisateur = u.id_utilisateur
            JOIN Livre l ON e.id_livre = l.id_livre
        """)
        borrowings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('borrowings.html', borrowings=borrowings)
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la récupération des emprunts : {err}", "danger")
        return redirect(url_for('index'))
    
@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        date_emprunt = request.form['date_emprunt']
        date_retour_prevue = request.form['date_retour_prevue']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Emprunt (id_utilisateur, id_livre, date_emprunt, date_retour_prevue)
                VALUES (%s, %s, %s, %s)
            """, (user_id, book_id, date_emprunt, date_retour_prevue))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Emprunt enregistré avec succès!", "success")
            return redirect(url_for('borrowings'))
        except mysql.connector.Error as err:
            flash(f"Erreur lors de l'enregistrement de l'emprunt : {err}", "danger")
            return redirect(url_for('borrow'))

    # Récupérer la liste des utilisateurs et des livres pour le formulaire
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Utilisateur')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM Livre')
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('borrow.html', users=users, books=books)

# Marquer un emprunt comme retourné
@app.route('/borrowings/<int:emprunt_id>/return', methods=['POST'])
def mark_as_returned(emprunt_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Emprunt SET date_retour_effective = CURDATE() WHERE id_emprunt = %s", (emprunt_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Emprunt marqué comme retourné!", "success")
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la mise à jour de l'emprunt : {err}", "danger")
    return redirect(url_for('borrowings'))

# Gestion des retours
@app.route('/returns', methods=['GET'])
def returns():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id_retour, u.nom AS utilisateur, l.titre AS livre, r.date_retour_effective, r.etat_livre
            FROM Retour r
            JOIN Emprunt e ON r.id_emprunt = e.id_emprunt
            JOIN Utilisateur u ON e.id_utilisateur = u.id_utilisateur
            JOIN Livre l ON e.id_livre = l.id_livre
        """)
        returns = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('returns.html', returns=returns)
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la récupération des retours : {err}", "danger")
        return redirect(url_for('index'))
    
@app.route('/returns/<int:emprunt_id>/add', methods=['GET', 'POST'])
def add_return(emprunt_id):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        date_retour_effective = request.form['date_retour_effective']
        etat_livre = request.form['etat_livre']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insérer les données dans la table Retour
            cursor.execute("""
                INSERT INTO Retour (id_emprunt, date_retour_effective, etat_livre)
                VALUES (%s, %s, %s)
            """, (emprunt_id, date_retour_effective, etat_livre))

            # Mettre à jour la date de retour effective dans la table Emprunt
            cursor.execute("""
                UPDATE Emprunt
                SET date_retour_effective = %s
                WHERE id_emprunt = %s
            """, (date_retour_effective, emprunt_id))

            conn.commit()
            cursor.close()
            conn.close()
            flash("Retour enregistré avec succès!", "success")
            return redirect(url_for('returns'))
        except mysql.connector.Error as err:
            flash(f"Erreur lors de l'enregistrement du retour : {err}", "danger")
            return redirect(url_for('add_return', emprunt_id=emprunt_id))

    # Récupérer les détails de l'emprunt pour pré-remplir le formulaire
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id_emprunt, u.nom AS utilisateur, l.titre AS livre, e.date_emprunt, e.date_retour_prevue
        FROM Emprunt e
        JOIN Utilisateur u ON e.id_utilisateur = u.id_utilisateur
        JOIN Livre l ON e.id_livre = l.id_livre
        WHERE e.id_emprunt = %s
    """, (emprunt_id,))
    borrowing = cursor.fetchone()
    cursor.close()
    conn.close()

    if not borrowing:
        flash("Emprunt introuvable.", "danger")
        return redirect(url_for('borrowings'))

    return render_template('add_return.html', borrowing=borrowing)

if __name__ == '__main__':
    app.run(debug=True)