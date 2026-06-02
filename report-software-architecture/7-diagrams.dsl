workspace "Audacity" "Audacity System Analysis" {

    !identifiers hierarchical

    model {
        ####################
        # DIAGRAM ELEMENTS #
        ####################

        # Users
        audioEditor = person "Audio Editor" "Performs quick recordings, converts file formats, and applies basic edits."
        academicUser = person "Academic User" "Uses the software for academic purposes, such as audio and data analysis or developing Nyquist plugins."

        # Main System
        audacity = softwareSystem "Audacity Software System" "Allows users to record live audio, edit multi-track compositions, and apply digital signal processing effects." "MainSystem" {

            # Containers
            desktopApp = container "Desktop Application" "Front-end that allows the user to interact with Audacity's features." "C++, Qt, QML" {

                # Components
                appEntry = component "Application Entry" "Bootstrapping layer containing Audacity's main entry point, run mode selection and application initialization." "C++"

                uiElements = component "UI Elements" "Provides reusable UI components, visual controls, toolbars and integrated user notifications." "Qt / QML"

                timeline = component "Timeline Visualization and Editing" "Handles project timeline visualization, track editing interactions, selections and audio visualization." "C++ / Qt / QML"

                projectCore = component "Project Core" "Manages project state, preferences, shared context and access to project persistence." "C++"

                audioEngine = component "Audio Engine" "Coordinates playback, recording, audio devices and low-level audio operations." "C++"

                effectsPlugins = component "Effects and Plugins Engine" "Manages built-in effects and external plugin formats, including Nyquist integration." "C++ / libnyquist"

                importExport = component "Import/Export Module" "Handles audio file import/export and delegates additional formats to external libraries such as FFmpeg." "C++"

                cloudSync = component "Cloud Sync" "Interacts with audio.com to save Audacity projects in the cloud and handle authentication." "C++ / HTTPS"

                legacyBridge = component "Legacy Bridge" "Adapter layer that bridges the modern components to Audacity's legacy AU3 C++ codebase." "C++"
            }

            database = container "Project File Database" "Provides local persistent storage for Audacity projects in the form of .aup3/.aup4 files." "SQLite" "Database"
        }

        # External Systems
        ffmpeg = softwareSystem "FFmpeg" "A collection of libraries and tools to process multimedia content such as audio, video, subtitles and related metadata." "ExternalSystem"
        openvino = softwareSystem "OpenVINO" "An open-source software toolkit developed by Intel for optimizing and deploying deep learning models." "ExternalSystem"
        audiocom = softwareSystem "audio.com" "Free audio hosting platform, used for storing '.aup3' project files in the cloud." "ExternalSystem"


        #################
        # RELATIONSHIPS #
        #################

        # User interactions
        audioEditor -> audacity.desktopApp "Performs audio editing"
        academicUser -> audacity.desktopApp "Performs audio analysis and develops Nyquist plugins"
        academicUser -> audacity.desktopApp.effectsPlugins "Develops and uses custom Nyquist plugins"

        # Application startup and module initialization
        audacity.desktopApp.appEntry -> audacity.desktopApp.uiElements "Initializes UI shell and QML views" "C++ / Qt / QML"
        audacity.desktopApp.appEntry -> audacity.desktopApp.projectCore "Initializes project context and preferences" "C++ module API"
        audacity.desktopApp.appEntry -> audacity.desktopApp.audioEngine "Initializes audio services" "C++ module API"
        audacity.desktopApp.appEntry -> audacity.desktopApp.effectsPlugins "Registers effects and plugin providers" "C++ module API"
        audacity.desktopApp.appEntry -> audacity.desktopApp.cloudSync "Initializes cloud services" "C++ module API"

        # UI-level interactions
        audacity.desktopApp.uiElements -> audacity.desktopApp.timeline "Displays and controls the project timeline" "Qt/QML bindings"
        audacity.desktopApp.uiElements -> audacity.desktopApp.effectsPlugins "Shows effect/plugin actions and requests execution" "Qt/QML actions"
        audacity.desktopApp.uiElements -> audacity.desktopApp.importExport "Requests import/export operations" "Qt/QML actions"
        audacity.desktopApp.uiElements -> audacity.desktopApp.cloudSync "Shows login, sync actions and cloud notifications" "Qt/QML actions"

        # Timeline and project/audio interactions
        audacity.desktopApp.timeline -> audacity.desktopApp.projectCore "Reads and updates project state" "C++ calls"
        audacity.desktopApp.timeline -> audacity.desktopApp.audioEngine "Requests playback, recording and audio visualization data" "C++ calls"
        audacity.desktopApp.timeline -> audacity.desktopApp.legacyBridge "Uses legacy project/track functionality through adapters" "C++ wrapper calls"

        # Effects and plugins
        audacity.desktopApp.effectsPlugins -> audacity.desktopApp.projectCore "Reads selected tracks and applies effect results" "C++ calls"
        audacity.desktopApp.effectsPlugins -> audacity.desktopApp.audioEngine "Processes audio through effect pipelines" "C++ calls"
        audacity.desktopApp.effectsPlugins -> audacity.desktopApp.legacyBridge "Bridges to legacy AU3 effect/plugin APIs" "C++ wrapper calls"
        audacity.desktopApp.effectsPlugins -> openvino "Can invoke optional AI plugin bundle" "Local plugin/runtime integration"

        # Audio engine
        audacity.desktopApp.audioEngine -> audacity.desktopApp.legacyBridge "Uses existing AU3 audio functionality where needed" "C++ wrapper calls"

        # Import/export
        audacity.desktopApp.importExport -> audacity.desktopApp.projectCore "Imports/exports audio data associated with the current project" "C++ calls"
        audacity.desktopApp.importExport -> ffmpeg "Decodes/encodes additional audio formats using" "FFmpeg libraries / dynamic loading"

        # Cloud sync
        audacity.desktopApp.cloudSync -> audacity.desktopApp.projectCore "Reads project metadata and sync state" "C++ calls"
        audacity.desktopApp.cloudSync -> audacity.database "Uploads/downloads local project files" "File I/O"
        audacity.desktopApp.cloudSync -> audiocom "Syncs project files and handles authentication" "HTTPS/JSON"

        # Persistence
        audacity.desktopApp.projectCore -> audacity.database "Reads and writes Audacity project files" "SQLite / file I/O"
    }

    views {
        systemContext audacity "ContextView" {
            include *
            autoLayout tb
        }

        container audacity "ContainerView" {
            include *
            autoLayout tb
        }

        component audacity.desktopApp "ComponentView" {
            include *
            autoLayout tb
        }

        styles {
            element "MainSystem" {
                color #FFFFFF
                background #1761AF
                stroke #155190
                strokeWidth 3
                shape roundedbox
            }
            element "ExternalSystem" {
                color #FFFFFF
                background #8B8395
                stroke #726781
                strokeWidth 3
                shape roundedbox
            }
            element "Person" {
                color #FFFFFF
                background #104174
                stroke #0E345C
                strokeWidth 3
                shape person
            }
            element "Database" {
                shape cylinder
            }
            element "Container" {
                color #FFFFFF
                background #28A1D8
                stroke #167CAC
                shape roundedbox
            }
            element "Component" {
                color #FFFFFF
                background #75C4ED
                stroke #3D8ABE
                shape roundedbox
            }
            element "Boundary" {
                strokeWidth 5
            }
            relationship "Relationship" {
                thickness 4
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}