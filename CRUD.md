## Endponts 
_(Json will be added later)_

| Endpoint                      | Usage                              | Request method | Access         | Request body/parameters      | Response status | Response body |
|-------------------------------|------------------------------------|----------------|----------------|------------------------------|-----------------|---------------|
| **Movies**                    | ---                                | ---            | ---            | ---                          | ---             | ---           |
| /movies                       | To get a list of films             | GET            | Everyone       | search, status, sort, offset | 200 OK          |               | 
| /movies?status=screened       | To get films that being screened   | GET            | Everyone       | search, sort, offset         | 200 OK          |               | 
| /movies?status=soon_available | To get that will be soon available | GET            | Everyone       | search, sort, offset         | 200 OK          |               | 
| /movies/{id}                  | To get films' info                 | GET            | Everyone       | -                            | 200 OK          |               | 
| /movies                       | To add a film                      | POST           | Admin          |                              | 201 Created     |               | 
| /movies/{id}                  | To update films' info              | PUT            | Admin          |                              | 200 OK          |               | 
| /movies/{id}                  | To delete film                     | DELETE         | Admin          |                              | 204 No Content  | -             |
| **Cinemas**                   | ---                                | ---            | ---            | ---                          | ---             | ---           |
| /cinemas                      | To get a list of cinemas           | GET            | Everyone       | -                            | 200 OK          |               | 
| /cinemas/{id}                 | To get cinemas' info               | GET            | Everyone       | -                            | 200 OK          |               |
| /cinemas                      | To add a cinema                    | POST           | Admin          |                              | 201 Created     |               | 
| /cinemas/{id}                 | To update cinemas' info            | PUT            | Admin          |                              | 200 OK          |               | 
| /cinemas/{id}                 | To delete cinema                   | DELETE         | Admin          |                              | 204 No Content  | -             |
| **Authorization**             | ---                                | ---            | ---            |                              | ---             | ---           |
| /users                        | To get a list of users             | GET            | Admin          | -                            | 200 OK          |               | 
| /users/{id}                   | To get users profile               | GET            | Owner or admin | -                            | 200 OK          |               | 
| /register                     | To register a new user             | POST           | Everyone       |                              | 201 Created     |               | 
| /login                        | To login in account                | POST           | Everyone       |                              | 200 OK          |               | 
| /users/{id}                   | To update user's profile           | PUT            | Owner or admin |                              | 200 OK          |               |
| /users/{id}                   | To delete user's profile           | DELETE         | Owner or admin |                              | 204 No Content  | -             |
| **Help**                      | ---                                | ---            | ---            | ---                          | ---             | ---           |
| /help                         | To get help/info                   | GET            | Everyone       | -                            | 200 OK          |               |
| **Information about us**      | ---                                | ---            | ---            |                              | ---             | ---           |
| /info                         | To get info about us               | GET            | Everyone       | -                            | 200 OK          |               | 
