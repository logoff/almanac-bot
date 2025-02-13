db = db.getSiblingDB('admin');

db.createCollection('ephemeris');

db.ephemeris.insertMany([
  {
    "date": new Date("1899-11-29"),
    "text": "Joan Gamper juntament amb els suïssos Otto Kunzle i Walter Wild, els anglesos John i William Parsons, l'alemany Otto Maier i els catalans Lluís d'Ossó, Bartomeu Terrades, l'aragonès Enric Ducay, Pere Cabot, Carles Pujol i Josep Llobet, es reuneixen al Gimnàs Solé per formar una associació que portarà el nom i l'escut de la ciutat: el Futbol Club Barcelona.",
    "location": {
        "latitude": 41.38291533569831,
        "longitude": 2.169884207359594
    }
  },
  {
    "date": new Date("1957-09-24"),
    "text": "S'inaugura el Camp Nou amb una missa solmne, una desfilada de diversos clubs de Catalunya i un partit entre el F.C. Barcelona i una selecció de jugadors de Varsòvia.",
    "location": {
        "latitude": 41.3808,
        "longitude": 2.1228
    }
  },
  {
    "date": new Date("1999-11-29"),
    "text": "El F.C. Barcelona celebra el seu centenari.",
    "location": {
        "latitude": 41.38291533569831,
        "longitude": 2.169884207359594
    }
  },
  {
    "date": new Date("1950-02-13 15:30:00"),
    "text": "test"
  }
]);
