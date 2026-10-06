---
name: sequence-diagram
description: Write, fix or restyle PlantUML sequence diagrams for software features in a consistent house style - actor labelled with a concrete user role (asked, never a generic "Actor") with a lifeline, requests orchestrated by the router/dispatcher, flat `break` blocks for errors, hierarchical step numbers (1., 3.1.1.), short prose labels, one participant per real source file named with a leading colon (":Client UI", ":AuthService"), and the full layer chain down to the database. Use this skill whenever the user asks for a sequence diagram, "sequence", "biểu đồ tuần tự", SDS/design-document diagrams, PlantUML or .puml files for a feature, use case or backlog item, or wants existing sequence diagrams checked, fixed, renumbered or regenerated - even if they only name the feature ("vẽ sequence cho Create Order", "make sequence diagrams for my backlog items").
---

# Sequence Diagram

These diagrams usually end up in a design document (SDS) as one image per function, where the document provides the heading. They are read side by side, so every diagram must look like it came from the same hand: same participant naming, same wording, same numbering, same way of drawing errors. They also have to be true to the code - a reviewer will compare them against it.

Read `references/patterns.md` before writing the first diagram of a session; it holds the building blocks (auth, validation, upload, service errors, client-side steps, multi-request flows). `assets/template.puml` is the starting file. `scripts/number_steps.py` numbers steps and lints the style.

## Step 1 - Settle the conventions first (mandatory: ask, don't guess)

Participant naming is the thing teams disagree on most, and a wrong guess means redrawing every diagram. This step is a hard gate: no diagram is written until participant naming and stereotype usage are confirmed by the user or by a convention the user has confirmed. Before drawing anything, look for an agreed convention:

1. A conventions file next to the diagrams (`SEQUENCE_CONVENTIONS.md` in the diagrams folder), or one the user points to.
2. Existing diagrams in the project - but only treat them as the convention if the user confirms they are the reference, since older diagrams may be the very thing being replaced.
3. A sample image the user provides.

If any of the points below is not settled by those sources, **ask the user** (use the AskUserQuestion tool when available; offer concrete options with a short example of how each renders). Do not fill gaps by inference - "it's probably X" is exactly the guess this step exists to prevent. A convention that is silent on stereotypes does not mean "no stereotypes" - ask. A participant whose name you are not sure of (what to call the client app, the database, a helper module) is also a question, not a guess.

- **Participant label format.** Default proposal is the UML anonymous-instance form with a leading colon - `":Client UI"`, `":Router"`, `":OrderController"`. Ask what the label after the colon should be: the source file/module name as written (`:orderController`), the class/component name (`:OrderController`), or a role name (`:Client UI`). Ask specifically about non-code participants such as the client, the database, external services ("Client UI" vs "Web App" vs "Mobile App"; "MongoDB" vs "Database").
- **UML stereotypes.** Ask explicitly whether participants need stereotypes, and in which form:
  - none - plain boxes;
  - text stereotypes on the box - `participant ":OrderController" as Ctrl <<control>>`;
  - UML shapes - `boundary` / `control` / `entity` / `database` instead of `participant`.
  If stereotypes are wanted, agree on the mapping (e.g. UI = boundary, controller/service = control, model = entity, DB = database).
- **Actor = a concrete user role, never a generic word.** The actor is labelled with the real role that performs the function in this system (`Manager`, `Cashier`, `Customer`...), never `Actor`, `User` or a placeholder. Ask: the list of roles the system has and their exact display names; the form (`Manager` or the instance form `:Manager`); and what to do when an endpoint allows several roles - draw the primary role only, show the roles joined in one label (`Admin / Manager`), or one diagram per role. If you can't tell from the code or the conventions which role performs a function, ask - don't pick one.
- **Label language** for messages (English Title Case is the default style; some teams want their own language).
- **Where files go and how they are named**, and the number prefix used in the header comment (e.g. `3.2.25`).

Write the answers into `SEQUENCE_CONVENTIONS.md` in the diagrams folder so the next session (or teammate) reuses them instead of asking again. Keep it short: a bullet per decision plus one example declaration block.

## Step 2 - Find the functions and read the real code

- If the user points at a backlog/task list, take the rows assigned to the person they name; each function becomes one diagram.
- Determine the actor for each function from the role restrictions in the code (e.g. which roles the route authorizes) and the agreed actor rule from Step 1. When the code allows more roles than the convention covers, or the function has no role check at all, ask which role to show.
- Trace each function through the actual code: route/endpoint definition (middleware order, role restrictions), validation, controller/handler, service, data-access/model, and the client screen when part of the behaviour runs client-side. Note every place that can fail and how the failure reaches the client.
- Don't copy from old diagrams or docs; they drift. If code and old diagram disagree, follow the code and mention it.

## Step 3 - One participant per real file

Each participant stands for one concrete source file/module (or one external system such as the database or a mail provider). Never merge two files into one box, even when they serve the same purpose - not `":OrderValidation + ValidateMiddleware"`, not `":Validation"` standing for a rules file *and* the middleware that runs them. If a request goes through two validation files, draw two participants, in the order the code calls them. Layers that don't exist in this code path don't appear. This keeps the diagram checkable against the codebase: every box maps to a file a reviewer can open.

Order participants left to right by first involvement: actor, client, router/dispatcher, error handler, middlewares in call order, controller, service(s), models/repositories in first-use order, external helpers (mailer, payment gateway), database last.

## Step 4 - Write the diagram (house style)

Start from `assets/template.puml`, rename participants per the agreed convention, and put `@@` where each step number goes.

- **No `title`** - the document heading sits outside the image.
- **Keep the header block** from the template (`hide footbox`, monochrome skinparams). Don't add `skinparam ParticipantPadding`; recent PlantUML prints a warning banner into the image for it.
- **Lifelines with activation bars**: `activate <Actor>` before step 1, `deactivate <Actor>` before `@enduml`; `++` on every callee, `--` on the matching return. Inside a `break`, only the error handler's bar opens and closes - the others keep running.
- **The router orchestrates**: each middleware returns to the router (`Proceed to Validation`, `Proceed to Controller`) and the router makes the next call; middlewares don't call each other.
- **Labels are short prose in Title Case**: `Send Create Order Request`, `Find Order By ID`, `Return 404 Not Found`, `Show "Order Not Found"`. No function names, JSON, query strings or URLs on arrows - mixing code and prose makes diagrams inconsistent. Endpoint and roles go in the header comment.
- **Errors are flat `break` blocks** (never nested `alt/else`); condition in lower-case prose: `break Invalid or missing token`. Place a break right after the step whose result triggers it; several breaks after one step are fine.
- **Numbering is generated**: main flow `1.`, `2.` ...; the k-th break after step N is `N.k.1.`, `N.k.2.` ... Never number by hand.
- **The actor is a named role** (`actor "Manager" as Actor`), as agreed in Step 1 - not `Actor` or `User`. The alias can stay `Actor` so the building blocks work unchanged; only the displayed label changes.
- **Start and end with the actor**: first a user action (`Click "Delete Order"`), last what the user sees (`Show "Order Deleted" & Refresh List`). Deletes get `Show Confirmation Dialog` / `Confirm Deletion`. Every break ends with the client showing something to the actor (a 401 typically ends `Clear Token & Redirect to Login` if the client really does that - check).
- **Client-only behaviour stays on the client** (`Client -> Client : Filter Items By Name`); don't draw API calls the client doesn't make.

## Step 5 - Number, lint, render, look

1. `python <skill-dir>/scripts/number_steps.py <files...>` - replaces `@@`, then lints. Flags: `--shapes` if the convention uses boundary/control/entity shapes, `--no-colon` only if the user chose labels without a leading colon. Fix everything it reports. To renumber an edited file, put `@@` back on the changed labels (or all of them) and rerun.
2. Render with PlantUML. If it isn't installed, download the jar into a temp/scratch folder (`https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar`), then `java -jar plantuml.jar -charset UTF-8 -checkonly <files>` and `-tpng -o <tmp-out> <files>`. Keep PNGs out of the repo unless asked.
3. Open at least one rendered PNG and compare it with the sample/reference the team uses.

## Being faithful to the code

Draw the error path the way the code really delivers it (snippets in `references/patterns.md`):

| What the code does | Path in the diagram |
|---|---|
| auth middleware rejects (missing/invalid token, role not allowed) | auth → router → error handler → client (401 / 403) |
| validation passes errors to the framework error handler | validation → router → error handler (400) |
| validation middleware writes the 400 response itself | validation → router → client, no error handler |
| service throws and the controller forwards it (async wrapper / `next(err)`) | service → controller → `Forward Error` → router → error handler |
| controller catches and responds itself | service → controller → `Return 4xx Error Response` → router → client |
| upload middleware rejects the file | upload → router → error handler (status as produced) |
| database constraint error not mapped to a domain error | DB/model → service → … → error handler, usually 500 |

Add a 403 break only when a role is actually excluded. Skip branches the code can't reach, and tell the user about such bugs instead of drawing them.

## Reporting back

List the files written, which checks and renders passed, the conventions used (and whether they came from the user, the conventions file, or a confirmed reference), anything in the code that looked wrong, and any choice you made between two plausible readings.
