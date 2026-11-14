# LARA Android submission build kit

A WebView Android front-end for the LARA PC/Ollama demo server. This is **not a self-contained offline LLM** and **not a Pleos SDK-integrated application**.

## Build
- Android API 34 / minSdk 28, Android Gradle Plugin 8.3.2, Gradle 8.4, Java 17.
- `.github/workflows/android-release.yml` builds and signs an installable **demo** release APK, downloadable in GitHub Actions artifacts.
- Alternatively open this directory as a project in Android Studio (Gradle 8.4 required); generate a signed APK via Build > Generate Signed Bundle / APK.

## Test Android
1. PC: Ollama running with qwen3:1.7b and Python 3 installed.
2. PC and phone connected to same **trusted private Wi-Fi**.
3. Run `휴대폰연결_PC서버실행.bat`, confirm `YES`; note PC IPv4 address. Allow Windows Firewall **Private networks only** if requested.
4. Phone: Install APK, enter `http://<PC_IPV4>:8765` at first start. Do not use `127.0.0.1` on phone (it refers to phone, not PC).
5. Tick `Ollama 연동 사용` and check server connection. Try voice via microphone, memory save/approval, restart, memory reuse, delete, route lookup.
6. To switch server address use Android back button in the app.

The local HTTP server exposes conversational requests to LAN clients; never use public/shared Wi-Fi, never forward port 8765. Close the server after demo. Stored memories are in Android WebView local storage, not encrypted; use fictional demo information only.

## Limitations
- No Play Store/Pleos deployment, no native vehicle SDK, no physical car state.
- Uses OS native speech recognizer and TextToSpeech. Services might require device-specific connectivity and permissions.
- Public OSM/OSRM providers not guaranteed. No real-time traffic or charge/fuel availability guarantees.
- Test-signed demonstration release is not suitable for production distribution. Per-build ephemeral certificate prevents updates over prior builds.
- APK build and installation are not yet verified by the assistant's execution environment.

## Pleos verification
See `PLEOS_연동_현황과_실행순서.md`. Vehicle/NaviHelper SDK and emulator are **not integrated or validated**. This remains a prototype, not a certified Pleos app.

## Local regression checks
Run `python -m unittest discover -s tests -v` and `python validate_project.py`.
