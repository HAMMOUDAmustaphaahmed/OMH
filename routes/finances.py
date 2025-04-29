from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Depense, Paiement, Trip, Vehicule, db
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
import calendar

finances_bp = Blueprint('finances', __name__, url_prefix='/finances')

@finances_bp.route('/')
@login_required
def index():
    # Obtenir la date actuelle et le mois en cours
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Calculer les revenus totaux
    total_revenus = db.session.query(func.sum(Paiement.montant_paye)).scalar() or 0
    
    # Calculer les dépenses totales
    total_depenses = db.session.query(func.sum(Depense.montant)).scalar() or 0
    
    # Calculer les revenus du mois en cours
    revenus_mois = db.session.query(func.sum(Paiement.montant_paye)).filter(
        extract('month', Paiement.date_paiement) == current_month,
        extract('year', Paiement.date_paiement) == current_year
    ).scalar() or 0
    
    # Calculer les dépenses du mois en cours
    depenses_mois = db.session.query(func.sum(Depense.montant)).filter(
        extract('month', Depense.date_depense) == current_month,
        extract('year', Depense.date_depense) == current_year
    ).scalar() or 0
    
    # Obtenir les derniers paiements
    derniers_paiements = Paiement.query.order_by(Paiement.date_paiement.desc()).limit(5).all()
    
    # Obtenir les dernières dépenses
    dernieres_depenses = Depense.query.order_by(Depense.date_depense.desc()).limit(5).all()
    
    return render_template('finances/dashboard.html',
                          total_revenus=total_revenus,
                          total_depenses=total_depenses,
                          revenus_mois=revenus_mois,
                          depenses_mois=depenses_mois,
                          derniers_paiements=derniers_paiements,
                          dernieres_depenses=dernieres_depenses)

@finances_bp.route('/depenses')
@login_required
def depenses():
    depenses = Depense.query.order_by(Depense.date_depense.desc()).all()
    vehicules = Vehicule.query.all()
    return render_template('finances/depenses.html', depenses=depenses, vehicules=vehicules)

@finances_bp.route('/add-depense', methods=['GET', 'POST'])
@login_required
def add_depense():
    if request.method == 'POST':
        nouvelle_depense = Depense(
            categorie=request.form.get('categorie'),
            montant=request.form.get('montant'),
            date_depense=datetime.strptime(request.form.get('date_depense'), '%Y-%m-%d').date(),
            description=request.form.get('description'),
            created_by=current_user.id_user
        )
        
        # Champ optionnel pour le véhicule
        if request.form.get('id_vehicule') and request.form.get('id_vehicule') != '':
            nouvelle_depense.id_vehicule = request.form.get('id_vehicule')
        
        db.session.add(nouvelle_depense)
        db.session.commit()
        
        flash('La dépense a été ajoutée avec succès.', 'success')
        return redirect(url_for('finances.depenses'))
    
    vehicules = Vehicule.query.all()
    return render_template('finances/add_depense.html', vehicules=vehicules)

@finances_bp.route('/edit-depense/<int:depense_id>', methods=['GET', 'POST'])
@login_required
def edit_depense(depense_id):
    depense = Depense.query.get_or_404(depense_id)
    
    if request.method == 'POST':
        depense.categorie = request.form.get('categorie')
        depense.montant = request.form.get('montant')
        depense.date_depense = datetime.strptime(request.form.get('date_depense'), '%Y-%m-%d').date()
        depense.description = request.form.get('description')
        
        # Champ optionnel pour le véhicule
        if request.form.get('id_vehicule') and request.form.get('id_vehicule') != '':
            depense.id_vehicule = request.form.get('id_vehicule')
        else:
            depense.id_vehicule = None
        
        db.session.commit()
        
        flash('La dépense a été mise à jour avec succès.', 'success')
        return redirect(url_for('finances.depenses'))
    
    vehicules = Vehicule.query.all()
    return render_template('finances/edit_depense.html', depense=depense, vehicules=vehicules)

@finances_bp.route('/delete-depense/<int:depense_id>', methods=['POST'])
@login_required
def delete_depense(depense_id):
    depense = Depense.query.get_or_404(depense_id)
    
    db.session.delete(depense)
    db.session.commit()
    
    flash('La dépense a été supprimée avec succès.', 'success')
    return redirect(url_for('finances.depenses'))

@finances_bp.route('/paiements')
@login_required
def paiements():
    paiements = Paiement.query.join(Trip).order_by(Paiement.date_paiement.desc()).all()
    return render_template('finances/paiements.html', paiements=paiements)

@finances_bp.route('/rapports')
@login_required
def rapports():
    # Obtenir l'année et le mois sélectionnés (par défaut : mois en cours)
    annee = request.args.get('annee', date.today().year, type=int)
    mois = request.args.get('mois', date.today().month, type=int)
    
    # Préparer les données pour la sélection des mois et années
    années_disponibles = range(2020, date.today().year + 1)
    mois_disponibles = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    # Calculer les revenus mensuels
    revenus_mensuels = db.session.query(
        extract('day', Paiement.date_paiement).label('jour'),
        func.sum(Paiement.montant_paye).label('montant')
    ).filter(
        extract('month', Paiement.date_paiement) == mois,
        extract('year', Paiement.date_paiement) == annee
    ).group_by('jour').all()
    
    # Calculer les dépenses mensuelles
    depenses_mensuelles = db.session.query(
        extract('day', Depense.date_depense).label('jour'),
        func.sum(Depense.montant).label('montant')
    ).filter(
        extract('month', Depense.date_depense) == mois,
        extract('year', Depense.date_depense) == annee
    ).group_by('jour').all()
    
    # Convertir les résultats en dictionnaires pour faciliter l'accès
    revenus_dict = {int(jour): float(montant) for jour, montant in revenus_mensuels}
    depenses_dict = {int(jour): float(montant) for jour, montant in depenses_mensuelles}
    
    # Préparer les données pour le graphique
    jours_dans_mois = calendar.monthrange(annee, mois)[1]
    labels = [str(i) for i in range(1, jours_dans_mois + 1)]
    revenus_data = [revenus_dict.get(i, 0) for i in range(1, jours_dans_mois + 1)]
    depenses_data = [depenses_dict.get(i, 0) for i in range(1, jours_dans_mois + 1)]
    
    # Calculer les totaux par catégorie de dépense
    depenses_par_categorie = db.session.query(
        Depense.categorie,
        func.sum(Depense.montant).label('montant')
    ).filter(
        extract('month', Depense.date_depense) == mois,
        extract('year', Depense.date_depense) == annee
    ).group_by(Depense.categorie).all()
    
    categories = [cat for cat, _ in depenses_par_categorie]
    montants_categorie = [float(montant) for _, montant in depenses_par_categorie]
    
    # Calculer les statistiques de voyage par type
    voyages_par_type = db.session.query(
        Trip.type,
        func.count(Trip.id_trip).label('nombre')
    ).filter(
        extract('month', Trip.date_depart) == mois,
        extract('year', Trip.date_depart) == annee
    ).group_by(Trip.type).all()
    
    types_voyage = [type for type, _ in voyages_par_type]
    nombre_par_type = [nombre for _, nombre in voyages_par_type]
    
    return render_template('finances/rapports.html', 
                          annee=annee,
                          mois=mois,
                          années_disponibles=années_disponibles,
                          mois_disponibles=mois_disponibles,
                          labels=labels,
                          revenus_data=revenus_data,
                          depenses_data=depenses_data,
                          categories=categories,
                          montants_categorie=montants_categorie,
                          types_voyage=types_voyage,
                          nombre_par_type=nombre_par_type)

@finances_bp.route('/api/rapport-vehicule/<int:vehicule_id>')
@login_required
def rapport_vehicule(vehicule_id):
    # Obtenir l'année et le mois sélectionnés (par défaut : mois en cours)
    annee = request.args.get('annee', date.today().year, type=int)
    mois = request.args.get('mois', date.today().month, type=int)
    
    # Calculer les revenus générés par le véhicule
    revenus = db.session.query(func.sum(Trip.prix)).filter(
        Trip.id_vehicule == vehicule_id,
        extract('month', Trip.date_depart) == mois,
        extract('year', Trip.date_depart) == annee,
        Trip.etat_trip != 'Annulé'
    ).scalar() or 0
    
    # Calculer les dépenses liées au véhicule
    depenses = db.session.query(func.sum(Depense.montant)).filter(
        Depense.id_vehicule == vehicule_id,
        extract('month', Depense.date_depense) == mois,
        extract('year', Depense.date_depense) == annee
    ).scalar() or 0
    
    # Nombre de voyages effectués
    nb_voyages = Trip.query.filter(
        Trip.id_vehicule == vehicule_id,
        extract('month', Trip.date_depart) == mois,
        extract('year', Trip.date_depart) == annee,
        Trip.etat_trip != 'Annulé'
    ).count()
    
    # Répartition des dépenses par catégorie
    depenses_par_categorie = db.session.query(
        Depense.categorie,
        func.sum(Depense.montant).label('montant')
    ).filter(
        Depense.id_vehicule == vehicule_id,
        extract('month', Depense.date_depense) == mois,
        extract('year', Depense.date_depense) == annee
    ).group_by(Depense.categorie).all()
    
    categories = [cat for cat, _ in depenses_par_categorie]
    montants = [float(montant) for _, montant in depenses_par_categorie]
    
    return jsonify({
        'revenus': float(revenus),
        'depenses': float(depenses),
        'benefice': float(revenus) - float(depenses),
        'nb_voyages': nb_voyages,
        'categories': categories,
        'montants': montants
    })