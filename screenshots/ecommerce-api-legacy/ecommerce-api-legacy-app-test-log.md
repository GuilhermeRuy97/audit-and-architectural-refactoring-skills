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
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc3NzgzMDYwMywiZXhwIjoxNzc3ODU5NDAzfQ.jEhMBfQHoRyHtlY4HLxQWN05mcda78bykPn2C6svqBs"
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
HTTP/1.1 401 Unauthorized
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 36
ETag: W/"24-GNDyEGK1yBKJB1sFHYU2n5ZGC54"
Date: Sun, 03 May 2026 17:51:04 GMT
Connection: close

{
  "error": "Invalid or expired token"
}
```

## Denied

```
HTTP/1.1 401 Unauthorized
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 36
ETag: W/"24-GNDyEGK1yBKJB1sFHYU2n5ZGC54"
Date: Sun, 03 May 2026 17:51:25 GMT
Connection: close

{
  "error": "Invalid or expired token"
}
```

## No token

```
HTTP/1.1 401 Unauthorized
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 35
ETag: W/"23-5acMW0iwqotvKDNixkkFKwa08HY"
Date: Sun, 03 May 2026 17:51:37 GMT
Connection: close

{
  "error": "Authentication required"
}
```

# Admin

## Financial Report

```
HTTP/1.1 401 Unauthorized
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 36
ETag: W/"24-GNDyEGK1yBKJB1sFHYU2n5ZGC54"
Date: Sun, 03 May 2026 17:51:48 GMT
Connection: close

{
  "error": "Invalid or expired token"
}
```

## Delete User

```
HTTP/1.1 401 Unauthorized
X-Powered-By: Express
Content-Type: application/json; charset=utf-8
Content-Length: 36
ETag: W/"24-GNDyEGK1yBKJB1sFHYU2n5ZGC54"
Date: Sun, 03 May 2026 17:52:03 GMT
Connection: close

{
  "error": "Invalid or expired token"
}
```