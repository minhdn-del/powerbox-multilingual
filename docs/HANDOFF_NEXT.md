# Bàn giao cho phiên tiếp theo (tài khoản khác) — sau phiên 2, 2026-11-26

Đọc theo thứ tự: `CLAUDE.md` → file này → `docs/aot-map.md` → `docs/sessions/2026-11-26_session2.md` → `docs/ACCEPTANCE.md`. Các file `docs/HANDOFF.md`, `docs/ROADMAP.md` là bàn giao gốc (từ ChatGPT), vẫn còn hiệu lực về quy tắc.

## 1. Tình trạng một câu
Đã biết chính xác app đổi ngôn ngữ thế nào; **chưa thêm được ngôn ngữ nào vào app** vì phải có mã nguồn Flutter (gate M2 BLOCKED). Chưa có APK mới. Đang **chờ chủ dự án chọn hướng A/B/C** (mục 5).

## 2. Repo và nhánh
- GitHub: `https://github.com/minhdn-del/powerbox-multilingual` (**PUBLIC**, theo yêu cầu chủ dự án). Vì công khai: không đưa lên dump Blutter, bảng dịch gốc, ảnh gốc, APK, khoá.
- Nhánh làm việc: `research/aot-localization` (main chỉ có bộ hồ sơ gốc).
  ```
  git clone https://github.com/minhdn-del/powerbox-multilingual.git
  cd powerbox-multilingual
  git switch research/aot-localization
  ```
- Thư mục gốc trên máy chủ dự án: `C:\Users\daong\Projects\powerbox-multilingual`. Nếu tài khoản mới chạy **cùng máy**, mở thẳng thư mục này (đã có `local/`, `local/blutter-arm64/`, emulator).

## 3. Những thứ KHÔNG có trong Git (phải lấy riêng)
| Cần | Lấy ở đâu |
|---|---|
| `local/` (APK gốc, APK TEST Blockly, checkpoint, hash) | Giải nén `D:\Download\PowerBox_GitHub_Handoff (2).zip`, chép thư mục `local/` vào gốc repo. Kiểm: `python -I scripts/verify_inputs.py` phải PASS. |
| Kết quả Blutter `local/blutter-arm64/` | Cùng máy: đã có. Máy khác: dựng lại theo mục 4 (~10 phút biên dịch). |
| `local/work/lib/` (thư viện tách từ APK) | Tự tách: `python -I -c "import zipfile;z=zipfile.ZipFile('local/input/base_1.apk');[z.extract(n,'local/work') for n in z.namelist() if n.startswith('lib/')]"` |
| Ảnh mốc `local/baseline/*.png` | Cùng máy: đã có. Máy khác: chụp lại theo mục 4.3. |

## 4. Dựng lại môi trường (Windows 11)
### 4.1 Công cụ có sẵn trên máy chủ dự án
- Android SDK: `%LOCALAPPDATA%\Android\Sdk` — build-tools 35.0.0 (`aapt2`, `apksigner.bat`, `zipalign`), platform-tools (`adb`), emulator, image `system-images;android-34;google_apis_playstore;x86_64`. **Không có trong PATH** → gọi bằng đường dẫn đầy đủ.
- Java: PATH ưu tiên Java 8; `apksigner`/`avdmanager` cần JDK 21: đặt tạm `JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot` và đưa `...\bin` lên đầu PATH.
- Visual Studio 2022 Community 17.14 (có VC++ x64, **không** có thành phần CMake → dùng cmake/ninja từ pip).
- jadx 1.5.7 (`C:\Users\daong\.local\share\jadx\bin`), Python 3.14, Node 24, git, gh (đã đăng nhập tài khoản GitHub của chủ dự án — tài khoản Claude mới không cần đăng nhập lại nếu cùng máy).
- Skill `android-reverse-engineering` ở `~/.claude/skills/` (chỉ dùng được bước fingerprint cho app Flutter; jadx không chứa logic app).

### 4.2 Blutter (phân tích `libapp.so` arm64)
Cùng máy: đã dựng ở `C:\Users\daong\Projects\tools\blutter` (commit `4a60ac64`), venv `.venv` có cmake, ninja, pyelftools, requests, capstone; binary `bin\blutter_dartvm3.12.2_android_arm64.exe`. Chạy lại: `cmd /c C:\Users\daong\Projects\tools\run_blutter.bat`.

Máy khác:
```
git clone https://github.com/worawit/blutter.git && cd blutter
git checkout 4a60ac648bf448c5a7596437243bcd0b9376fdf0
git apply <repo>/tools/blutter/msvc-zc-preprocessor.diff   # bắt buộc: Dart 3.12 dùng __VA_OPT__
python -m venv .venv && .venv\Scripts\python -m pip install cmake ninja pyelftools requests capstone
.venv\Scripts\python scripts\init_env_win.py
```
Sửa đường dẫn trong `tools/blutter/run_blutter.bat` rồi chạy. Kết quả đúng: log kết thúc `BLUTTER_EXIT=0`, thư mục có `pp.txt`, `objs.txt`, `asm/`, `ida_script/addNames.py`.

Blutter chỉ in thân ~162/988 hàm (Dart 3.12 bỏ Code object). Dùng `scripts/aot_disasm.py` (cần `capstone`) để xem các hàm còn lại:
```
.venv\Scripts\python -I -X utf8 scripts/aot_disasm.py local/work/lib/arm64-v8a/libapp.so local/blutter-arm64 xref 0xe448
.venv\Scripts\python -I -X utf8 scripts/aot_disasm.py local/work/lib/arm64-v8a/libapp.so local/blutter-arm64 fn 0x2994c8
```

### 4.3 Emulator
- AVD `powerbox34` đã tạo (Android 14, x86_64 + dịch ARM64). Máy còn AVD `mstrans34` của việc khác — **không đụng**. Đôi khi có `emulator-5556` lạ → luôn dùng `adb -s emulator-5554`.
- Khởi động: `%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe -avd powerbox34 -no-snapshot -no-boot-anim` (chạy nền).
- **Bắt buộc** cài với `--abi arm64-v8a`, nếu không app gốc crash (`libflutter.so is for EM_AARCH64`):
  `adb -s emulator-5554 install -g --abi arm64-v8a local/input/base_1.apk`
- Mở: `adb -s emulator-5554 shell am start -n com.yundongjia.app.blocks_powerbox/com.yundongjia.blocks.MainActivity`
- Màn hình 2400×1080 ngang: nút "Got it" (1545,528); lá cờ ngôn ngữ (2195,163); trong dropdown cờ Mỹ (2195,385). Log ngôn ngữ: `adb logcat | grep " flutter "` → `保存配置完成 {… language: en …}`.

## 5. Quyết định đang chờ chủ dự án
| | Hướng | Đề xuất |
|---|---|---|
| **A** | Xin mã nguồn Flutter từ hãng Shenzhen Yundongjia (hoặc nhờ hãng build) | **Khuyên dùng.** Trong lúc chờ: làm bảng dịch đủ ~70 khoá thật, ảnh có chữ th/lo/km, chuẩn hoá Blockly stage3, test hồi quy, gói yêu cầu gửi hãng. |
| B | Nghiên cứu tái tuần tự hoá snapshot Dart 3.12.2 (hai ABI) | Không khuyên: chưa có tiền lệ, rủi ro hỏng BLE/điều khiển, ARM32 không có công cụ. Chỉ làm nếu chủ chấp nhận rủi ro bằng văn bản. |
| C | Chỉ phần Blockly | Không đạt yêu cầu "menu chính + toàn app"; cần chủ ghi nhận phạm vi ngoại lệ. |

**Đừng tự chọn thay chủ dự án.** Hỏi trước khi làm.

## 6. Việc làm được ngay dù chọn hướng nào (không sửa nhị phân)
1. Chụp mốc mọi màn hình bản gốc (zh và en): trang chủ, từng dòng sản phẩm (A/N/3/N7/N8/M/B/C/D/E/F/K/G/R/MP/M2, pin, receiver), remote, gravity, path, lập trình Blockly, camera/ảnh, xoá file, kết nối Bluetooth, hướng dẫn. Lưu `local/baseline/` (không commit).
2. Lập bảng dịch theo schema `key,source,context,en,th,lo,km,source_ref,review_status,screen_test` cho đúng các khoá trong `tr()` (pool `0xe1f0..0xe700`, xem `aot-map.md`). Giữ nguyên `baidu_asr_pid`, `voice_command_1..5` theo tiếng Anh. Bảng chứa chuỗi gốc → để trong `local/`, chỉ commit phần dịch tự viết nếu chủ đồng ý.
3. Làm rõ ảnh `.jpg` theo `cn`/`en` ở hàm `0x2d23d0`.
4. Chạy lại test Blockly stage3 (`node local/extracted/stage3/test_locale.js`, `browser_test.py`) và ghi kết quả thật.

## 7. Quy tắc phải giữ (tóm tắt từ CLAUDE.md)
- Không vá byte mù, không đè ngôn ngữ gốc, không bỏ ABI, không hook runtime rồi gọi là xong.
- Không commit `local/`, APK, khoá, mã/ảnh trích xuất. Ký bằng `apksigner`/`zipalign` của SDK, khoá mới để local.
- Mỗi phiên ghi `docs/sessions/<ngày>_sessionN.md`: lệnh, kết quả PASS/FAIL/BLOCKED/NOT RUN, rủi ro, bước sau. Không ghi PASS khi chưa chạy.
- Chủ dự án không viết mã: nói tiếng Việt dễ hiểu, một câu trước mỗi bước.

## 8. Lời nhắn dán vào phiên mới
```
Tiếp nhận dự án Power Box Multilingual. Mở thư mục C:\Users\daong\Projects\powerbox-multilingual
(hoặc clone https://github.com/minhdn-del/powerbox-multilingual, nhánh research/aot-localization,
rồi chép thư mục local/ từ D:\Download\PowerBox_GitHub_Handoff (2).zip vào gốc repo).
Đọc CLAUDE.md, docs/HANDOFF_NEXT.md, docs/aot-map.md, docs/sessions/2026-11-26_session2.md trước khi làm.
Chạy python -I scripts/verify_inputs.py. Hướng đi tôi chọn: <A / B / C>.
Nói với tôi bằng tiếng Việt dễ hiểu, một câu trước mỗi bước.
```
