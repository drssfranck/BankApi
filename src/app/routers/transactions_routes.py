from fastapi import APIRouter, HTTPException
from typing import List
import csv
from pathlib import Path
from app.models.cardData import CardData

DATA_FILE = Path(__file__).parent.parent / "data" / "cards_data.csv"

router = APIRouter()

@router.get("/", response_model=List[CardData], summary="Récupère toutes les cartes")
def get_card_list():
    cards = []
    try:
        with DATA_FILE.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    card = CardData(
                        id=int(row["id"]),
                        client_id=int(row["client_id"]),
                        card_brand=row["card_brand"],
                        card_type=row["card_type"],
                        card_number=row["card_number"],
                        expire=row["expire"],
                        cvv=int(row["cvv"]),
                        has_ship=row["has_ship"].lower() in ["true", "1", "yes"],
                        num_card_issueds=int(row["num_card_issueds"]),
                        credit_limit=float(row["credit_limit"])
                    )
                    cards.append(card)
                except Exception as e:
                    print(f"Ligne invalide ignorée: {row} -> {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de données introuvable")
    return cards
