# File bàn giao

Toàn bộ file gốc và checkpoint đặt dưới `local/` (Git ignore). Không xóa chúng khi tạo repo local. Chỉ dùng stage3 làm baseline Blockly.

| Đường dẫn | Nội dung |
|---|---|
| `local/input/base_1.apk` | APK gốc, immutable |
| `local/build/PowerBox_2.1.1_Blockly_TEST.apk` | APK test, không có menu Flutter mới |
| `local/checkpoints/PowerBox_locale_draft.zip` | Stage1, tài nguyên ảnh/dictionary draft |
| `local/checkpoints/PowerBox_stage2_webview_patch.zip` | Stage2 cũ |
| `local/checkpoints/PowerBox_stage3_verified_patch.zip` | Stage3, baseline patch và test |
| `local/checkpoints/PowerBox_stage5_AOT_language_inventory.zip` | Stage5, 35 ứng viên chuỗi + offsets draft |
| `local/extracted/stage1/` ... `stage5/` | Đã giải nén và stage4 scripts/logs để Claude dùng ngay |
| `local/input/android-reverse-engineering-skill-master.zip` | Skill gốc do user cung cấp; đọc hướng dẫn, review trước khi chạy script |
| `local/input/rust-anything-main.zip` | Skill gốc tham khảo phương pháp regression; không chuyển app sang Rust |
| `local/evidence/apk_comparison.json` | So sánh payload APK ở phiên bàn giao |
| `local/SHA256SUMS.json` | Hash và kích thước toàn bộ file local được giao (trừ chính manifest) |

## Tái lập checkpoint (từ repo root)
```bash
python scripts/verify_inputs.py
node local/extracted/stage3/test_locale.js
# Cần Python playwright và Chromium tương thích, có thể cài qua môi trường dev:
python local/extracted/stage3/browser_test.py local/input/base_1.apk
python local/extracted/stage4/test_inline_portable.py local/input/base_1.apk local/build/PowerBox_2.1.1_Blockly_TEST.apk
```
Các test trên là desktop/mô phỏng, không phải Android. Script portable mới chỉ sửa đường dẫn, chưa xác minh chạy ở máy đích. Stage4 test builder cũ dùng `cryptography`, có tự ký v2 và tạo local test key, chỉ để tham khảo/tái lập TEST trong môi trường kiểm soát; chính thức dùng SDK signer. Nếu chạy, xuất file mới thay vì ghi đè APK đã bàn giao:
```bash
python local/extracted/stage4/build_test.py local/input/base_1.apk local/extracted/stage3/patch/assets/flutter_assets/assets/html local/build/PowerBox_Blockly_REBUILD_TEST.apk
```
Không giao key test cũ, bản rebuild có thể khác chữ ký. Các hash ban đầu chỉ kiểm tra artifact bàn giao, không tự ghi đè manifest hash để che thay đổi. Các log trước đó là bằng chứng lưu, không phải kết quả của máy mới.
