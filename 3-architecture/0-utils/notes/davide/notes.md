
# 1. Componenti che avevo guardato

cartelle toccate / considerate:

```text
src/app
src/appshell
src/projectscene
src/trackedit
src/uicomponents
src/toast
src/au3wrap
src/project
src/audio
src/playback
src/record
src/effects
src/au3cloud
src/importexport
```

idea generale: Audacity è un monolite modulare, quindi non stiamo dividendo in servizi separati, però dentro `src/` ci sono moduli abbastanza chiari.

---

# 2. Desktop App UI / componenti principali

## Audacity Application Bootstrap

tocca:

```text
src/app/main.cpp
src/app/appfactory.cpp
src/app/guiapp.h
```

note:
- è il punto da cui parte l'app
- interpreta il run mode
- crea l'applicazione corretta
- inizializza il resto
- quindi Audacity non parte “direttamente dalla finestra”
- prima c'è bootstrap applicativo, poi parte la UI

flusso mentale:

```text
main / appfactory
  -> crea app
  -> registra moduli
  -> fa partire UI
```

---

## App Shell Module

= `src/appshell`

tocca:

```text
src/appshell/appshellmodule.cpp
src/appshell/internal/applicationactioncontroller.cpp
src/appshell/internal/applicationuiactions.cpp
src/appshell/internal/startupscenario.cpp
src/appshell/internal/sessionsmanager.cpp
```

note:
- gestisce roba tipo finestre, dialog, startup, sessioni, azioni globali
- la considero come “scocca” dell'app
- dentro ha pezzi importanti, ma nel diagramma si può accorpare un po'
- flusso molto base:

```text
app bootstrap -> app shell
```

---

## Application Action Controller

tocca:

```text
src/appshell/internal/applicationactioncontroller.cpp
src/appshell/iapplicationactioncontroller.h
```

note:
- componente importante
- raccoglie interazione utente
- la inoltra a un layer di action/controller
- poi quel layer decide quale servizio/modulo attivare
- utile perché la UI non deve chiamare tutto direttamente

idea:

```text
utente clicca qualcosa
  -> action controller
    -> modulo giusto
```

---

## Project Scene Module

tocca:

```text
src/projectscene/view/timeline
src/projectscene/view/trackspanel
src/projectscene/view/tracksitemsview
src/projectscene/view/toolbars
src/projectscene/view/statusbar
src/projectscene/view/playcursor
src/projectscene/view/trackruler
src/projectscene/qml
```

note:
- vista a progetto aperto
- tracce, timeline, pannelli, cursore, toolbar, status bar
- è una delle parti più centrali perché è dove l'utente passa più tempo
- nel diagramma aggiornato questa roba può finire dentro un componente più accorpato tipo:

```text
Timeline Visualization and Editing
```

---

## Track Edit Module

tocca:

```text
src/trackedit/api
src/trackedit/dom
src/trackedit/internal
src/trackedit/internal/au3
src/trackedit/view
src/trackedit/qml
```

note:
- gestisce editing delle tracce
- collegato a Project Scene / Timeline
- nel diagramma aggiornato può anche essere accorpato con timeline/editing

---

## UI Components / Toast

prima li avevo separati:

```text
UI Components Module
Toast Module
```

poi nel diagramma aggiornato:
- toast è stato integrato nella UI
- ci sta, perché è feedback/notifica utente
- quindi componente unico tipo:

```text
UI Elements
```

che contiene:
- componenti UI riusabili
- toolbar / pannelli
- popup / notifiche / toast
- controlli visuali

---

# 3. Effects / Plugin Engine

## nota sul nome

prima lo chiamavo:

```text
Plugin Engine
```

poi meglio:

```text
Effects and Plugins Engine
```

perché nella codebase i plugin sono molto legati a `src/effects`.

---

## Effects Base Module

tocca:

```text
src/effects/effects_base
```

note:
- centro del sistema effetti/plugin
- base comune
- gestisce in modo più astratto gli effetti
- poi delega ai provider specifici

idea:

```text
Effects Base
  -> Builtin
  -> Nyquist
  -> VST
  -> LV2
  -> Audio Unit
  -> Vamp
```

---

## Effects UI / Menus

tocca:

```text
src/effects/effects_base/qml
src/effects/effects_base/view
src/projectscene/view/toolbars/geteffectsmodel.cpp
```

note:
- ponte tra “utente sceglie effetto” e “sistema carica/esegue effetto”
- non basta caricare plugin, devono anche comparire in menu / toolbar / UI

---

## Builtin Effects Module

tocca:

```text
src/effects/builtin
src/effects/builtin_collection
```

note:
- effetti nativi di Audacity
- meglio separarli dai plugin esterni
- sono built-in, non installati dall'utente

---

## Nyquist Effects Module

tocca:

```text
src/effects/nyquist
thirdparty/libnyquist
share/nyquist-plug-ins
share/nyquist-runtime
```

note:
- Nyquist importante perché permette plugin/script
- utile anche per academic user
- dal sito: linguaggio per sound synthesis/analysis basato su Lisp
- quindi non è solo “effetto”, è anche estendibilità/custom plugin

---

## VST / LV2 / Audio Unit / Vamp

tocca:

```text
src/effects/vst
src/effects/lv2
src/effects/audio_unit
src/effects/vamp
```

note:
- altri formati plugin supportati
- nel diagramma si possono mettere come moduli separati
- non dire solo “Nyquist + OpenVINO”, perché manca roba
- OpenVINO va trattato diversamente, vedi sotto

---

## OpenVINO AI Tools

note:
- ho trovato riferimenti, ma non modulo interno chiaro tipo `src/effects/openvino`
- quindi meglio non trattarlo come componente interno stabile
- meglio come sistema esterno / plugin opzionale
- wording prudente:

```text
May support optional AI plugin integration
```

non:

```text
Loads plugins from OpenVINO
```

che sembra troppo forte.

---

# 4. Flussi generali

## desktop app ui flow

```text
User
  -> App Shell / UI Elements
  -> Application Action Controller
  -> Project Scene / Timeline / Effects UI
  -> Project / Audio / Plugin / Cloud modules
```

nota:
- la UI non fa tutto
- raccoglie azioni e chiede ai moduli giusti

---

## plugin flow

```text
User selects an effect/plugin
  -> Effects UI / Menus
  -> Effects Base Module
  -> specific effect/plugin provider
       - Builtin Effects
       - Nyquist
       - VST
       - LV2
       - Audio Unit
       - Vamp
       - optional OpenVINO AI tools
  -> audio/project data is modified
  -> UI is updated
```

nota:
- anche qui UI non esegue direttamente plugin
- chiede esecuzione al sistema effetti/plugin

---

# 5. Container vs Component

## cosa importante detta con Leo

C4 container = applicazione o data store, qualcosa che ha senso deployare/eseguire da solo.

Quindi per Audacity:

```text
Desktop Application
Project File Database
```

ok come container.

Non ha senso mettere:

```text
Core Service
Cloud Service
Effects Service
```

come container se sono solo pezzi interni dell'app desktop.

---

## container level

a livello container va bene:

```text
Desktop Application -> Project File Database
```

perché il container deployabile vero è l'app desktop.

questa relazione NON vuol dire che ogni classe UI parli diretta con SQLite.

vuol dire solo:

```text
l'app usa il database progetto
```

---

## component level

a livello component invece meglio essere più precisi:

```text
Timeline / Effects / Cloud
  -> Project Core
    -> Project File Database
```

quindi:
- no `Core Service` come container
- sì `Project Core` come componente interno

---

# 6. Relazioni e da dove vengono

## nota generale

- le relazioni NON sono tutte chiamate a funzione verificate
- non è un call graph
- è C4
- quindi sono relazioni architetturali / responsabilità / dipendenze tra moduli
- alcune sono molto probabili dalla codebase
- altre sono inferite guardando cosa fanno i componenti

cose usate per deciderle:
- struttura in `src/`
- responsabilità dei moduli
- coerenza con container diagram
- cosa ha senso a livello C4

---

# 7. Relazioni abbastanza safe

## Desktop Application -> Project File Database

```text
Desktop Application -> Project File Database
Reads from and writes to
```

- ok nel container diagram
- app desktop usa DB progetto
- non significa UI -> SQLite diretto

---

## Project Core -> Project File Database

```text
Project Core -> Project File Database
Reads and writes Audacity project files
```

- ok nel component diagram
- `Project Core` = stato progetto / persistenza / preferenze / contesto
- evita mille frecce al database

---

## Import/Export Module -> FFmpeg

```text
Import/Export Module -> FFmpeg
Decodes/encodes additional audio formats using
```

- abbastanza safe
- FFmpeg serve per import/export formati audio
- quindi nel component diagram va attaccato a import/export
- non alla UI generica

meglio:

```text
ImportExport -> FFmpeg
```

non:

```text
Desktop App UI -> FFmpeg
```

a livello container può restare generico, perché i componenti interni non si vedono.

---

## Effects and Plugins Engine -> OpenVINO

```text
Effects and Plugins Engine -> OpenVINO
May support optional AI plugin integration
```

- openvino sta lato plugin/effetti, se presente
- non attaccarlo a tutta la desktop app nel component diagram
- usare wording prudente
- non siamo sicuri sia implementato pienamente nella app refactorata

---

## Cloud Sync -> audio.com

```text
Cloud Sync -> audio.com
Syncs project files and handles authentication
```

- ok
- audio.com è sistema esterno cloud
- tecnologia:

```text
HTTPS/JSON
```

---

## Legacy Bridge

```text
Legacy Bridge
```

- rappresenta `au3wrap`
- ponte tra nuova architettura e vecchio core AU3
- adapter/bridge architetturale

---

# 8. Relazioni più inferite

## Application Entry -> moduli vari

```text
Application Entry -> UI Elements
Application Entry -> Project Core
Application Entry -> Audio Engine
Application Entry -> Effects and Plugins Engine
Application Entry -> Import/Export Module
Application Entry -> Cloud Sync
```

- relazione di bootstrap
- vuol dire inizializza/registra moduli
- non per forza call diretta a ogni classe

---

## UI Elements -> Timeline

```text
UI Elements -> Timeline Visualization and Editing
Displays and controls the project timeline
```

- sensata
- la UI mostra e controlla la timeline
- da verificare se serve call precisa

---

## UI Elements -> Effects and Plugins Engine

```text
UI Elements -> Effects and Plugins Engine
Shows effect/plugin actions and requests execution
```

- utente seleziona effetti dalla UI
- UI chiede al modulo effetti/plugin
- non esegue direttamente plugin

---

## UI Elements -> Import/Export Module

```text
UI Elements -> Import/Export Module
Requests import/export operations
```

- menu/dialog UI chiedono import/export
- logica vera nel modulo import/export

---

## Timeline -> Audio Engine

```text
Timeline -> Audio Engine
Requests playback, recording and audio visualization data
```

- plausibile
- timeline e playback/audio visualization sono collegati
- non scrivere che timeline controlla tutto l'audio

---

## Timeline -> Project Core

```text
Timeline -> Project Core
Reads and updates project state
```

- sensata
- timeline usa stato progetto, tracce, selezioni

---

## Timeline -> Legacy Bridge

```text
Timeline -> Legacy Bridge
Uses legacy project/track functionality through adapters
```

- architetturale
- alcune robe progetto/tracce stanno ancora nel vecchio AU3
- non significa che tutto passa per forza da lì

---

## Effects and Plugins -> Project Core

```text
Effects and Plugins Engine -> Project Core
Reads selected tracks and applies effect results
```

- ha senso
- effetti lavorano su tracce/progetto
- però magari nel codice passa anche da legacy/AU3

---

## Effects and Plugins -> Audio Engine

```text
Effects and Plugins Engine -> Audio Engine
Uses audio data/services during effect execution
```

- inferita
- effetti lavorano su audio
- ma non so se chiamano diretto `audioEngine`
- meglio wording morbido

---

## Effects and Plugins -> Legacy Bridge

```text
Effects and Plugins Engine -> Legacy Bridge
Bridges to legacy AU3 effect/plugin APIs
```

- plausibile
- effetti/plugin hanno ancora pezzi legacy
- `au3wrap` può stare in mezzo

---

## Audio Engine -> Legacy Bridge

```text
Audio Engine -> Legacy Bridge
Uses existing AU3 audio functionality where needed
```

- plausibile
- alcune parti audio possono ancora appoggiarsi ad AU3
- non spacciarla per call verificata al 100%

---

## Import/Export -> Project Core

```text
Import/Export Module -> Project Core
Imports/exports audio data associated with the current project
```

- dipendenza logica
- import deve mettere dati nel progetto
- export deve leggere dati dal progetto

---

## Import/Export -> Legacy Bridge

```text
Import/Export Module -> Legacy Bridge
Uses legacy import/export functionality where needed
```

- plausibile
- se import/export ha pezzi AU3 passa da lì
- da verificare se serve precisione estrema

---

## Cloud Sync -> Project Core

```text
Cloud Sync -> Project Core
Reads project metadata and sync state
```

- ha senso
- sync deve sapere progetto/stato/metadati
- potrebbe passare da servizi specifici, ma a livello architetturale ok

---

## Cloud Sync -> Database

```text
Cloud Sync -> Project File Database
Uploads/downloads local project files
```

- occhio
- non dire che fa query SQLite
- meglio dire file progetto locali
- potrebbe lavorare sul file `.aup3/.aup4`, non sul DB in senso query

meglio:

```text
Uploads/downloads local project files
```

non:

```text
Queries database
```

