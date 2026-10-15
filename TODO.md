# TODO — présentation Nessie (15/10/2026)

## 1. Faire tourner la démo dans son état actuel

- [x] `mise.toml` : variables utiles de `.envrc` (dbt, `AWS_*` vers MinIO). Les variables PySpark
      et `NESSIEDIR` / `PYICEBERG_HOME` ne servaient plus.
- [x] `nessie-cli` : service compose (profil `tools`) lancé par `mise run cli`, sur le réseau compose
      (plus de `--network host`). Accepte les options du CLI, ex. `mise run cli -c "LIST REFERENCES;"`.
- [x] Taskfile → tâches mise. `run` / `fail` renommées `pipeline-ok` / `pipeline-ko`. Doc et slides
      mises à jour.
- [x] Images MinIO : les images officielles ne sont plus publiques (Docker Hub et quay.io → 401).
      Remplacées par le fork communautaire `pgsty/minio` + `pgsty/mc`, tags fixés.
- [x] Dry-run (stack repartie de zéro) : `stack-reset`, `stack-up`, `pipeline-ok`, `pipeline-ko`, `branches`,
      `dbt-inspect`, `cli`, rollback `ASSIGN BRANCH main TO release-…` (10 → 5 lignes), notebook
      exécuté en headless.
- [x] Testés à la main : le notebook (`mise run notebook`) et le REPL (`mise run cli`).
- [x] `.envrc` et `.direnv/` supprimés.

## 1 bis. Sortie de `mise run pipeline-ok` / `pipeline-ko`

- [x] Sortie en français, une étape à la fois (0 à 4) avec l'outil qui agit, pause (Entrée) entre
      les étapes, hash court de `main` avant / après, nombre de lignes branche vs main, tableau des
      lignes ingérées (lignes sales en rouge), résumé dbt par modèle et par test.
- [x] `mise run pipeline-ok` validé à la main (pauses comprises).
- [x] `mise run pipeline-ko` validé à la main.

Retours du test (implémentés) :
- [x] Sortir l'initialisation de `main` (namespaces `raw` et `marts`) de la pipeline : l'étape 0
      décrit l'état, elle ne modifie rien.
- [x] Étape 0 : afficher « raw.orders : n'existe pas encore » quand la table est absente (pas « 0 lignes »).
- [x] `mise run stack-up` avec une sortie narrée, sans pause : [1/3] démarrer la stack (compose et
      `uv sync` masqués sauf erreur), [2/3] état initial de Nessie (`main` @ commit zéro, aucune
      table), [3/3] créer les namespaces sur `main` (rôle de `raw` / `marts`, +2 commits, « déjà en
      place » si la stack est déjà initialisée).
- [x] `demo-scenario.md` : noter le contournement « main vide → No common ancestor » comme réponse
      possible à une question.
- [x] Titres d'étapes sous forme de description ; la pause annonce l'étape suivante.
- [x] État de `main` pour les deux tables (`raw.orders` en lignes, `marts.daily_orders` en jours et
      commandes), une ligne par table.
- [x] Tâches renommées `stack-up` / `stack-down` / `stack-reset`.
- [x] Mot de passe MinIO aléatoire (Chrome signalait `minioadmin` comme mot de passe ayant fuité).

## 2. Corrections avant ce soir

- [ ] Slide « Maturité » + `plan.md` : le bug DuckDB #1145 est corrigé (PR #1230, mergée le
      26/07/2026). Vérifier dans quelle version de DuckDB le correctif est publié, puis reformuler.
- [ ] Slide « Maturité » : Trino #24134 a été fermée en « not planned » (une syntaxe dédiée aux
      branches est annoncée). Préciser.
- [ ] README : `pipeline_YYYYMMDD` → `pipeline-HHMMSS`, ajouter les tags `release-HHMMSS`, mettre à
      jour le déroulé.
- [ ] Notebook : aligner sa description (README + acte 3) sur ce qu'il fait réellement.
- [ ] « 100 % local, zéro Java » : nuancer (le serveur Nessie est en Java/Quarkus, dans un conteneur).
- [x] Mineur : `--keep` dans `pipeline.py` ne fait rien (corrigé avec la nouvelle sortie).

## 3. Approfondir les concepts (questions / réponses)

- [ ] Session de questions sur Iceberg, Nessie et la stack ; décider après chaque réponse si une
      slide doit évoluer.
- [ ] Parler des namespaces dans les présentations HTML. Séparer ce qui relève d'Iceberg (un
      namespace regroupe des tables, comme un schéma SQL : `raw.orders`) de ce qui est propre à
      Nessie (un namespace est versionné : le créer produit un commit). Choisir où le placer
      (`iceberg.html`, `presentation.html` ou les deux).

## 4. Slide 03/07 (stack) : détail au clic

- [ ] Clic sur un bloc → panneau de détail : rôle, ce que fait l'élément dans la démo, fichier(s)
      concerné(s), alternatives.

## 5. Slide 06/07 (maturité) : ajouter Snowflake

- [ ] Vérifier ce que Snowflake sait faire avec un catalog Iceberg externe / Nessie (lecture,
      écriture, choix de la branche), sources à l'appui.
- [ ] Ajouter une ligne Snowflake et, si c'est possible, expliquer comment l'intégrer.

## Si on a fini

- [ ] Raffiner le notebook : ne pas planter sur une branche sans `raw.orders`, pouvoir choisir les
      tags, ajouter l'historique des commits, parcourir les tables.
- [ ] Se passer de PyIceberg avec une version à jour de DuckDB : vérifier que `ATTACH` sur une
      branche Nessie fonctionne (lecture + écriture + `CREATE OR REPLACE`), et voir ce que ça
      simplifie (plugins dbt, `catalog.py`).
