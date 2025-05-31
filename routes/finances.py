from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from decimal import Decimal
import json
import os

from models import db, Transaction, CompteBancaire, Budget, PieceJointe, RapportFinancier, Depense
from utils import allowed_file, save_file, generate_pdf_report, calculate_financial_indicators, get_monthly_stats, generate_budget_summary, generate_excel_report

finances_bp = Blueprint('finances', __name__)



@finances_bp.route('/')
@login_required
def index():
    # Récupération des statistiques générales
    total_revenus = db.session.query(func.sum(Transaction.montant)).\
        filter(Transaction.type == 'Revenu').scalar() or 0
    
    total_depenses = db.session.query(func.sum(Transaction.montant)).\
        filter(Transaction.type == 'Dépense').scalar() or 0
    
    # Solde total des comptes
    solde_total = db.session.query(func.sum(CompteBancaire.solde_actuel)).scalar() or 0
    
    # Transactions récentes
    transactions_recentes = Transaction.query.\
        order_by(Transaction.date_transaction.desc()).limit(10).all()
    
    # Statistiques budgétaires
    budgets = Budget.query.all()
    
    # Date actuelle
    current_time = datetime.utcnow()
    
    return render_template('finances/dashboard.html',
                         total_revenus=total_revenus,
                         total_depenses=total_depenses,
                         solde_total=solde_total,
                         transactions_recentes=transactions_recentes,
                         budgets=budgets,
                         current_time=current_time,
                         username=current_user.username)

@finances_bp.route('/dashboard-financier')
@login_required
def dashboard_financier():
    total_revenus = db.session.query(func.sum(Transaction.montant)).\
        filter(Transaction.type == 'Revenu').scalar() or 0
    
    total_depenses = db.session.query(func.sum(Transaction.montant)).\
        filter(Transaction.type == 'Dépense').scalar() or 0
    
    solde_total = db.session.query(func.sum(CompteBancaire.solde_actuel)).scalar() or 0
    
    transactions_recentes = Transaction.query.\
        order_by(Transaction.date_transaction.desc()).limit(10).all()
    
    budgets = Budget.query.all()
    
    return render_template('finances/dashboard.html',
                         total_revenus=total_revenus,
                         total_depenses=total_depenses,
                         solde_total=solde_total,
                         transactions_recentes=transactions_recentes,
                         budgets=budgets)

@finances_bp.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        try:
            transaction = Transaction(
                type=request.form['type'],
                montant=Decimal(request.form['montant']),
                date_transaction=datetime.strptime(request.form['date_transaction'], '%Y-%m-%d'),
                description=request.form['description'],
                categorie=request.form['categorie'],
                sous_categorie=request.form.get('sous_categorie'),
                mode_paiement=request.form['mode_paiement'],
                reference=request.form.get('reference'),
                id_compte=request.form['id_compte'],
                created_by=current_user.id_user
            )
            
            if 'piece_jointe' in request.files:
                file = request.files['piece_jointe']
                if file and allowed_file(file.filename):
                    filename = save_file(file)
                    piece_jointe = PieceJointe(
                        nom_fichier=filename,
                        url_fichier=f'/uploads/{filename}',
                        type_document='justificatif'
                    )
                    transaction.pieces_jointes.append(piece_jointe)
            
            compte = CompteBancaire.query.get(transaction.id_compte)
            if transaction.type == 'Revenu':
                compte.solde_actuel += transaction.montant
            elif transaction.type == 'Dépense':
                compte.solde_actuel -= transaction.montant
            
            db.session.add(transaction)
            db.session.commit()
            
            flash('Transaction ajoutée avec succès!', 'success')
            return redirect(url_for('finances.transactions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout de la transaction: {str(e)}', 'danger')
    
    transactions = Transaction.query.order_by(Transaction.date_transaction.desc()).all()
    comptes = CompteBancaire.query.all()
    return render_template('finances/transactions.html', 
                         transactions=transactions,
                         comptes=comptes)
@finances_bp.route('/comptes', methods=['GET', 'POST'])
@login_required
def comptes():
    if request.method == 'POST':
        try:
            compte = CompteBancaire(
                nom_banque=request.form['nom_banque'],
                numero_compte=request.form['numero_compte'],
                type_compte=request.form['type_compte'],
                solde_actuel=Decimal(request.form['solde_initial']),
                devise=request.form['devise'],
                date_ouverture=datetime.strptime(request.form['date_ouverture'], '%Y-%m-%d')
            )
            
            db.session.add(compte)
            db.session.commit()
            
            flash('Compte bancaire ajouté avec succès!', 'success')
            return redirect(url_for('finances.comptes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du compte: {str(e)}', 'danger')
    
    comptes = CompteBancaire.query.all()
    return render_template('finances/comptes.html', comptes=comptes)

@finances_bp.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    if request.method == 'POST':
        try:
            budget = Budget(
                categorie=request.form['categorie'],
                montant_prevu=Decimal(request.form['montant_prevu']),
                periode_debut=datetime.strptime(request.form['periode_debut'], '%Y-%m-%d'),
                periode_fin=datetime.strptime(request.form['periode_fin'], '%Y-%m-%d'),
                notes=request.form.get('notes')
            )
            
            db.session.add(budget)
            db.session.commit()
            
            flash('Budget ajouté avec succès!', 'success')
            return redirect(url_for('finances.budgets'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du budget: {str(e)}', 'danger')
    
    budgets = Budget.query.all()
    return render_template('finances/budgets.html', budgets=budgets)

@finances_bp.route('/rapports')
@login_required
def rapports():
    rapports = RapportFinancier.query.order_by(RapportFinancier.date_creation.desc()).all()
    return render_template('finances/rapports.html', rapports=rapports)

@finances_bp.route('/generer-rapport', methods=['POST'])
@login_required
def generer_rapport():
    type_rapport = request.form['type_rapport']
    periode_debut = datetime.strptime(request.form['periode_debut'], '%Y-%m-%d')
    periode_fin = datetime.strptime(request.form['periode_fin'], '%Y-%m-%d')
    
    if type_rapport == 'flux_tresorerie':
        transactions = Transaction.query.\
            filter(Transaction.date_transaction.between(periode_debut, periode_fin)).\
            order_by(Transaction.date_transaction).all()
        
        contenu = {
            'transactions': [
                {
                    'date': t.date_transaction.strftime('%Y-%m-%d'),
                    'type': t.type,
                    'montant': float(t.montant),
                    'description': t.description
                } for t in transactions
            ]
        }
    
    rapport = RapportFinancier(
        type_rapport=type_rapport,
        periode_debut=periode_debut,
        periode_fin=periode_fin,
        contenu=contenu,
        created_by=current_user.id_user
    )
    
    db.session.add(rapport)
    db.session.commit()
    
    pdf_path = generate_pdf_report(rapport)
    
    return jsonify({
        'success': True,
        'rapport_id': rapport.id_rapport,
        'pdf_url': url_for('static', filename=f'rapports/{pdf_path}')
    })

@finances_bp.route('/api/statistiques-mensuelles')
@login_required
def statistiques_mensuelles():
    annee = request.args.get('annee', datetime.now().year)
    
    stats = db.session.query(
        extract('month', Transaction.date_transaction).label('mois'),
        Transaction.type,
        func.sum(Transaction.montant).label('total')
    ).\
    filter(extract('year', Transaction.date_transaction) == annee).\
    group_by('mois', Transaction.type).all()
    
    resultats = {
        'labels': [f'Mois {i}' for i in range(1, 13)],
        'revenus': [0] * 12,
        'depenses': [0] * 12
    }
    
    for stat in stats:
        index = stat.mois - 1
        if stat.type == 'Revenu':
            resultats['revenus'][index] = float(stat.total)
        else:
            resultats['depenses'][index] = float(stat.total)
    
    return jsonify(resultats)
@finances_bp.route('/api/statistiques')
@login_required
def get_statistiques():
    try:
        date_fin = datetime.now()
        date_debut = date_fin - timedelta(days=365)
        
        transactions = Transaction.query.filter(
            Transaction.date_transaction.between(date_debut, date_fin)
        ).all()
        
        stats = calculate_financial_indicators(transactions, date_debut, date_fin)
        monthly_stats = get_monthly_stats(transactions, date_fin.year)
        
        return jsonify({
            'success': True,
            'data': {
                'indicateurs': stats,
                'statistiques_mensuelles': monthly_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@finances_bp.route('/api/mouvements/<int:id_compte>')
@login_required
def get_mouvements_compte(id_compte):
    try:
        compte = CompteBancaire.query.get_or_404(id_compte)
        transactions = Transaction.query.filter_by(id_compte=id_compte)\
            .order_by(Transaction.date_transaction.desc()).all()
        
        mouvements = []
        solde_cumule = float(compte.solde_actuel)
        
        for transaction in reversed(transactions):
            mouvement = {
                'date': transaction.date_transaction.strftime('%Y-%m-%d'),
                'description': transaction.description,
                'type': transaction.type,
                'montant': float(transaction.montant),
                'solde': solde_cumule
            }
            
            if transaction.type == 'Dépense':
                solde_cumule += float(transaction.montant)
            else:
                solde_cumule -= float(transaction.montant)
                
            mouvements.append(mouvement)
        
        return jsonify({
            'success': True,
            'mouvements': mouvements
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@finances_bp.route('/api/budgets/suivi')
@login_required
def get_suivi_budgets():
    try:
        date_debut = datetime.now().replace(day=1)
        date_fin = (date_debut + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        budgets = Budget.query.filter(
            Budget.periode_debut <= date_fin,
            Budget.periode_fin >= date_debut
        ).all()
        
        resume = generate_budget_summary(budgets)
        
        return jsonify({
            'success': True,
            'data': resume
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@finances_bp.route('/rapports/<int:id_rapport>/telecharger/<format>')
@login_required
def telecharger_rapport(id_rapport, format):
    try:
        rapport = RapportFinancier.query.get_or_404(id_rapport)
        
        if format == 'pdf':
            buffer = generate_pdf_report(rapport)
            return send_file(
                buffer,
                download_name=f'rapport_{rapport.type_rapport}_{rapport.periode_debut.strftime("%Y%m%d")}.pdf',
                as_attachment=True,
                mimetype='application/pdf'
            )
        elif format == 'excel':
            buffer = generate_excel_report(rapport)
            return send_file(
                buffer,
                download_name=f'rapport_{rapport.type_rapport}_{rapport.periode_debut.strftime("%Y%m%d")}.xlsx',
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'success': False,
                'message': 'Format non supporté'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
@finances_bp.route('/api/transactions/categories')
@login_required
def get_categories_stats():
    try:
        date_debut = datetime.now().replace(day=1)
        date_fin = (date_debut + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        stats = db.session.query(
            Transaction.categorie,
            func.sum(Transaction.montant).label('total')
        ).filter(
            Transaction.date_transaction.between(date_debut, date_fin),
            Transaction.type == 'Dépense'
        ).group_by(Transaction.categorie).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'categorie': stat.categorie,
                'total': float(stat.total)
            } for stat in stats]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@finances_bp.route('/api/transactions/update/<int:id_transaction>', methods=['PUT'])
@login_required
def update_transaction(id_transaction):
    try:
        transaction = Transaction.query.get_or_404(id_transaction)
        data = request.get_json()
        
        # Récupérer l'ancien montant et type pour ajuster le solde du compte
        ancien_montant = float(transaction.montant)
        ancien_type = transaction.type
        
        # Mettre à jour la transaction
        for key, value in data.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        # Ajuster le solde du compte
        compte = CompteBancaire.query.get(transaction.id_compte)
        if ancien_type == 'Revenu':
            compte.solde_actuel -= Decimal(str(ancien_montant))
        else:
            compte.solde_actuel += Decimal(str(ancien_montant))
            
        if transaction.type == 'Revenu':
            compte.solde_actuel += Decimal(str(transaction.montant))
        else:
            compte.solde_actuel -= Decimal(str(transaction.montant))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction mise à jour avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@finances_bp.route('/api/transactions/delete/<int:id_transaction>', methods=['DELETE'])
@login_required
def delete_transaction(id_transaction):
    try:
        transaction = Transaction.query.get_or_404(id_transaction)
        
        # Ajuster le solde du compte
        compte = CompteBancaire.query.get(transaction.id_compte)
        if transaction.type == 'Revenu':
            compte.solde_actuel -= Decimal(str(transaction.montant))
        else:
            compte.solde_actuel += Decimal(str(transaction.montant))
        
        # Supprimer les pièces jointes associées
        for piece in transaction.pieces_jointes:
            if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], piece.nom_fichier)):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], piece.nom_fichier))
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction supprimée avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@finances_bp.route('/api/budgets/update/<int:id_budget>', methods=['PUT'])
@login_required
def update_budget(id_budget):
    try:
        budget = Budget.query.get_or_404(id_budget)
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(budget, key):
                setattr(budget, key, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Budget mis à jour avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
