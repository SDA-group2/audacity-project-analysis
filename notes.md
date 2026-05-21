# Miei componenti

cartelle toccati:

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
```

---


### Audacity Application Bootstrap

avvia l'applicazione, tocca:

```text
src/app/main.cpp
src/app/appfactory.cpp
src/app/guiapp.h
```

In pratica è il punto in cui l'app parte, interpreta il run mode, crea l'applicazione corretta e inizializza il resto.

NB!!!! Audacity non parte direttamente da una finestra grafica, ma da un bootstrap applicativo che prepara il contesto, i moduli e poi fa partire la UI.

---

### App Shell Module

= `src/appshell`.

gestisce --> finestre, dialog, controller, azioni etc., 
Dentro ha altri pezzi importanti, la considero come scocca e basta
tocca: 

```text
src/appshell/appshellmodule.cpp
src/appshell/internal/applicationactioncontroller.cpp
src/appshell/internal/applicationuiactions.cpp
src/appshell/internal/startupscenario.cpp
src/appshell/internal/sessionsmanager.cpp
```

flusso quindi per ora app --> shell

---

### Application Action Controller
 
uno dei componenti più importanti del diagramma.  raccoglie l'interazione dell'utente e la inoltra a un action/controller layer, che poi decide quale servizio o modulo attivare.

tocca: 

```text
src/appshell/internal/applicationactioncontroller.cpp
src/appshell/iapplicationactioncontroller.h
```

---

### Project Scene Module

visualizzazione a progetto aperto: tracce, timeline, pannelli, cursore, toolbar, status bar...
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

oggetivo parte centrale perche quella in cui l'utente passa + tempo

---

### Track Edit Module

gestisce l'editing delle tracce per cui collegata a sopra, tocca:

```text
src/trackedit/api
src/trackedit/dom
src/trackedit/internal
src/trackedit/internal/au3
src/trackedit/view
src/trackedit/qml
```

---

### UI Components Module

libreria di componenti UI

---

### Toast Module

modulo per notifiche, messaggi, feedback utente etc

---

## Plugin Engine

molto legato agli effect, proporrei di unirli

### Effects Base Module

centro perche fa da base per il sistema dei plugin, li gestisce tutti in modo astratto, tocca:

```text
src/effects/effects_base
```

---

### Effects UI / Menus

tocca:
```text
src/effects/effects_base/qml
src/effects/effects_base/view
src/projectscene/view/toolbars/geteffectsmodel.cpp
```

è il ponte tra scegliere un effetto e caricarlo

---

### Builtin Effects Module

```text
src/effects/builtin
src/effects/builtin_collection
```

effetti nativi che secondo me vanno separati dai plugin

---

### Nyquist Effects Module

Questo componente rappresenta:

```text
src/effects/nyquist
thirdparty/libnyquist
share/nyquist-plug-ins
share/nyquist-runtime
```

dal sito -> Nyquist is a programming language for sound synthesis and analysis based on the Lisp programming language. It is an extension of the XLISP dialect of Lisp, and is named after Harry Nyquist. It can be used to write plugin effects for Audacity. The Nyquist programming language and interpreter were written by Roger Dannenberg at Carnegie Mellon University, with support from Yamaha Corporation and IBM.

---

### VST, LV2, Audio Unit e Vamp

```text
src/effects/vst
src/effects/lv2
src/effects/audio_unit
src/effects/vamp
```

racchiude gestione dei plugin oltre a openvino e nyquist

---

### OpenVINO AI Tools

ho trovato solo riferimenti, sicuro va messo come componente interno? (meglio trattarlo come side?)

---

desktop app ui flusso 

```text
User
  -> App Shell
  -> Application Action Controller
  -> Project Scene / Track Edit / Effects UI
  -> Project / Audio / Plugin / Cloud modules
```

plugin flusso:

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