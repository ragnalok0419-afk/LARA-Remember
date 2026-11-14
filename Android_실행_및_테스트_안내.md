# Android + Pleos 테스트 안내

## Android APK 빌드

1. GitHub에 이 폴더 **전체 내용**을 업로드 (`.github/workflows` 포함).
2. Actions > `Build LARA Android installable APK` > Run workflow.
3. 초록색 성공 표시 및 `LARA-Android-release-APK` 아티팩트의 APK를 내려받아 실제 Android 기기에 설치.
4. 성공하지 않으면 GitHub Actions 전체 오류 로그를 확인하고 수정하기. **APK 생성/서명/설치는 이 문서 작성 시점에 미검증.**
5. 공모전 제출 이름은 `손정훈_LARA_release.apk` 권장. 실제 APK를 이름만 바꾸더라도 유효한 설치 파일인지 확인.

## 휴대폰 연결

- PC에서 Ollama를 켜고 `ollama pull qwen3:1.7b` 실행(최초 한 번).
- PC에서 `휴대폰연결_PC서버실행.bat`를 열고 YES 입력.
- 같은 비공개 Wi-Fi에서 PC IP 확인 후 Android 앱 첫 화면에 `http://PC_IP:8765` 설정.
- 일반 Android Emulator에서 PC 서버는 보통 `http://10.0.2.2:8765`가 사용되나, **Pleos AVD에서는 네트워크 동작을 확인해야 하며** PC 서버가 로컬 접속만 열려 있을 경우 연결되지 않음.
- 공개 Wi-Fi에서 실행하거나 라우터 포트를 인터넷에 개방하지 말 것. 입력된 기억은 암호화되지 않았으므로 시연에는 가상 개인 정보만 사용.

## 필수 검증 시나리오

1. 음성 대화 → Qwen3 응답이 질문에 대응하는지 확인
2. `내일 부산 출장 가, 기억해 줘` → 승인 버튼 → 새로고침 후 기억 확인
3. 동승자 모드 → 기억을 대화에 사용하지 않는지 확인
4. 서울 출발 / 부산 도착, 주행가능거리 181km → 경로 조회 및 부족 거리 안내 확인
5. 주유소 후보가 조회된 경우에만 동의 후 경유지 시뮬레이션, 기존 부산 목적지 유지 확인
6. 온라인 지도 오류 시 임의 시설·거리를 만들어 내지 않는지 확인
7. Android 앱에서 지도 열기, 한국어 음성 인식/합성, 서버 주소 변경 확인
8. 실제 Pleos AVD에서 앱 설치, SDK 호출은 추가 검증 필요

## 오류 유형

- HTTP 502 = Ollama 호출·응답 문제: 모델 설치(`ollama list`), 서버 로그 확인.
- 접속 실패 = IP / PC 서버 / Windows 방화벽 Private 프로필 / Wi-Fi 분리 여부 확인.
- APK 빌드 실패 = Actions 로그 확인, SDK/Gradle 동기화 및 signing 세부 확인.
