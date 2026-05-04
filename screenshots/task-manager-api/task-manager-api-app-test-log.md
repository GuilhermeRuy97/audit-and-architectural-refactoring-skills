## Health

```
Invoke-RestMethod http://localhost:5000/health
```

```
status timestamp
------ ---------
ok     2026-05-04 13:08:37.185208
```

## Register

```
Invoke-RestMethod http://localhost:5000/users -Method POST `
>>   -Body '{"name":"Alice","email":"alice@test.com","password":"secret99","role":"admin"}' `
>>   -ContentType "application/json"
```

```
active     : True
created_at : 2026-05-04 16:09:42.232428
email      : alice@test.com
id         : 2
name       : Alice
role       : admin
```

## Auth guard
```
try { Invoke-RestMethod http://localhost:5000/tasks } catch { $_.Exception.Response.StatusCode }
```

```
Unauthorized
```

```
try {
    Invoke-RestMethod http://localhost:5000/tasks -Headers @{ Authorization = "Bearer fake-jwt-token-1" }
} catch { $_.Exception.Response.StatusCode }
```

```
Unauthorized
```

## Tasks

```
# List all tasks
Invoke-RestMethod http://localhost:5000/tasks -Headers $h

# Create a task (due_date in the past → overdue: true)
$task = Invoke-RestMethod http://localhost:5000/tasks -Method POST `
  -Body '{"title":"My first task","priority":1,"due_date":"2024-01-01"}' `
  -ContentType "application/json" -Headers $h

# Get a single task
Invoke-RestMethod "http://localhost:5000/tasks/$($task.id)" -Headers $h

# Update status
Invoke-RestMethod "http://localhost:5000/tasks/$($task.id)" -Method PUT `
  -Body '{"status":"done"}' -ContentType "application/json" -Headers $h

# Search by keyword
Invoke-RestMethod "http://localhost:5000/tasks/search?q=first" -Headers $h

# Stats
Invoke-RestMethod http://localhost:5000/tasks/stats -Headers $h

# Delete
Invoke-RestMethod "http://localhost:5000/tasks/$($task.id)" -Method DELETE -Headers $h
```

```
category_id :
created_at  : 2026-05-04 16:14:23.345483
description :
due_date    : 2024-01-01 00:00:00
id          : 1
overdue     : True
priority    : 1
status      : pending
tags        : {}
title       : My first task
updated_at  : 2026-05-04 16:14:23.345483
user_id     :

category_id : 
created_at  : 2026-05-04 16:14:23.345483
description :
due_date    : 2024-01-01 00:00:00
id          : 1
overdue     : False
priority    : 1
status      : done
tags        : {}
title       : My first task
updated_at  : 2026-05-04 16:14:23.362004
user_id     :

category_id :
created_at  : 2026-05-04 16:14:23.345483
description :
due_date    : 2024-01-01 00:00:00
id          : 1
overdue     : False
priority    : 1
status      : done
tags        : {}
title       : My first task
updated_at  : 2026-05-04 16:14:23.362004
user_id     :

cancelled       : 0
completion_rate : 100.0
done            : 1
in_progress     : 0
overdue         : 0
pending         : 0
total           : 1

message : Task deletada com sucesso
```

## Categories

```
# List
Invoke-RestMethod http://localhost:5000/categories -Headers $h

# Create
$cat = Invoke-RestMethod http://localhost:5000/categories -Method POST `
  -Body '{"name":"Backend","color":"#3498db"}' `
  -ContentType "application/json" -Headers $h

# Update
Invoke-RestMethod "http://localhost:5000/categories/$($cat.id)" -Method PUT `
  -Body '{"name":"Backend Dev"}' -ContentType "application/json" -Headers $h

# Delete
Invoke-RestMethod "http://localhost:5000/categories/$($cat.id)" -Method DELETE -Headers $h
```

```
color       : #3498db
created_at  : 2026-05-04 16:00:20.278719
description :
id          : 1
name        : Backend
task_count  : 0

color       : #3498db
created_at  : 2026-05-04 16:15:03.208290
description :
id          : 2
name        : Backend Dev

message : Categoria deletada
```

## Users

```
# List all users
Invoke-RestMethod http://localhost:5000/users -Headers $h

# Get a specific user
Invoke-RestMethod http://localhost:5000/users/1 -Headers $h

# Get a user's tasks
Invoke-RestMethod http://localhost:5000/users/1/tasks -Headers $h

# Update a user
Invoke-RestMethod http://localhost:5000/users/1 -Method PUT `
  -Body '{"name":"Alice Updated"}' -ContentType "application/json" -Headers $h
```

```
active     : True
created_at : 2026-05-04 15:59:08.845562
email      : admin@test.com
id         : 1
name       : Test Admin
role       : admin
task_count : 0

active     : True
created_at : 2026-05-04 16:09:42.232428
email      : alice@test.com
id         : 2
name       : Alice
role       : admin
task_count : 0

active     : True
created_at : 2026-05-04 15:59:08.845562
email      : admin@test.com
id         : 1
name       : Test Admin
role       : admin
tasks      : {}

active     : True
created_at : 2026-05-04 15:59:08.845562
email      : admin@test.com
id         : 1
name       : Alice Updated
role       : admin
```

## Reports

```
# Summary report (all users, tasks by status/priority, overdue list)
Invoke-RestMethod http://localhost:5000/reports/summary -Headers $h

# Per-user report
Invoke-RestMethod http://localhost:5000/reports/user/1 -Headers $h
```

```
generated_at      : 2026-05-04 16:15:59.671882
overdue           : @{count=0; tasks=System.Object[]}
overview          : @{total_categories=1; total_tasks=0; total_users=2}
recent_activity   : @{tasks_completed_last_7_days=0; tasks_created_last_7_days=0}
tasks_by_priority : @{critical=0; high=0; low=0; medium=0; minimal=0}
tasks_by_status   : @{cancelled=0; done=0; in_progress=0; pending=0}
user_productivity : {@{completed_tasks=0; completion_rate=0.0; total_tasks=0; user_id=1; user_name=Alice Updated}, @{completed_tasks=0; completion_rate=0.0; total_tasks=0; user_id=2; user_name=Alice}}

statistics : @{cancelled=0; completion_rate=0.0; done=0; high_priority=0; in_progress=0; overdue=0; pending=0; total_tasks=0}
user       : @{email=admin@test.com; id=1; name=Alice Updated}
```

## Seed realistic data

```
.venv\Scripts\python.exe seed.py
```

```
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
```