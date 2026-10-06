# Building blocks

Copy the block that matches how the code behaves, then adapt the condition and the final `Show ...` text. Aliases follow `assets/template.puml`: `Actor`, `UI` (client), `Router`, `Err` (error handler), `Auth`, `Upload`, `Rules` (validation rules file), `Validate` (middleware that collects/raises validation errors), `Ctrl`, `Svc`, `Model`, `DB`. Display labels come from the agreed convention - the examples use the colon form (`":XxxService"`).

## Contents
1. Declaring participants (plain, text stereotype, UML shapes)
2. Authentication / authorization
3. Upload
4. Validation
5. Service errors
6. Database-level errors
7. Optional work and early exits
8. Client-side only steps
9. Multi-request flows
10. Mapping layers in common stacks

## 1. Declaring participants

One participant per real file/module or external system. Declare them in first-involvement order.

Plain (no stereotypes):
```
actor "Manager" as Actor
participant ":Client UI" as UI
participant ":Router" as Router
participant ":OrderController" as Ctrl
participant ":OrderService" as Svc
participant ":OrderModel" as Model
participant ":Database" as DB
```
Text stereotypes (only if the user asked for them):
```
participant ":Client UI" as UI <<boundary>>
participant ":OrderController" as Ctrl <<control>>
participant ":OrderService" as Svc <<control>>
participant ":OrderModel" as Model <<entity>>
participant ":Database" as DB <<database>>
```
UML shapes (only if the user asked for them; lint with `--shapes`):
```
boundary ":Client UI" as UI
control ":OrderController" as Ctrl
entity ":OrderModel" as Model
database ":Database" as DB
```
Two validation files on one route = two participants:
```
participant ":orderValidation" as Rules
participant ":validateMiddleware" as Validate
```
Never `participant ":orderValidation + validateMiddleware"`.

## 2. Authentication / authorization

Authentication only (no role restriction, or every role allowed):
```
Router -> Auth ++ : @@ Verify Authentication
break Invalid or missing token
  Auth --> Router : @@ Throw 401 Unauthorized Error
  Router -> Err ++ : @@ Handle Error
  Err --> UI -- : @@ Return 401 Unauthorized
  UI --> Actor : @@ Clear Token & Redirect to Login
end
Auth --> Router -- : @@ Proceed to Validation
```
When a role is excluded, label the call `Verify Authentication & Role` and add right after the first break:
```
break Insufficient role
  Auth --> Router : @@ Throw 403 Forbidden Error
  Router -> Err ++ : @@ Handle Error
  Err --> UI -- : @@ Return 403 Forbidden
  UI --> Actor : @@ Show Access Denied Message
end
```
If authentication and role checks live in different files, they are different participants. Public endpoints have no auth participant. The proceed label names the next stop (`Proceed to Upload`, `Proceed to Validation`, `Proceed to Controller`).

## 3. Upload

```
Router -> Upload ++ : @@ Upload Xxx Image (If Any)
break File is not an image or too large
  Upload --> Router : @@ Throw Upload Error
  Router -> Err ++ : @@ Handle Error
  Err --> UI -- : @@ Return 400 Bad Request
  UI --> Actor : @@ Show "Invalid Image File"
end
Upload -> Upload : @@ Save Image & Attach Image Path
Upload --> Router -- : @@ Proceed to Validation
```
Use the status the code really produces (some upload libraries raise errors without a status, which the error handler turns into 500).

## 4. Validation

Rules file + middleware that forwards errors to the framework error handler:
```
Router -> Rules ++ : @@ Check Xxx Data Rules
Rules --> Router -- : @@ Return Rule Results
Router -> Validate ++ : @@ Collect Validation Errors
break Invalid name, price or items
  Validate --> Router : @@ Throw 400 Validation Error
  Router -> Err ++ : @@ Handle Error
  Err --> UI -- : @@ Return 400 Bad Request
  UI --> Actor : @@ Show Validation Error
end
Validate --> Router -- : @@ Proceed to Controller
```
A single validation file that writes the 400 response itself:
```
Router -> Rules ++ : @@ Validate Xxx Data
break Missing field or invalid email
  Rules --> Router : @@ Return 400 Error Response
  Router --> UI : @@ Return 400 Bad Request
  UI --> Actor : @@ Show Validation Error
end
Rules --> Router -- : @@ Proceed to Controller
```
Name the break after what the rules really check, briefly.

## 5. Service errors

Controller forwards errors to the error handler (async wrapper, `next(err)`, exception filter, `@ControllerAdvice`...):
```
break Xxx not found
  Svc --> Ctrl : @@ Throw 404 Not Found Error
  Ctrl --> Router : @@ Forward Error
  Router -> Err ++ : @@ Handle Error
  Err --> UI -- : @@ Return 404 Not Found
  UI --> Actor : @@ Show "Xxx Not Found"
end
```
Controller catches and answers itself:
```
break Xxx not found
  Svc --> Ctrl : @@ Throw 404 Not Found Error
  Ctrl --> Router : @@ Return 404 Error Response
  Router --> UI : @@ Return 404 Not Found
  UI --> Actor : @@ Show "Xxx Not Found"
end
```
Check the catch block for the real status (e.g. `error.status || 400`).

Status names: 400 `Bad Request`, 401 `Unauthorized`, 403 `Forbidden`, 404 `Not Found`, 409 `Conflict`, 422 `Unprocessable Entity`, 429 `Too Many Requests`, 500 `Internal Server Error`.

A check that needs no data access (comparison, permission, price rule) gets a self-call so the break has a step to follow:
```
Svc -> Svc : @@ Check Duplicate Items
break Same item added twice
  ...
end
```
Rules evaluated at the same point may share one break (`break Price above original price or end date not after start date`).

## 6. Database-level errors

Constraint violation that isn't mapped to a domain error:
```
Model -> DB ++ : @@ Insert User
DB --> Model -- : @@ Return Insert Result
break Username or email already exists
  Model --> Svc : @@ Throw Duplicate Key Error
  Svc --> Ctrl : @@ Throw Error
  Ctrl --> Router : @@ Forward Error
  Router -> Err ++ : @@ Handle Error
  Err --> UI -- : @@ Return 500 Internal Server Error
  UI --> Actor : @@ Show Error Message
end
```
Schema validation inside the model: `Model -> Model : @@ Validate Xxx Schema`, then a break starting at `Model --> Svc`. Model-internal work is a self-call (`Model -> Model : @@ Hash Password`).

## 7. Optional work and early exits

Put optional work in the label rather than an `opt` block: `Find New Category (If Changed)`, `Generate Code (If Empty)`. A successful early exit (e.g. filter by something that doesn't exist returns an empty list) is still a `break`, ending with `Return 200 OK` and `Show Empty Xxx List`.

## 8. Client-side only steps

Load from the API normally, show the list without closing the client bar (`UI --> Actor : @@ Show Xxx List`), then:
```
Actor -> UI : @@ Type Keyword In Search Box
UI -> UI : @@ Filter Xxx By Name
UI --> Actor -- : @@ Show Matching Xxx
```
Same for a detail view opened from already loaded data - no API call.

## 9. Multi-request flows

A function spanning several requests (e.g. request OTP -> verify OTP -> reset password) is one diagram with one running number sequence. Between requests the client shows the next form without closing its bar (`UI --> Actor : @@ Show OTP Input Form`) and the actor acts again (`Actor -> UI : @@ Enter OTP & Click "Verify"`). External helpers (mail, SMS, payment) are participants placed before the database.

## 10. Mapping layers in common stacks

Use the files that actually exist; these are only hints for where to look.

| Stack | Router / dispatcher | Middleware / filters | Controller | Service | Data access | Error handler |
|---|---|---|---|---|---|---|
| Express / Node | `routes/*.js` | `middlewares/*`, validation files | `controllers/*` | `services/*` | `models/*` (Mongoose/Sequelize) | error middleware |
| NestJS | module routing | guards, pipes, interceptors | `*.controller.ts` | `*.service.ts` | repositories / entities | exception filters |
| Spring Boot | DispatcherServlet | filters, interceptors, `@Valid` | `@RestController` | `@Service` | `@Repository` / JPA entities | `@ControllerAdvice` |
| ASP.NET Core | routing middleware | middleware, filters | controllers | services | DbContext / repositories | exception middleware |
| Django / DRF | `urls.py` | middleware, permissions, serializers | views / viewsets | services (if any) | models / ORM | exception handler |
