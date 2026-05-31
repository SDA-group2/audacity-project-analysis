workspace "Audacity" "Audacity System Analysis" {

    !identifiers hierarchical

    model {
        ####################
        # DIAGRAM ELEMENTS #
        ####################

        # Users
        audioEditor = person "Audio Editor" "Performs quick recordings, convert file formats, and apply basic edits."
        academicUser = person "Academic User" "Uses the software for academic purposes, such as audio and data analysis or developing Nyquist plugins."

        # Main System
        audacity = softwareSystem "Audacity Software System" "Allows users to record live audio, edit multi-track compositions, and apply digital signal processing effects." "MainSystem" {
          desktopApp = container "Desktop Application" "Front-end that allows the user to interact with Audacity's features." "C++, Qt, QML" {
            cloudSync = component "Cloud Sync" "Interacts with audio.com to save Audacity projects in the cloud."
            plugins = component "Plugin Component" "TODO"
          }

          database = container "Project File Database" "Provides local persistent storage for audacity projects in the form of aup3/aup4 files." "SQLite" {
            tags "Database"
          }
        }

        # External Systems
        ffmpeg = softwareSystem "FFmpeg" "A collection of libraries and tools to process multimedia content such as audio, video, subtitles and related metadata." "ExternalSystem"
        openvino = softwareSystem "OpenVINO" "An open-source software toolkit developed by Intel for optimizing and deploying deep learning models." "ExternalSystem"
        audiocom = softwareSystem "audio.com" "Free audio hosting platform, used for storing '.aup3' project files in the cloud." "ExternalSystem"

        #################
        # RELATIONSHIPS #
        #################

        audioEditor -> audacity.desktopApp "Performs audio editing"
        academicUser -> audacity.desktopApp "Performs audio analysis and develops Nyquist plugins"

        audacity.desktopApp -> audacity.database "Reads from and write to"
        audacity.desktopApp -> ffmpeg "Converts to some file formats using"
        audacity.desktopApp -> audiocom "Syncs project files"
        audacity.desktopApp -> openvino "Loads plugins from"

        academicUser -> audacity.desktopApp.plugins

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
