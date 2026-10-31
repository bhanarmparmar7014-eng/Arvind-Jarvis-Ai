[app]
title = ARVIND JARVIS AI
package.name = jarvis
package.domain = org.arvind

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy,plyer,requests,urllib3,certifi,chardet,idna


orientation = portrait
fullscreen = 0

# Android Permissions
android.permissions = INTERNET, RECORD_AUDIO, BATTERY_STATS, CALL_PHONE

# Android API aur NDK version stable set karein
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a


# Allow Root / PRoot Build
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
