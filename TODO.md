# TODO — présentation Nessie (15/10/2026)

## 1. Faire tourner la démo dans son état actuel

- [x] `mise.toml` : variables utiles de `.envrc` (dbt, `AWS_*` vers MinIO). Les variables PySpark
      et `NESSIEDIR` / `PYICEBERG_HOME` ne servaient plus.
- [x] `nessie-cli` : service compose (profil `tools`) lancé par `mise run cli`, sur le réseau compose
      (plus de `--network host`). Accepte les options du CLI, ex. `mise run cli -c "LIST REFERENCES;"`.
- [x] Taskfile → tâches mise. `run` / `fail` renommées `pipeline` / `pipeline-bad`. Doc et slides
      mises à jour.
- [x] Images MinIO : les images officielles ne sont plus publiques (Docker Hub et quay.io → 401).
      Remplacées par le fork communautaire `pgsty/minio` + `pgsty/mc`, tags fixés.
- [x] Dry-run (stack repartie de zéro) : `reset`, `up`, `pipeline`, `pipeline-bad`, `branches`,
      `dbt-inspect`, `cli`, rollback `ASSIGN BRANCH main TO release-…` (10 → 5 lignes), notebook
      exécuté en headless.
- [x] Testés à la main : le notebook (`mise run notebook`) et le REPL (`mise run cli`).
- [x] `.envrc` et `.direnv/` supprimés.

## 2. Corrections avant ce soir

- [ ] Slide « Maturité » + `plan.md` : le bug DuckDB #1145 est corrigé (PR #1230, mergée le
      26/07/2026). Vérifier dans quelle version de DuckDB le correctif est publié, puis reformuler.
- [ ] Slide « Maturité » : Trino #24134 a été fermée en « not planned » (une syntaxe dédiée aux
      branches est annoncée). Préciser.
- [ ] README : `pipeline_YYYYMMDD` → `pipeline-HHMMSS`, ajouter les tags `release-HHMMSS`, mettre à
      jour le déroulé.
- [ ] Notebook : aligner sa description (README + acte 3) sur ce qu'il fait réellement.
- [ ] « 100 % local, zéro Java » : nuancer (le serveur Nessie est en Java/Quarkus, dans un conteneur).
- [ ] Mineur : `--keep` dans `pipeline.py` ne fait rien.

## 3. Approfondir les concepts (questions / réponses)

- [ ] Session de questions sur Iceberg, Nessie et la stack ; décider après chaque réponse si une
      slide doit évoluer.

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
