// mongo-init.js
db = db.getSiblingDB('myapp');

// Crea collezione users
db.createCollection('users');

// Crea indici
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "google_id": 1 }, { unique: true, sparse: true });

// Inserisci dati di esempio (opzionale)
db.users.insertOne({
  email: "test@example.com",
  name: "Test User",
  created_at: new Date()
});

print('Database inizializzato con successo!');