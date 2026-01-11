from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Solitaire deck adapter", description="Adapter that provides Deck of Cards API functionalities to Solitaire game")
api_url = "https://deckofcardsapi.com/api/deck"

DEBUG_DECK = "j3377oca0u0b"

decks = []

@app.get("/new_deck")
def get_new_deck():
    """
    Retrive a new shuffled deck of cards from the Deck of Cards API
    """
    print("Getting new deck")
    response = requests.get(f"{api_url}/new/shuffle/?deck_count=1")
    deck = response.json()

    #deck = {
     #   "success":True,
      #  "deck_id":"v9co4nofwwsv",
       # "remaining":52,
        #"shuffled":True
    #}

    print(f"Deck received: {deck}")

    decks.append(deck['deck_id'])
    return deck

@app.get("/draw_cards/{deck_id}/{count}")
def draw_cards(deck_id: str, count: int):
    """
    Draw a specified number of cards from a given deck
    """
    if deck_id not in decks and deck_id != DEBUG_DECK:
        raise HTTPException(status_code=404, detail="Item not found")

    response = requests.get(f"{api_url}/{deck_id}/draw/?count={count}")

    return response.json()

@app.post("/shuffle/{deck_id}")
def shuffle_deck(deck_id: str):
    """
    Shuffle the specified deck
    """
    if deck_id not in decks and deck_id != DEBUG_DECK:
        raise HTTPException(status_code=404, detail="Item not found")

    response = requests.get(f"{api_url}/{deck_id}/shuffle/")

    return response.json()