# Báo cáo bàn giao kỹ thuật

## Phạm vi và trạng thái
Power Box 2.1.1, package được ghi nhận `com.yundongjia.app.blocks_powerbox`, Flutter/Dart AOT, Blockly trong WebView, BLE. Metadata phiên bản/package là thông tin phân tích trước; xác minh lại bằng `apkanalyzer` hoặc `aapt` khi có SDK. Không có source Flutter gốc. Không có chứng minh main menu mới đã hoạt động. Không có bản APK final.

### Định danh APK
- Gốc SHA-256: `30bd6c884e1290204cf94d48bca15d010133aa10dddade0d87e0b1d37150bf99`.
- Blockly TEST SHA-256: `d4ea10b9b614524d93c9ef6afc26bea9fbb6e63da96d922e20e1d57829852334`.
- Kiểm tra lại ở phiên bàn giao: cả hai ZIP CRC OK, 626 entry mỗi file, tập tên entry giống nhau, nội dung khác đúng 6 HTML dưới `assets/flutter_assets/assets/html/`: `index.html`, `index_3.html`, `index_32.html`, `index_4.html`, `index_6.html`, `index_l.html`. Manifest, DEX và tất cả `.so` byte-identical. Xem `local/evidence/apk_comparison.json`. Không đồng nghĩa đã test Android hay BLE.
- Dart string ghi nhận 3.12.2 stable, hai ABI arm64-v8a và armeabi-v7a. Snapshot symbols, SHA của `libapp.so` / `libflutter.so`, asset list và FontManifest trong `local/extracted/stage3/native_inventory.json`. Cần xác minh tương thích parser cho chính snapshot này, không chỉ phiên bản Dart.

## Giai đoạn 1 — draft tài nguyên
`local/extracted/stage1/`: 20 mục dịch tham chiếu, 12 ảnh mới (4 ảnh × th/lo/km), ảnh English gốc, asset inventory và preview. `a_seiral` giữ nhãn model, các bản sao không tính là bản dịch mới. Các file JSON không phải định dạng localization native đã xác minh. Font Noto đã dùng để render ảnh trước đó không được phân phối trong gói. Chưa sửa AssetManifest.bin hoặc AOT. Chưa review người bản ngữ.

## Giai đoạn 2 và 3 — Blockly
`local/extracted/stage2/` là checkpoint cũ. Ưu tiên **stage3** (`patch/`, `blockly_messages.json`, `test_locale.js`, `browser_test.py`, logs, `native_inventory.json`). 41 key mỗi locale × 4 = 164 mục. Sáu HTML chỉ thêm import JS; script tạo select `#pb-language`, dùng `Blockly.Msg`, option `original` + en/th/lo/km, key localStorage `powerbox.blockly.locale.v1`; chọn original phục hồi giá trị ban đầu, storage failure fallback. Không đổi ID khối, code điều khiển hay XML. `DEFAULT_LIST_ITEM` và `PROCEDURE_DEFAULT_NAME` không dịch vì ảnh hưởng dữ liệu mặc định. Một số text tạo trước khi đổi locale có thể cần refresh đúng cách, chưa xác minh tất cả UI.

Bằng chứng lưu trước: `browser_results.txt`: 6 trang × 4 lượt switch, context menu cleanup thực, XML mẫu và defaults không đổi, original restore, không exception JS trong test desktop Chromium offline. Media gốc không load đầy đủ; không claim visual parity, toàn bộ tính năng hay Android. `mock_results.txt`: storage/fallback, duplicate guard ở Node VM mock.

## Giai đoạn 4 — APK TEST
`local/build/PowerBox_2.1.1_Blockly_TEST.apk`. Stage4 `build_test.py` inline JS vào 6 HTML để không sửa manifest asset. Tự tạo chữ ký v2 test và kiểm tra digest/chữ ký nội bộ; trước đó thiếu SDK apksigner chính thức, không xác minh install Android. 16 KB alignment của stored `.so` được báo bởi script cũ, cần xác minh SDK. `inline_results.txt` có 6 dòng PASS test Chromium đọc HTML trong APK mới; `packaged_test_results.txt` rỗng, không coi là PASS. `test_inline_portable.py` chỉ sửa đường dẫn local cho tái lập, chưa chạy lại bản portable ở thời điểm bàn giao. Các script cũ giữ nguyên, có đường dẫn tuyệt đối `/mnt/data/...`. Không bàn giao private key test cũ; build mới dùng key khác trừ khi có key hợp lệ bên ngoài. Đừng coi TEST là final hoặc dùng nó để vận hành thiết bị chưa test.

## Giai đoạn 5 — AOT string candidates
`local/extracted/stage5/aot_string_candidates.csv`, `evidence.json`, en/th/lo/km JSON. 35 exact printable strings có ở cả hai ELF (vd Settings, language, Remote, Gravity, Control); offsets từ GNU `strings -a -n 3 -t x`, không phải object/call-site hay instruction patch. 13 mục unmatched được ghi trong evidence, không suy ra là không tồn tại UI. Các chuỗi có thể là framework, preference keys hoặc internal strings. Không replace binary theo CSV. Chưa tìm được locale dispatcher, object pool references, menu callback, asset routing hay native bridge.

## Blocker thật sự
Blutter tải thất bại do DNS ở môi trường trước; support Dart snapshot và ARM32 chưa được thiết lập. `apksigner`, `zipalign`, `adb`, `jadx`, `blutter` không thấy trong PATH khi kiểm tra bàn giao; Java và Node có. Chưa có Android runtime, BLE device test, native reviewer. Cần môi trường dev có Internet và Android SDK, thiết bị test, quyền chỉnh sửa/phân phối. Tooling mới không bảo đảm AOT patch khả thi. Nếu không có phương án an toàn, báo không thể đáp ứng trọn vẹn bằng APK hiện có và xin source/giải pháp chính thức; không tự ý viết lại app.
