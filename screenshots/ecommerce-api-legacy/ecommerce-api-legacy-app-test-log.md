## Health
```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 15
ETag: W/"f-VaSQ4oDUiZblZNAEkkN+sX+q3Sg"
Date: Sun, 03 May 2026 17:49:32 GMT
Connection: close

{
  "status": "ok"
}
```

# Auth

## Login

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 171
ETag: W/"ab-7baN6IcQ9Zs7dKcHbkJQKh2rd4c"
Date: Sun, 03 May 2026 17:50:03 GMT
Connection: close

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsIiIsImlhdCI6MTc3NzgzMDYwMywiZXhwIjoxNzc3ODU5NDAzfQ.jEhMBfQHoRyHtlY4HLxQWN05mcda78bykPn2C6svqBs"
}
```

## Register

```
HTTP/1.1 201 Created
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 12
ETag: W/"c-SFjeaFTlhYiJ2dKSCI6wkDN8DUU"
Date: Sun, 03 May 2026 17:50:35 GMT
Connection: close

{
  "userId": 2
}
```

# Checkout

## Approved

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 35
ETag: W/"23-pcPozAYVr0Z8Hc9ZB5uZF+mIuHM"
Date: Sun, 03 May 2026 18:00:20 GMT
Connection: close

{
  "msg": "Success",
  "enrollment_id": 4
}
```

## Denied

```
HTTP/1.1 400 Bad Request
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 74
ETag: W/"4a-X7OASrMg4i+4stHEHR2WTdKa8f8"
Date: Sun, 03 May 2026 18:00:42 GMT
Connection: close

{
  "error": "Payment denied — only Visa cards accepted in this simulation"
}
```

## No token

```
HTTP/1.1 401 Unauthorized
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 35
ETag: W/"23-5acMW0iwqotvKDNixkkFKwa08HY"
Date: Sun, 03 May 2026 18:01:01 GMT
Connection: close

{
  "error": "Authentication required"
}
```

# Admin

## Financial Report

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 236
ETag: W/"ec-sVvG8nBfmOO12w/s+6jXhYvzIv8"
Date: Sun, 03 May 2026 18:01:09 GMT
Connection: close

[
  {
    "course": "Clean Architecture",
    "revenue": 997,
    "students": [
      {
        "student": "Leonan",
        "paid": 997
      }
    ]
  },
  {
    "course": "Docker",
    "revenue": 1491,
    "students": [
      {
        "student": "Leonan",
        "paid": 497
      },
      }
    ]
  }
]
```

## Delete User

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 55
ETag: W/"37-tUffHnBPPYnDMEOFZRza3qLf4SA"
Date: Sun, 03 May 2026 18:01:35 GMT
Connection: close

{
  "msg": "User and related records deleted successfully"
}
```