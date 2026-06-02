workspace "Audacity" "Audacity System Analysis" {

    !identifiers hierarchical

    model {
        ####################
        # DIAGRAM ELEMENTS #
        ####################

        # Users
        audioEditor = person "Audio Editor" "Performs quick recordings, convert file formats, and apply basic edits."
        academicUser = person "Academic User" "Uses the software for academic purposes, such as audio and data analysis or developing Nyquist plugins."

        # Main System (Context)
        audacity = softwareSystem "Audacity Software System" "Allows users to record live audio, edit multi-track compositions, and apply digital signal processing effects." "MainSystem" {

          # Containers
          desktopApp = container "Desktop Application" "Front-end that allows the user to interact with Audacity's features." "C++, Qt, QML" {

            # Components
            cloudSync = component "Cloud Sync" "Interacts with audio.com to save Audacity projects in the cloud and handle authentication."

            # *MISSING* src/ modules: context, project, preferences, shared

            appEntry = component "Application Entry" "Bootstrapping layer, containing Audacity's main entry point and QML UI configuration."

            effectsPlugins = component "Effects and Plugins Engine" "Defines built-in effects and handles libnyquist integration for writing custom plugins."

            uiElements = component "UI Elements" "Provides custom reusable widgets, visual control panels (e.g. toolbars) and popup alert notifications (toasts)."

            # importExport = component "Import Export Module" "TODO" # can possibly be integrated in an existing component (?)

            legacyBridge = component "Legacy Bridge" "Translation layer that bridges the modern components to Audacity's legacy C++ codebase."

            timeline = component "Timeline Visualization and Editing" "Handles sample clip operations and selections and calculates/renders spectral audio data."

            audioEngine = component "Audio Engine" "Manages everything related to audio, from audio recording to handling audio devices."
          }

          database = container "Project File Database" "Provides local persistent storage for audacity projects in the form of aup3/aup4 files." "SQLite" "Database"
        }

        # External Systems
        ffmpeg = softwareSystem "FFmpeg" "A collection of libraries and tools to process multimedia content such as audio, video, subtitles and related metadata." "ExternalSystem"
        openvino = softwareSystem "OpenVINO" "An open-source software toolkit developed by Intel for optimizing and deploying deep learning models." "ExternalSystem"
        audiocom = softwareSystem "audio.com" "Free audio hosting platform, used for storing '.aup3' project files in the cloud." "ExternalSystem"

        #################
        # RELATIONSHIPS #
        #################

        audioEditor -> audacity.desktopApp "Performs audio editing"
        academicUser -> audacity.desktopApp "Performs audio analysis and develops Nyquist plugins" ""

        audacity.desktopApp -> audacity.database "Reads from and write to" "Direct function calls (e.g. such as open(), load())"
        audacity.desktopApp -> ffmpeg "Supports additional audio file formats using" "TODO_TECH"
        audacity.desktopApp.cloudSync -> audiocom "Syncs project files, handles user authentication" "HTTPS/JSON"
        audacity.desktopApp -> openvino "Loads plugins from" "TODO_TECH"

        academicUser -> audacity.desktopApp.effectsPlugins
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
