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

- [x] Slide « Maturité » + `plan.md`, DuckDB : #1145 corrigé dans l'extension (PR #1230, mergée le
      26/07/2026 sur la branche principale) mais pas encore publié : la 1.5.6 (28/09/2026) ne
      l'inclut pas. `CREATE OR REPLACE` toujours absent (#784). Pastille « Pas encore ».
- [x] Slide « Maturité » + `plan.md`, Trino : #24134 fermée « not planned ». Le `CREATE BRANCH … IN
      TABLE` ajouté en 2025 concerne les branches Iceberg d'une table, pas les branches Nessie.
- [x] README : noms `pipeline-HHMMSS` / `-bad`, tags, étapes 0 à 4, mise en place, arborescence ;
      le déroulé renvoie vers `demo-scenario.md` et `demo-cli.md`.
- [x] Notebook : description du README alignée sur ce qu'il fait (l'acte 3 était déjà juste).
- [x] « Zéro Java » / « sans JVM » retiré des slides, de `plan.md` et du README (pas important).
- [x] Mineur : `--keep` dans `pipeline.py` ne fait rien (corrigé avec la nouvelle sortie).
- [x] Deux slides après « La pipeline » : 04 « La branche, c'est une adresse » (cas idéal, DuckDB
      attache la branche) et 05 « Le détour par PyIceberg » (le bug, les plugins, le prix). Le deck
      passe à 9 slides ; `plan.md` suit.
- [ ] Slide 04/09 « La pipeline » : dépasse de 24 px en 1440×900 (antérieur).

## 3. Approfondir les concepts (questions / réponses)

- [x] Session de questions sur Iceberg, Nessie et la stack ; décider après chaque réponse si une
      slide doit évoluer.
- [x] Namespaces : une ligne sur la carte Catalog de la slide « modèle mental » d'`iceberg.html`
      (concept de catalogue Iceberg, comme un schéma SQL). Le versionnement par Nessie reste à l'oral.
- [x] (à l'oral) Branches Iceberg vs branches Nessie : une branche Iceberg est une référence de snapshot dans
      **une** table (Spark, Trino `CREATE BRANCH … IN TABLE`) ; une branche Nessie couvre **tout le
      catalogue** (plusieurs tables, merge atomique). Question probable : en parler dans les slides ?

## 4. Slide 03/09 (stack) : détail au clic

- [x] Clic sur un bloc → panneau de détail : rôle, ce que fait l'élément dans la démo, fichier(s)
      concerné(s), alternatives, et une phrase « à dire ». Fermeture par Échap, ✕ ou clic à côté ;
      les flèches ne changent pas de slide tant que le panneau est ouvert.
- [x] Slide stack réorganisée : barre `pipeline.py · orchestration` au-dessus des colonnes data plane
      et control plane (pas de l'infra) ; colonnes Infra / Data plane (PyIceberg, dbt · DuckDB,
      plugin) / Control plane (`nessie.py`, Alerte). mise passe dans la légende.
- [x] MinIO → Silo (fork communautaire de MinIO par Pigsty) dans les slides, le README, `plan.md`,
      le scénario et la sortie de `stack-up` ; noms de services Docker inchangés. Détail Silo : seules
      les alternatives de production restent.
- [x] Sélecteur de thème clair / sombre (bouton ☀/☾ et touche `t`) sur les deux decks.
- [ ] Mineur : `docker-compose.yml` utilise `nessie.version.store.type=JDBC`, variante dépréciée dans
      Nessie (préférer `JDBC2`). Ne pas changer avant la présentation.

## 4 bis. Slide 09/09 « À creuser »

- [x] Bloc « Protéger main » (non cliquable) : autorisations Nessie par rôle ; limite : merge =
      même permission qu'un commit direct.
- [x] Bloc « Maintenance Iceberg » (à creuser) : pas de maintenance en direct, passer par Nessie GC
      (garbage collector, programme à part) ; metadata.json Nessie = snapshot courant seulement.
- [x] Blocs ajoutés : Pipelines concurrentes (conflit de merge vérifié), Intégration aux outils,
      Pérennité de Nessie. À l'oral : volumétrie, exploitation, cycle de vie des branches.

## 5. Slide 08/09 (maturité) : ajouter Snowflake

- [x] Recherche doc : *catalog integration* `ICEBERG_REST` avec `PREFIX = '<branche>'`, une intégration
      + une *catalog-linked database* par branche ; auth obligatoire, Nessie joignable depuis Snowflake.
- [x] Ligne Snowflake « ⚠ Non testé » ajoutée à la slide Maturité ; bloc « Intégration aux outils »
      sur la slide À creuser.
- [ ] Tester pour de vrai (Nessie exposé et authentifié, external volume S3) : `PREFIX` bien pris en
      compte ? comportement avec un metadata.json réduit au snapshot courant ?

## Si on a fini

- [x] Notebook réécrit en explorateur (branche `notebook-rework`) : sélecteur de branche, toutes
      les tables de tous les namespaces exposées en vues DuckDB `iceberg_scan` (`<namespace>_<table>`,
      rien en mémoire), cellule SQL.
      Ne plante plus sur une branche sans table.
- [ ] Se passer de PyIceberg avec une version à jour de DuckDB : vérifier que `ATTACH` sur une
      branche Nessie fonctionne (lecture + écriture + `CREATE OR REPLACE`), et voir ce que ça
      simplifie (plugins dbt, `catalog.py`).
      Tests du 15/10/2026 (branche jetable, `main` intact) :
      - DuckDB 1.5.6 (stable) et son extension `core_nightly` : **KO**, adresse
        `/iceberg/<br>/v1/<br>|warehouse/…` (extension tirée de la branche 1.5, sans le correctif).
      - DuckDB `2.0.0.dev2610011535` (préversion PyPI) : **lecture OK** sur la branche ;
        `CREATE TABLE AS`, `INSERT`, `DELETE`, `DROP` OK avec `SET iceberg_use_metadata_log = false` ;
        `CREATE OR REPLACE` toujours refusé (#784) → passer par DROP + CREATE.
      - Mode d'emploi et plan d'intégration dans dbt : [`docs/project/duckdb-2.0.md`](docs/project/duckdb-2.0.md).

## Tri et réorganisation (branche `repo-cleanup`)

- [x] `presentation/` déplacé dans `docs/presentation/`.
- [x] Docs obsolètes supprimés (nix, MinIO, Spark, pynessie, doublon CLI), le reste mis à jour en anglais.
- [x] Structure : `docs/concepts/` (général), `docs/project/` (ce qu'on a construit),
      `docs/presentation/` (talk, en français), index `docs/README.md`. README racine en anglais.
