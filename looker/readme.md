# Looker Studio Dashboard

Dieses Verzeichnis dokumentiert das im Rahmen der Masterarbeit erstellte Looker-Studio-Dashboard zur Visualisierung der automatisierten Datenqualitätsprüfungen.

## Datenquelle

Das Dashboard basiert auf den in BigQuery gespeicherten Ergebnissen der Quality Gates.

Verwendete Tabelle bzw. View:

- `v_dq_results`

Die Daten stammen aus den automatisierten Prüfungen mit:

- dbt
- Great Expectations

## Inhalt der Dashboard-Screenshots

Die abgelegten Screenshots zeigen zentrale Auswertungen der Datenqualitätsprüfung, darunter:

- Anzahl der Datenqualitätsprüfungen je Werkzeug und Szenario
- fehlgeschlagene Prüfungen je Quality Gate
- erkannte Regelverletzungen je Prüfregel
- Vergleich der Szenarien `clean`, `technical` und `faulty`

## Szenarien

Im Dashboard werden die folgenden Szenarien verglichen:

- `clean`: Ausgangsszenario ohne gezielte Fehlerinjektion
- `technical`: Szenario mit technischen Datenqualitätsproblemen
- `faulty`: Szenario mit fachlichen und strukturellen Datenqualitätsproblemen

## Zweck

Das Dashboard dient der transparenten Darstellung der Validierungsergebnisse. Es unterstützt die Nachvollziehbarkeit der Quality-Gate-Ergebnisse und ergänzt die Evaluation des prototypischen Quality-as-Code-Frameworks.