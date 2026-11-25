# M0 — Baseline (phiên 1, 2026-11-26)

Mọi số liệu dưới đây đo lại trên máy Windows 11 của chủ dự án từ `local/input/base_1.apk`. Chỉ là phân tích tĩnh; **chưa chạy trên Android**.

## Toàn vẹn đầu vào (A01)
- `python -I scripts/verify_inputs.py` → PASS (hash toàn bộ `local/`, CRC, 626 entry, đúng 6 HTML khác giữa gốc và Blockly TEST).
- SHA-256 APK gốc: `30bd6c884e1290204cf94d48bca15d010133aa10dddade0d87e0b1d37150bf99` (khớp bàn giao).

## Định danh APK (aapt2 / apksigner / zipalign, build-tools 35.0.0)
| Mục | Giá trị |
|---|---|
| package | `com.yundongjia.app.blocks_powerbox` |
| version | versionName `2.1.1`, versionCode `1` |
| SDK | min 24, target 36, compile 37 |
| launcher | `com.yundongjia.blocks.MainActivity`, màn hình ngang |
| ký | chỉ v2; 1 signer RSA-2048, cert SHA-256 `8469496fe92e6c3199d28040b0057b5268c14f07bb25d3cf4857f88f2fa54a08` (DN: Shenzhen Yundongjia) |
| zipalign | `zipalign -c -P 16 4` → OK |
| quyền | INTERNET, ACCESS_WIFI_STATE, ACCESS_NETWORK_STATE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION (max 28), BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN (neverForLocation), BLUETOOTH_CONNECT, BLUETOOTH_ADVERTISE, RECORD_AUDIO, WAKE_LOCK, DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION |
| features | bluetooth_le, bluetooth, location, microphone, wifi, screen.landscape |

`locales` của aapt chỉ phản ánh resource Android (AndroidX/Material), **không** phải ngôn ngữ giao diện Flutter.

## Framework (fingerprint.sh của skill android-reverse-engineering)
Flutter. Mã ứng dụng nằm trong `libapp.so` (Dart AOT). DEX chỉ là vỏ Android + plugin. Thư viện native: `libapp.so`, `libflutter.so` (arm64-v8a, armeabi-v7a), `libble.so`, `libdartjni.so`, `libdatastore_shared_counter.so` (cả x86_64). Không có `libapp.so` x86_64 → máy ảo x86_64 chỉ chạy được nhờ dịch ARM (Android 11+ image có ARM translation; cần thử).

## Dart snapshot (`python -I scripts/fingerprint_snapshot.py local/input/base_1.apk`)
| ABI | libapp.so SHA-256 | snapshot hash | flags |
|---|---|---|---|
| arm64-v8a | `93f0c2a0…7e04` | `ace654289f5abc240509fc941453ebc5` | product, dedup_instructions, compressed-pointers |
| armeabi-v7a | `b74bd6ab…4253` | `ace654289f5abc240509fc941453ebc5` | product, dedup_instructions, no-compressed-pointers |

Dart `3.12.2 (stable) (Tue Jun 9 01:11:39 2026)`. Cả hai ABI biên dịch từ cùng mã Dart (cùng snapshot hash) nhưng layout object khác nhau (con trỏ nén/không nén, 64/32 bit) → mọi thay đổi phải làm riêng cho từng ABI.

## Phát hiện mới so với bàn giao
1. **Tên Dart đã bị obfuscate** (`--obfuscate`): tên lớp/hàm của app dạng `yC`, `pw`, `_xse@7391376058`. Tên framework/plugin vẫn đọc được. Hệ quả: Blutter sẽ cho cấu trúc nhưng tên hàm của app vô nghĩa; phải truy theo chuỗi hằng, asset path và call graph.
2. Không có file bản dịch (JSON/ARB) trong `flutter_assets`; chữ giao diện nằm trong snapshot. Không thấy chuỗi `English/Deutsch/Русский/中文` dạng một byte → tên ngôn ngữ (nếu có) có thể là chuỗi hai byte (UTF-16) hoặc ảnh; cần parser.
3. Neo locale đã thấy (chỉ là chuỗi, chưa phải call site): `_localeClosure` đứng sát `assets/light_zh.png`; `didChangeLocales`, `PlatformConfigurationNativeApi::SetApplicationLocale`; chuỗi `language` sát `init:` (có thể là khoá SharedPreferences); plugin `shared_preferences_android` (SharedPreferencesAsyncApi getString/setString).
4. Ảnh theo locale có hậu tố `en`, `zh`, `de`, `ru` (không đồng đều mỗi ảnh). Danh sách locale gốc thực tế vẫn **chưa xác minh runtime**.

## Môi trường máy (để làm tiếp)
| Công cụ | Trạng thái |
|---|---|
| Android SDK `%LOCALAPPDATA%\Android\Sdk` | build-tools 34/35 (aapt2, apksigner, zipalign), platform-tools (adb 37.0.3), emulator, image `android-34;google_apis_playstore;x86_64`; chưa có AVD, chưa có điện thoại cắm |
| Java | JDK 21 qua `JAVA_HOME` (PATH ưu tiên Java 8 → apksigner cần đặt PATH tạm) |
| jadx | 1.5.7 |
| Visual Studio 2022 Community 17.14 | có VC++ x64 (cần cho Blutter) |
| cmake / ninja độc lập | chưa có trong PATH (VS thường kèm sẵn) |
| Python 3.14, Node 24, git, gh | có |

## Gate
- A01: PASS (lại).
- A08 (một phần): công cụ SDK chính thức đã có; chưa build.
- Các gate khác: NOT RUN.
