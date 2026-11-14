from pathlib import Path
import py_compile, subprocess
p=Path(__file__).resolve().parent
py_compile.compile(str(p/'server.py'), doraise=True)
html=(p/'app/src/main/assets/index.html').read_text(encoding='utf-8')
js=html.split('<script>',1)[1].split('</script>',1)[0]
subprocess.run(['node','--check','-'],input=js,text=True,check=True)
java=(p/'app/src/main/java/com/remember/lara/MainActivity.java').read_text(encoding='utf-8')
manifest=(p/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
assert 'INTERNET' in manifest and 'RECORD_AUDIO' in manifest
assert 'window.laraSpeechResult' in java
assert 'AndroidLara' in java and 'openExternal' in java
assert 'LARA_LAN' in (p/'server.py').read_text(encoding='utf-8')
assert 'new URL(' in html and 'location.origin' in html
print('Source-level smoke checks passed; this is NOT an Android build or device test.')
