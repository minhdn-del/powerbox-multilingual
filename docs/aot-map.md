# AOT map — cơ chế ngôn ngữ của Power Box 2.1.1 (M1)

Phiên 2, 2026-11-26. Đối tượng: `lib/arm64-v8a/libapp.so` SHA-256 `93f0c2a0…7e04` từ APK gốc `30bd6c88…bf99`. Địa chỉ là địa chỉ ảo trong `libapp.so` (trùng offset file). Repo công khai nên chỉ ghi địa chỉ, offset pool và kết luận; không chép dump, bảng dịch hay mã trích xuất.

## Công cụ và cách tái lập
| Bước | Công cụ / phiên bản | Ghi chú |
|---|---|---|
| Phân tích snapshot | Blutter `worawit/blutter@4a60ac64` (2026-08-18), dựng trên Windows bằng VS 2022 17.14 + cmake 4.4.5/ninja 1.13 từ pip, ICU 73.2, Capstone 4.0.2 | Phải thêm `/Zc:preprocessor` vào cờ MSVC ở `scripts/CMakeLists.txt` và `blutter/CMakeLists.txt` (Dart 3.12 dùng `__VA_OPT__`). Xuất ra `local/blutter-arm64/` (không commit). |
| Thân hàm thiếu | `scripts/aot_disasm.py` (tự viết, chỉ đọc) + Capstone 5.0.7 | Blutter chỉ in thân 162 hàm; 826 hàm `size: -0x1` vì Code object bị loại (`dwarf_stack_traces_mode`). Tool lấy entry point từ `ida_script/addNames.py` + đích `bl`, cắt hàm theo entry kế tiếp, chú thích nạp pool qua `x27`. |
| Runtime | Emulator `powerbox34` (Android 14 x86_64 google_apis_playstore, ARM64 qua `libndk_translation`) | Phải cài `adb install -g --abi arm64-v8a`; mặc định Android chọn x86_64 (APK có vài `.so` x86_64 nhưng không có `libapp.so`/`libflutter.so` x86_64) và app gốc crash `UnsatisfiedLinkError`. |

Lệnh: `python -I scripts/aot_disasm.py local/work/lib/arm64-v8a/libapp.so local/blutter-arm64 xref 0xe448` hoặc `fn 0x2994c8`.

## Ngôn ngữ gốc (đã xác minh runtime trên emulator)
- Chỉ **2 ngôn ngữ**: Trung (`ch`) và Anh (`en`). Lần chạy đầu mặc định `ch`, không theo ngôn ngữ hệ thống.
- Menu chọn: **dropdown lá cờ ở góc phải trên trang chủ** (cờ Trung Quốc / cờ Mỹ). Không thấy trong Settings riêng. Đổi có hiệu lực ngay, không cần khởi động lại.
- Ảnh `instruct_de`, `remote_de`, `state_de`, `state_ru` có trong APK nhưng **không được mã tham chiếu** → không phải ngôn ngữ đang hoạt động.
- Ảnh chụp mốc: `local/baseline/01_launch_arm64.png` (zh), `02_after_flag_tap.png` (dropdown), `03_home_en.png` (en).

## Lưu trữ lựa chọn
- `AppConfig` (Dart) lưu map `{appName, language, debug, saved, agree, properties}`; log `保存配置完成 {… language: en …}` khi đổi.
- Hàm dựng cấu hình mặc định: `0x24a7b8` (giá trị mặc định `language = "ch"`, pool `0x3070`), serializer khoá: `0x28613c` (pool `0x2f10..0x2f38`). Đối tượng cấu hình là static `sF._vLb` (pool `0x2ea8`).
- File lưu trong dữ liệu riêng của app; app không `debuggable` nên không đọc trực tiếp được trên emulator Google Play.

## Tra bản dịch (`tr`)
`0x2994c8` (closure, lớp obfuscate `Cka`), giả mã:
```
tr(key):
  map = (sF._vLb.language == "ch") ? LE.IVc : LE.HVc   // pool 0x3070, 0xe1e8, 0xe1e0
  return map[key] ?? key
```
- `LE.HVc` (pool `0xe1e0`) = bảng Anh, `LE.IVc` (pool `0xe1e8`) = bảng Trung; static late, khởi tạo lười bằng map literal dựng trong mã (không phải const map trong snapshot).
- **Mọi giá trị khác `"ch"` đều rơi về tiếng Anh.** Không có danh sách locale, không có `supportedLocales`/ARB, không có GetX `Translations` chuẩn.
- Khoảng 70 khoá mỗi bảng (chuỗi pool `0xe1f0..0xe700`), gồm: tên dòng sản phẩm (`a`, `n`, `n3`, … `m2`), nhãn điều khiển (`remote_txt`, `control_txt`, `path_*`, `component_1..7`, `module`), hộp thoại (`camera`, `photos`, `tips`, `delete`, `cancel`, `delete_message`), ảnh theo ngôn ngữ (`program`, `remote`, `introduce`, `gravity`, `languangImage`), `lang`, trạng thái Bluetooth.
- **Khoá chức năng, không phải chữ hiển thị**: `baidu_asr_pid` (mã mô hình nhận giọng nói Baidu, khác nhau giữa en/zh) và `voice_command_1..5` (chuỗi so với kết quả nhận giọng nói). Ngôn ngữ mới phải giữ giá trị tương ứng của tiếng Anh cho các khoá này, nếu không chức năng điều khiển giọng nói hỏng.

## Chọn ảnh theo ngôn ngữ
- Ảnh chính lấy qua `tr("program" | "remote" | "introduce" | "gravity" | "languangImage")` → đường dẫn asset `assets/*_en.png` hoặc `assets/*_zh.png` / `state_ch.png`.
- `0x297ec4`: dựng `"assets/state_" + x + ".png"`; `0x297f2c`: ánh xạ `ch`/`en`.
- `0x2d23d0`: dựng tên ảnh `.jpg` theo `"cn"`/`"en"` + `"_"` (pool `0x15f38`, `0xe0a8`, `0x15f40`) — chưa xác định asset tương ứng (không có `.jpg` trong `flutter_assets`; có thể tải/lấy nơi khác). Cần làm rõ ở M3.

## Blockly / WebView
- Trang được nạp qua `webview_flutter_android` `loadUrl` + `FlutterAssetManager`; pool có `assets/html/index_l.html`, `assets/html/index_3.html` (các trang khác dựng động).
- Chưa thấy native truyền ngôn ngữ sang WebView (không có `runJavaScript`/tham số `lang` trong pool). Cầu nối ngôn ngữ native→Blockly **chưa tồn tại** trong bản gốc.

## ARM32 (`armeabi-v7a`)
- Cùng snapshot hash `ace65428…` → cùng mã Dart, cùng logic; layout khác (32-bit, không nén con trỏ).
- Blutter chỉ hỗ trợ arm64 (README). Chưa có công cụ có bằng chứng hỗ trợ phân tích Dart 3.12 ARM32.

## Kết luận gate M1 → M2
Xem `docs/sessions/2026-11-26_session2.md` mục "Đánh giá khả thi".
