# LARA Pleos Connect 연동·검증 상태 (2026-11-15)

## 절대 구분해야 하는 세 가지 상태

- **작동 확인한 부분:** Windows PC에서 Python 서버 및 Ollama Qwen3를 이용한 브라우저 시연. 모의 차량 주행가능거리와 온라인 OSRM 경로를 연결한 응답 및 OSM 시설 검색 코드가 있음.
- **구성만 준비한 부분:** Android Java WebView 앱 소스, GitHub Actions 데모 release APK 빌드 워크플로. **이 환경에서 APK 빌드 성공/설치 성공을 재현하지 못함.**
- **실제로 구현되지 않은 부분:** Pleos Vehicle SDK의 실차 상태 조회, NaviHelper SDK의 실제 내비 경유지 추가, Pleos 2.1.0 에뮬레이터 구동, 실차 검증. 여기 포함된 앱을 Pleos SDK 연동 완료라고 제출하지 말 것.

## 공식 문서에서 확인한 개발 환경

- Android API 28 이상, Gradle 8.0 이상, Java 또는 Kotlin; 개발용 Pleos Connect Emulator 2.1.0.
- Windows Pleos AVD 업데이트 URL: `https://nexus-playground.pleos.ai/repository/raw-releases/connect-avd/2.x/crp-sys-img.xml`
- Android Studio > SDK Manager > SDK Update Sites > Add, 위 URL 등록 > SDK Platforms > Android API 34 Pleos Connect system image 설치.
- Device Manager > Create device > Automotive > Pleos Connect, Android API 34, RAM 4GB, Cold boot 구성.
- Pleos Playground의 프로젝트 생성 후 SDK 상태 확인. 공식 문서상 Vehicle State, NaviHelper가 사용 가능으로 표기되어 있지만 실행 환경의 실제 권한은 별도로 확인.

## 실제 SDK 연동에 필요한 단계 (아직 미완료)

1. Pleos SDK Maven 저장소: `https://nexus-playground.pleos.ai/repository/maven-releases/`
2. 공식 문서 기준 Vehicle SDK `ai.pleos.playground:Vehicle:2.3.1`(빠른 시작 예제) 또는 프로젝트 호환 버전, NaviHelper SDK `ai.pleos.playground:NaviHelper:3.0.5`. 버전 일치 여부 및 접근 권한 확인.
3. 각 API의 실제 권한을 manifest에 선언. Vehicle `Fuel` 또는 `EvBattery`의 구체적 조회 가능 속성은 에뮬레이터의 Capability API로 먼저 확인한다. **지원 여부를 알 수 없는 잔여 주행거리 API를 임의로 호출하지 않는다.**
4. SDK 연결 (`initialize`) → capability 확인 → 상태 비동기 조회 → `onComplete`/`onFailed` 처리 → 사용자에게 '실제 차량 데이터' 또는 '모의 데이터' 출처 표시 → `release`.
5. NaviHelper 연결 → 리스너 등록 → 운전자에게 정확한 경유지 이름·경로 변경 안내 → 명시적 동의 → 경유지 요청 → 이벤트로 성공 여부 확인 → 리스너 해제 및 종료.
6. Virtual Console에서 차량 값 변경 및 실패 시나리오 테스트. 이 과정이 통과하기 전까지 차량 SDK 연동 성공이라고 표시하지 않는다.

## 검증 결과 기록란

| 항목 | 현재 상태 | 실제 검증 시 기록 |
|---|---|---|
| Python 구문·단위 테스트 | 자동 검증 스크립트 제공 | tests 실행 결과 |
| JavaScript 구문 | Node가 있으면 자동 검사 | node --check |
| Gradle assembleRelease | **실행 불가** (이 환경의 SDK 부재) | GitHub Actions URL과 성공 로그 |
| Android 휴대폰 APK 설치 | **미검증** | 기기명/Android 버전/설치 로그 |
| Pleos Connect 2.1.0 AVD | **미검증** | AVD 명칭/부팅 스크린샷 |
| Vehicle SDK 상태 조회 | **미연동** | capability/실제 응답 |
| NaviHelper 경유지 변경 | **미연동** | 요청/성공 이벤트 |
| 실제 차량 데이터 | **미검증** | 지원 차량·테스트 기록 |

## 공식 출처

- https://appdevchallenge.auto-hmg.io/guide/development
- https://appdevchallenge.auto-hmg.io/guide/submission
- https://document.pleos.ai/docs/pleos-only/getting-started
- https://document.pleos.ai/docs/pleos-only/create-my-project
- https://document.pleos.ai/docs/connect/guide/getting-started/application-development/setup-connect-sdk-emulator
- https://document.pleos.ai/docs/pleos-only/connect-sdk-pleos/NaviHelper/importing-sdk

## 제출 주의

공모전 1차에서 신청서는 필수, 영상/GitHub/APK는 선택. 소스와 release APK로 가산점을 받으려면 **실제 빌드되고 설치 가능한 APK**를 `apk/`에 추가하고 저장소 URL·최종 커밋 번호를 제출해야 함. 자동 빌드용 워크플로만으로 가산점이 확정되지 않음. 시연 자료에서 Windows PC의 Ollama 서버 연결을 반드시 명시할 것.
