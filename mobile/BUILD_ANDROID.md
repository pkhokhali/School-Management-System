# Build APK without Android Studio (IDE)

You need **Android SDK tools** to build an APK, but you do **not** need the full Android Studio IDE. Pick one option below.

---

## Option A — Smallest local install (Command-line tools only)

No Android Studio app — only the SDK (~smaller download).

1. Download **Command line tools only** for Windows:  
   https://developer.android.com/studio#command-line-tools-only  
   (scroll to “Command line tools only”)

2. Unzip to e.g. `C:\Android\cmdline-tools\latest\`

3. Install SDK packages (PowerShell):

```powershell
$env:ANDROID_HOME = "C:\Android"
mkdir -Force "$env:ANDROID_HOME\cmdline-tools\latest" | Out-Null
# Move unzipped tools into cmdline-tools\latest if needed

& "$env:ANDROID_HOME\cmdline-tools\latest\bin\sdkmanager.bat" --sdk_root=$env:ANDROID_HOME "platform-tools" "platforms;android-35" "build-tools;35.0.0"

flutter config --android-sdk $env:ANDROID_HOME
flutter doctor --android-licenses
```

4. Set **User** environment variable `ANDROID_HOME` = `C:\Android` (Windows Settings → Environment variables), restart terminal.

5. Build:

```powershell
cd mobile
flutter build apk --debug --dart-define=API_BASE_URL=http://YOUR_PC_IP:8000/api/v1
```

APK: `build\app\outputs\flutter-apk\app-debug.apk`

---

## Option B — Build APK in the cloud (nothing to install except Git)

If the project is on **GitHub**:

1. Push this repo to GitHub.
2. Open **Actions** → **Build mobile APK** → **Run workflow**.
3. Set **api_base_url** to your PC address, e.g. `http://192.168.101.85:8000/api/v1`.
4. When finished, download **institute-mobile-debug-apk** from the run’s **Artifacts**.
5. Copy `app-debug.apk` to your phone and install.

No Android Studio and no local SDK required.

---

## Option C — Quick UI test in Chrome (not a real APK)

Camera/QR may not work; good for login and student screens only:

```powershell
cd mobile
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

Docker must expose port 8000 on the host.

---

## After you have the APK on your phone

| Check | Detail |
|-------|--------|
| Same Wi‑Fi | Phone and PC |
| Docker | `docker compose up` in `docker/` |
| API test | Phone browser → `http://YOUR_PC_IP:8000/api/v1/features/` |
| Firewall | Allow TCP **8000** on private network |
| Login | `student1@institute.edu.np` / `student123` |

---

## Optional — Full Android Studio

Only if you want an emulator and visual Android debugging:  
https://developer.android.com/studio
