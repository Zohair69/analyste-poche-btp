"""
Génère le jeu de données de démonstration : une menuiserie FICTIVE.

Toutes les données (noms, montants, dates) sont inventées par ce script.
Elles servent uniquement à tester l'application.

Tables produites dans data/demo/ (CSV, séparateur « ; », encodage UTF-8) :
- clients   : les clients de la menuiserie
- devis     : les devis envoyés (acceptés, refusés ou en attente)
- chantiers : un chantier par devis accepté
- factures  : acompte puis solde de chaque chantier
- achats    : les achats de matériaux affectés à un chantier
- heures    : les heures de travail passées sur chaque chantier

Lancement : python scripts/generer_demo.py
Auteur : Zohair
"""

from pathlib import Path

import numpy as np
import pandas as pd

# Graine fixe : on obtient toujours exactement les mêmes données.
rng = np.random.default_rng(42)

DOSSIER_SORTIE = Path(__file__).resolve().parent.parent / "data" / "demo"
DATE_DEBUT = pd.Timestamp("2025-01-01")
DATE_FIN = pd.Timestamp("2026-11-15")  # « aujourd'hui » pour la démo

# --- Référentiels métier ---------------------------------------------------
# Type de travaux -> fourchette de montant HT d'un devis (en euros)
TYPES_TRAVAUX = {
    "Fenêtres": (2500, 12000),
    "Porte d'entrée": (1800, 5000),
    "Escalier": (4000, 15000),
    "Cuisine": (6000, 20000),
    "Placards et dressing": (1500, 7000),
    "Volets": (1200, 6000),
    "Parquet": (2000, 9000),
}
NOMS = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
        "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
        "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel",
        "Girard", "André", "Mercier", "Dupont", "Lambert", "Bonnet", "Fontaine"]
VILLES = ["Lyon", "Villeurbanne", "Vénissieux", "Saint-Priest", "Bron",
          "Vaulx-en-Velin", "Caluire-et-Cuire", "Oullins", "Décines-Charpieu",
          "Meyzieu", "Rillieux-la-Pape", "Saint-Fons"]
FOURNISSEURS = {  # fournisseurs fictifs
    "Bois": "Scierie Fictive du Rhône",
    "Quincaillerie": "Quincaillerie Démo",
    "Vitrage": "Verrerie Exemple",
    "Finition": "Peintures Test",
}
SALARIES = ["Menuisier 1", "Menuisier 2", "Menuisier 3", "Apprenti"]
TAUX_HORAIRE = {"Menuisier 1": 38.0, "Menuisier 2": 36.0,
                "Menuisier 3": 35.0, "Apprenti": 18.0}  # coût chargé €/h


def date_aleatoire(debut, fin):
    """Tire une date au hasard entre debut et fin (incluses)."""
    nb_jours = (fin - debut).days
    return debut + pd.Timedelta(days=int(rng.integers(0, nb_jours + 1)))


# --- 1. Clients ---------------------------------------------------------------
def generer_clients(nb=120):
    lignes = []
    for i in range(1, nb + 1):
        est_pro = rng.random() < 0.25
        nom = rng.choice(NOMS)
        lignes.append({
            "id_client": f"C{i:03d}",
            "nom_client": f"SCI {nom}" if est_pro else f"Famille {nom}",
            "type_client": "Professionnel" if est_pro else "Particulier",
            "ville": rng.choice(VILLES),
            "date_premier_contact": date_aleatoire(DATE_DEBUT - pd.Timedelta(days=365), DATE_FIN),
        })
    return pd.DataFrame(lignes)


# --- 2. Devis -----------------------------------------------------------------
def generer_devis(clients, nb=320):
    lignes = []
    for i in range(1, nb + 1):
        client = clients.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        type_travaux = rng.choice(list(TYPES_TRAVAUX))
        mini, maxi = TYPES_TRAVAUX[type_travaux]
        date_devis = date_aleatoire(DATE_DEBUT, DATE_FIN)
        anciennete = (DATE_FIN - date_devis).days

        # Un devis récent peut encore être en attente de réponse.
        if anciennete < 30 and rng.random() < 0.6:
            statut, date_reponse = "En attente", pd.NaT
        else:
            statut = "Accepté" if rng.random() < 0.45 else "Refusé"
            delai = int(rng.integers(3, 30))
            date_reponse = min(date_devis + pd.Timedelta(days=delai), DATE_FIN)

        lignes.append({
            "id_devis": f"D{i:04d}",
            "id_client": client["id_client"],
            "type_travaux": type_travaux,
            "date_devis": date_devis,
            "montant_ht": round(float(rng.uniform(mini, maxi)), 2),
            "statut": statut,
            "date_reponse": date_reponse,
        })
    return pd.DataFrame(lignes).sort_values("date_devis").reset_index(drop=True)


# --- 3. Chantiers -------------------------------------------------------------
def generer_chantiers(devis):
    acceptes = devis[devis["statut"] == "Accepté"].reset_index(drop=True)
    lignes = []
    for i, d in acceptes.iterrows():
        debut_prevu = d["date_reponse"] + pd.Timedelta(days=int(rng.integers(10, 45)))
        duree_prevue = int(rng.integers(3, 20))
        fin_prevue = debut_prevu + pd.Timedelta(days=duree_prevue)
        # Budget de coût prévu (matériaux + main-d'œuvre) : 60 à 75 % du devis.
        budget = round(d["montant_ht"] * float(rng.uniform(0.60, 0.75)), 2)

        if debut_prevu > DATE_FIN:
            statut, fin_reelle = "Planifié", pd.NaT
        else:
            # Retard possible : 0 jour le plus souvent, parfois plusieurs.
            retard = int(rng.choice([0, 0, 0, 0, 0, 0, 0, 2, 5, 15]))
            fin_reelle = fin_prevue + pd.Timedelta(days=retard)
            if fin_reelle > DATE_FIN:
                statut, fin_reelle = "En cours", pd.NaT
            else:
                statut = "Terminé"

        lignes.append({
            "id_chantier": f"CH{i + 1:03d}",
            "id_devis": d["id_devis"],
            "id_client": d["id_client"],
            "type_travaux": d["type_travaux"],
            "date_debut_prevue": debut_prevu,
            "date_fin_prevue": fin_prevue,
            "date_fin_reelle": fin_reelle,
            "budget_prevu_ht": budget,
            "statut": statut,
        })
    return pd.DataFrame(lignes)


# --- 4. Achats et heures (le coût réel des chantiers démarrés) ---------------
def generer_achats_et_heures(chantiers):
    achats, heures = [], []
    for _, ch in chantiers[chantiers["statut"] != "Planifié"].iterrows():
        # Dépassement de budget : la plupart des chantiers restent proches
        # du budget, certains dérapent.
        facteur = float(rng.choice([0.80, 0.85, 0.88, 0.90, 0.92, 0.95, 1.10, 1.30]))
        cout_cible = ch["budget_prevu_ht"] * facteur
        part_materiaux = float(rng.uniform(0.45, 0.65))
        fin = ch["date_fin_reelle"] if pd.notna(ch["date_fin_reelle"]) else DATE_FIN
        debut = min(ch["date_debut_prevue"], fin)

        # Achats : 2 à 5 lignes qui se partagent le budget matériaux.
        nb = int(rng.integers(2, 6))
        parts = rng.dirichlet(np.ones(nb))
        for p in parts:
            categorie = rng.choice(list(FOURNISSEURS))
            achats.append({
                "id_chantier": ch["id_chantier"],
                "date_achat": date_aleatoire(debut - pd.Timedelta(days=7), debut),
                "fournisseur": FOURNISSEURS[categorie],
                "categorie": categorie,
                "montant_ht": round(cout_cible * part_materiaux * float(p), 2),
            })

        # Heures : on répartit le budget main-d'œuvre en journées de travail.
        reste = cout_cible * (1 - part_materiaux)
        while reste > 0:
            salarie = rng.choice(SALARIES)
            nb_heures = float(rng.choice([4.0, 7.0, 8.0]))
            heures.append({
                "id_chantier": ch["id_chantier"],
                "date_travail": date_aleatoire(debut, fin),
                "salarie": salarie,
                "nb_heures": nb_heures,
                "cout_horaire": TAUX_HORAIRE[salarie],
            })
            reste -= nb_heures * TAUX_HORAIRE[salarie]

    achats = pd.DataFrame(achats)
    achats.insert(0, "id_achat", [f"A{i:05d}" for i in range(1, len(achats) + 1)])
    heures = pd.DataFrame(heures)
    heures.insert(0, "id_saisie", [f"H{i:05d}" for i in range(1, len(heures) + 1)])
    return achats, heures


# --- 5. Factures (acompte 30 % au démarrage, solde à la fin) -----------------
def generer_factures(chantiers, devis, clients):
    montants = devis.set_index("id_devis")["montant_ht"]
    types = clients.set_index("id_client")["type_client"]
    lignes = []

    def ajouter(ch, nature, date_facture, montant_ht):
        # TVA : 10 % (rénovation chez un particulier), 20 % pour un professionnel.
        taux = 0.10 if types[ch["id_client"]] == "Particulier" else 0.20
        echeance = date_facture + pd.Timedelta(days=30)
        # Paiement : souvent avant l'échéance, parfois en retard, parfois pas encore.
        delai = int(rng.choice([5, 15, 25, 30, 40, 60, 90]))
        date_paiement = date_facture + pd.Timedelta(days=delai)
        if date_paiement > DATE_FIN:
            date_paiement = pd.NaT
        lignes.append({
            "id_chantier": ch["id_chantier"],
            "id_client": ch["id_client"],
            "nature": nature,
            "date_facture": date_facture,
            "date_echeance": echeance,
            "montant_ht": round(montant_ht, 2),
            "taux_tva": taux,
            "montant_ttc": round(montant_ht * (1 + taux), 2),
            "date_paiement": date_paiement,
        })

    for _, ch in chantiers[chantiers["statut"] != "Planifié"].iterrows():
        total = montants[ch["id_devis"]]
        ajouter(ch, "Acompte", ch["date_debut_prevue"], total * 0.30)
        if ch["statut"] == "Terminé":
            ajouter(ch, "Solde", ch["date_fin_reelle"], total * 0.70)

    factures = pd.DataFrame(lignes).sort_values("date_facture").reset_index(drop=True)
    factures.insert(0, "id_facture", [f"F{i:04d}" for i in range(1, len(factures) + 1)])
    return factures


def main():
    clients = generer_clients()
    devis = generer_devis(clients)
    # Cohérence : le premier contact d'un client a lieu au plus tard
    # le jour de son premier devis.
    premier_devis = devis.groupby("id_client")["date_devis"].min()
    clients["date_premier_contact"] = clients.apply(
        lambda c: min(c["date_premier_contact"], premier_devis.get(c["id_client"], c["date_premier_contact"])),
        axis=1)
    chantiers = generer_chantiers(devis)
    achats, heures = generer_achats_et_heures(chantiers)
    factures = generer_factures(chantiers, devis, clients)

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    tables = {"clients": clients, "devis": devis, "chantiers": chantiers,
              "factures": factures, "achats": achats, "heures": heures}
    for nom, df in tables.items():
        df.to_csv(DOSSIER_SORTIE / f"{nom}.csv", sep=";", index=False,
                  encoding="utf-8", date_format="%Y-%m-%d")
        print(f"{nom:<10} : {len(df):>5} lignes")
    print(f"Fichiers écrits dans {DOSSIER_SORTIE}")


if __name__ == "__main__":
    main()
