https://projectnessie.org/nessie-latest/cli/#repl-commands

```sql
-- Connect to nessie (Iceberg REST URI recommended in doc)
connect to http://localhost:19120/iceberg

-- List references (branches / tags):
list references

-- list contents (tables / views)
list contents

-- show current branch
show reference

-- switch branch
use <branch>

-- create a branch
create branch dev
use branch dev

create namespace ooo
list contents

```
