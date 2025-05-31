from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from models import Trip, TripAffectation, TripDepense, Paiement, Vehicule, Chauffeur, db
from datetime import datetime
from sqlalchemy import func, or_
import pandas as pd
import io
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

def generate_trip_code():
    """Génère un code unique pour le voyage: AA-XXXX où AA=année et XXXX=séquence"""
    try:
        year_short = datetime.now().strftime('%y')
        # Changement ici : on cherche le dernier voyage par ordre décroissant
        last_trip = db.session.query(Trip).filter(
            Trip.code_voyage.like(f'{year_short}-%')
        ).order_by(Trip.code_voyage.desc()).first()

        if last_trip and last_trip.code_voyage:
            try:
                last_number = int(last_trip.code_voyage.split('-')[1])
                new_number = str(last_number + 1).zfill(4)  # Padding avec des zéros
            except (IndexError, ValueError):
                new_number = '0001'
        else:
            new_number = '0001'

        return f"{year_short}-{new_number}"
    except Exception as e:
        logger.error(f"Erreur lors de la génération du code : {str(e)}")
        # Code de secours basé sur le timestamp
        return f"{datetime.now().strftime('%y-%m%d%H%M')}"

@trips_bp.route('/')
@login_required
def index():
    """Page principale de gestion des voyages"""
    return render_template('trips/manage.html')

@trips_bp.route('/data')
@login_required
def trips_data():
    """API pour obtenir les données des voyages (pour DataTable/AJAX)"""
    search = request.args.get('search', '').strip()
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    trip_type = request.args.get('type')
    sort_by = request.args.get('sort_by', 'date_depart')
    order = request.args.get('order', 'desc')

    query = Trip.query

    # Filtres
    if search:
        query = query.filter(or_(
            Trip.code_voyage.ilike(f'%{search}%'),
            Trip.nom.ilike(f'%{search}%'),
            Trip.client_nom.ilike(f'%{search}%')
        ))
    
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%d/%m/%Y').date()
            query = query.filter(Trip.date_depart >= date_debut)
        except ValueError:
            pass

    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%d/%m/%Y').date()
            query = query.filter(Trip.date_depart <= date_fin)
        except ValueError:
            pass

    if trip_type:
        query = query.filter(Trip.type == trip_type)

    # Tri
    if hasattr(Trip, sort_by):
        column = getattr(Trip, sort_by)
        if order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    else:
        query = query.order_by(Trip.date_depart.desc())

    # Exécution de la requête
    trips = query.all()
    trips_dict = []
    
    for t in trips:
        # Calcul du total des passagers
        total_passagers = (t.nombre_adultes or 0) + (t.nombre_enfants or 0) + (t.nombre_bebes or 0)
        
        # Format de la date et heure
        date_str = t.date_depart.strftime('%d/%m/%Y') if t.date_depart else ''
        heure_str = t.date_depart.strftime('%H:%M') if t.date_depart else ''
        
        # Détermination de l'état
        etat = 'Planifié'  # Vous pouvez ajouter votre logique d'état ici
        
        # Formatage du prix
        prix = float(t.tarif) if t.tarif is not None else 0.0
        
        trips_dict.append({
            'id_trip': t.id_trip,
            'code_voyage': t.code_voyage,
            'nom': t.nom or '',
            'type': t.type,
            'client_nom': t.client_nom or '',
            'date_depart': date_str,
            'heure_depart': heure_str,
            'total_passagers': total_passagers,
            'tarif': f"{prix:.3f}",  # Format avec 3 décimales
            'etat': etat  # Ajout de l'état
        })

    return jsonify({'data': trips_dict})

@trips_bp.route('/add/normal', methods=['GET', 'POST'])
@login_required
def add_normal_trip():
    """Ajouter un nouveau voyage normal"""
    if request.method == 'POST':
        try:
            # Conversion des dates
            date_str = request.form.get('date_depart')
            heure_str = request.form.get('heure_depart')
            
            if not date_str:
                flash('La date de départ est requise', 'danger')
                return redirect(url_for('trips.add_normal_trip'))

            try:
                date_depart = datetime.strptime(date_str, '%d/%m/%Y')
                if heure_str:
                    heure = datetime.strptime(heure_str, '%H:%M').time()
                    date_depart = datetime.combine(date_depart.date(), heure)
            except ValueError as e:
                flash('Format de date ou heure invalide', 'danger')
                return redirect(url_for('trips.add_normal_trip'))

            # Calcul total passagers
            nombre_adultes = int(request.form.get('nombre_adultes', 0))
            nombre_enfants = int(request.form.get('nombre_enfants', 0))
            nombre_bebes = int(request.form.get('nombre_bebes', 0))
            total_passagers = nombre_adultes + nombre_enfants + nombre_bebes

            # Création du voyage
            new_trip = Trip(
                code_voyage=generate_trip_code(),
                nom=request.form.get('nom'),
                type=request.form.get('type'),
                client_nom=request.form.get('client_nom'),
                client_telephone=request.form.get('client_telephone'),
                client_email=request.form.get('client_email'),
                date_depart=date_depart,
                total_passagers=total_passagers,
                nombre_adultes=nombre_adultes,
                nombre_enfants=nombre_enfants,
                nombre_bebes=nombre_bebes,
                tarif=float(request.form.get('tarif', 0)),
                commission_achat=request.form.get('commission_achat') == 'on',
                point_depart=request.form.get('point_depart'),
                point_arrivee=request.form.get('point_arrivee'),
                created_by_id=current_user.id_user
            )

            # Gestion commission
            if new_trip.commission_achat and request.form.get('prix_commission'):
                new_trip.montant_commission = float(request.form.get('prix_commission'))

            # Points de visite pour excursion
            if request.form.get('type') == 'Excursion':
                points_visite = request.form.getlist('points_visite[]')
                if points_visite:
                    new_trip.points_intermediaires = [point for point in points_visite if point.strip()]

            db.session.add(new_trip)
            db.session.flush()

            # Affectations véhicules/chauffeurs
            vehicules = request.form.getlist('vehicules[]')
            chauffeurs = request.form.getlist('chauffeurs[]')
            
            if not vehicules or not chauffeurs:
                flash('Veuillez sélectionner au moins un véhicule et un chauffeur', 'danger')
                return redirect(url_for('trips.add_normal_trip'))

            for v_id in vehicules:
                for c_id in chauffeurs:
                    affectation = TripAffectation(
                        id_trip=new_trip.id_trip,
                        id_vehicule=int(v_id),
                        id_chauffeur=int(c_id)
                    )
                    db.session.add(affectation)

            # Dépenses supplémentaires
            if new_trip.type in ['Excursion', 'Varié']:
                depenses_noms = request.form.getlist('depense_nom[]')
                depenses_montants = request.form.getlist('depense_montant[]')
                
                for nom, montant in zip(depenses_noms, depenses_montants):
                    if nom and montant:
                        try:
                            depense = TripDepense(
                                id_trip=new_trip.id_trip,
                                nom=nom,
                                prix_unitaire=float(montant),
                                nombre_personnes=1,
                                total=float(montant)
                            )
                            db.session.add(depense)
                        except ValueError:
                            flash(f'Montant invalide pour la dépense : {nom}', 'danger')
                            return redirect(url_for('trips.add_normal_trip'))

            db.session.commit()
            flash('Voyage ajouté avec succès.', 'success')
            return redirect(url_for('trips.manage'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'ajout du voyage : {str(e)}")
            flash(f'Erreur lors de l\'ajout du voyage : {str(e)}', 'danger')
            return redirect(url_for('trips.add_normal_trip'))

    # GET request
    vehicules = Vehicule.query.filter_by(etat='En marche').all()
    chauffeurs = Chauffeur.query.filter_by(statut='Actif').all()
    return render_template('trips/add_trip.html',
                         vehicules=vehicules,
                         chauffeurs=chauffeurs,
                         code_voyage=generate_trip_code())

@trips_bp.route('/add/vente', methods=['GET', 'POST'])
@login_required
def add_vente_trip():
    """Ajouter une commission de vente"""
    if request.method == 'POST':
        try:
            date_str = request.form.get('date_vente')
            if not date_str:
                flash('La date est requise', 'danger')
                return redirect(url_for('trips.add_vente_trip'))

            try:
                date_vente = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                flash('Format de date invalide', 'danger')
                return redirect(url_for('trips.add_vente_trip'))

            new_trip = Trip(
                code_voyage=generate_trip_code(),
                nom=request.form.get('nom'),
                type='Commission Vente',
                client_nom=request.form.get('client_nom'),
                date_depart=date_vente,
                tarif=float(request.form.get('prix', 0)),
                commission_achat=True,
                created_by_id=current_user.id_user
            )
            
            db.session.add(new_trip)
            db.session.commit()
            flash('Commission de vente ajoutée avec succès.', 'success')
            return redirect(url_for('trips.manage'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout de la commission : {str(e)}', 'danger')
            return redirect(url_for('trips.add_vente_trip'))

    return render_template('trips/vente_trip.html',
                         code_voyage=generate_trip_code())

@trips_bp.route('/edit/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    """Éditer un voyage existant"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        try:
            # Mise à jour des informations de base
            trip.nom = request.form.get('nom')
            trip.type = request.form.get('type')
            trip.client_nom = request.form.get('client_nom')
            trip.client_telephone = request.form.get('client_telephone')
            trip.client_email = request.form.get('client_email')

            # Mise à jour des passagers
            trip.nombre_adultes = int(request.form.get('nombre_adultes', 0))
            trip.nombre_enfants = int(request.form.get('nombre_enfants', 0))
            trip.nombre_bebes = int(request.form.get('nombre_bebes', 0))
            trip.total_passagers = trip.nombre_adultes + trip.nombre_enfants + trip.nombre_bebes

            # Mise à jour de l'itinéraire
            trip.point_depart = request.form.get('point_depart')
            trip.point_arrivee = request.form.get('point_arrivee')

            # Mise à jour de la date et heure
            date_str = request.form.get('date_depart')
            heure_str = request.form.get('heure_depart')
            
            if date_str:
                try:
                    date_depart = datetime.strptime(date_str, '%Y-%m-%d')
                    if heure_str:
                        heure = datetime.strptime(heure_str, '%H:%M').time()
                        date_depart = datetime.combine(date_depart.date(), heure)
                    trip.date_depart = date_depart
                except ValueError as e:
                    flash('Format de date ou heure invalide', 'danger')
                    return redirect(url_for('trips.edit_trip', trip_id=trip_id))

            # Mise à jour du prix
            trip.tarif = float(request.form.get('tarif', 0))
            trip.commission_achat = request.form.get('commission_achat') == 'on'
            if trip.commission_achat and request.form.get('prix_commission'):
                trip.montant_commission = float(request.form.get('prix_commission', 0))

            # Mise à jour des affectations
            TripAffectation.query.filter_by(id_trip=trip.id_trip).delete()
            vehicules = request.form.getlist('vehicules[]')
            chauffeurs = request.form.getlist('chauffeurs[]')
            
            for v_id in vehicules:
                for c_id in chauffeurs:
                    if v_id and c_id:  # Vérifier que les IDs ne sont pas vides
                        affectation = TripAffectation(
                            id_trip=trip.id_trip,
                            id_vehicule=int(v_id),
                            id_chauffeur=int(c_id)
                        )
                        db.session.add(affectation)

            # Mise à jour de l'horodatage
            trip.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Voyage modifié avec succès.', 'success')
            return redirect(url_for('trips.manage'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification : {str(e)}', 'danger')
            return redirect(url_for('trips.edit_trip', trip_id=trip_id))

    # GET request
    vehicules = Vehicule.query.filter_by(etat='En marche').all()
    chauffeurs = Chauffeur.query.filter_by(statut='Actif').all()
    affectations = TripAffectation.query.filter_by(id_trip=trip.id_trip).all()

    return render_template('trips/edit_trip.html',
                         trip=trip,
                         vehicules=vehicules,
                         chauffeurs=chauffeurs,
                         affectations=affectations)



@trips_bp.route('/delete/<int:trip_id>', methods=['DELETE'])
@login_required
def delete_trip(trip_id):
    try:
        trip = Trip.query.get_or_404(trip_id)
        
        # Supprimer d'abord les affectations liées
        TripAffectation.query.filter_by(id_trip=trip_id).delete()
        
        # Puis supprimer le voyage
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Voyage supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@trips_bp.route('/export/<int:trip_id>')
@login_required
def export_trip(trip_id):
    """Exporter un voyage en Excel"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Préparation des données
    data = {
        'Code': [trip.code_voyage],
        'Nom': [trip.nom],
        'Type': [trip.type],
        'Client': [trip.client_nom],
        'Date': [trip.date_depart.strftime('%d/%m/%Y')],
        'Adultes': [trip.nombre_adultes],
        'Enfants': [trip.nombre_enfants],
        'Bébés': [trip.nombre_bebes],
        'Total passagers': [trip.total_passagers],
        'Prix': [float(trip.tarif or 0)],
        'Commission': [float(trip.montant_commission or 0)],
        'Point de départ': [trip.point_depart],
        'Point d\'arrivée': [trip.point_arrivee]
    }
    
    # Création du fichier Excel
    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Voyage', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Voyage']
        
        # Format monnaie
        money_fmt = workbook.add_format({'num_format': '#,##0.000'})
        worksheet.set_column('J:K', None, money_fmt)  # Colonnes Prix et Commission
        
        # Ajustement largeur colonnes
        for idx, col in enumerate(df.columns):
            worksheet.set_column(idx, idx, max(len(str(col)), df[col].astype(str).str.len().max()) + 2)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'voyage_{trip.code_voyage}.xlsx'
    )

@trips_bp.route('/check-disponibilite', methods=['POST'])
@login_required
def check_disponibilite():
    """Vérifier la disponibilité des véhicules et chauffeurs"""
    date = request.form.get('date')
    vehicule_ids = request.form.getlist('vehicules[]')
    chauffeur_ids = request.form.getlist('chauffeurs[]')
    
    if not date:
        return jsonify({'error': 'Date requise'}), 400
        
    try:
        date_check = datetime.strptime(date, '%d/%m/%Y').date()
    except ValueError:
        return jsonify({'error': 'Format de date invalide'}), 400
        
    conflits = []
    
    # Vérification véhicules
    for v_id in vehicule_ids:
        affectations = TripAffectation.query.join(Trip).filter(
            TripAffectation.id_vehicule == v_id,
            Trip.date_depart == date_check
        ).all()
        
        if affectations:
            vehicule = Vehicule.query.get(v_id)
            conflits.append({
                'type': 'vehicule',
                'id': v_id,
                'nom': f"{vehicule.modele} - {vehicule.matricule}",
                'voyages': [{
                    'id': a.trip.id_trip,
                    'nom': a.trip.nom,
                    'date_depart': a.trip.date_depart.strftime('%d/%m/%Y')
                } for a in affectations]
            })
            
    # Vérification chauffeurs
    for c_id in chauffeur_ids:
        affectations = TripAffectation.query.join(Trip).filter(
            TripAffectation.id_chauffeur == c_id,
            Trip.date_depart == date_check
        ).all()
        
        if affectations:
            chauffeur = Chauffeur.query.get(c_id)
            conflits.append({
                'type': 'chauffeur',
                'id': c_id,
                'nom': f"{chauffeur.prenom} {chauffeur.nom}",
                'voyages': [{
                    'id': a.trip.id_trip,
                    'nom': a.trip.nom,
                    'date_depart': a.trip.date_depart.strftime('%d/%m/%Y')
                } for a in affectations]
            })
    
    return jsonify({
        'disponible': len(conflits) == 0,
        'conflits': conflits
    })