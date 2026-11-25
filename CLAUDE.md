# Claude Code — nhiệm vụ Power Box Multilingual

Bạn tiếp tục công việc từ các checkpoint có thật trong `local/`. Chủ dự án chỉ yêu cầu bổ sung ngôn ngữ, không viết lại app, không đổi Rust, không sửa chức năng. Đọc `docs/HANDOFF.md`, `docs/ROADMAP.md`, `docs/ACCEPTANCE.md`, `docs/ARTIFACTS.md` và chạy `python scripts/verify_inputs.py` trước.

## Yêu cầu sản phẩm
- Một APK Power Box 2.1.1 duy nhất, thêm English (en, giữ nếu đã có), ภาษาไทย (th), ພາສາລາວ (lo), ភាសាខ្មែរ (km). Giữ mọi ngôn ngữ gốc (xác minh runtime, không suy ra từ tên ảnh). Không thêm tiếng Việt.
- Menu Language trong Settings chính, chọn ngôn ngữ ngay trong app, cập nhật đồng bộ tất cả màn hình, ảnh, Blockly, thông báo, hướng dẫn, lưu lựa chọn qua khởi động lại, fallback hợp lệ.
- Giữ bố cục, biểu tượng, chức năng, chương trình lưu, Bluetooth, mã lệnh động cơ, permission, package ID nếu có thể. Chỉ đổi nội dung và điều chỉnh hiển thị tối thiểu cần thiết để không cắt chữ. Không thay đổi giá trị điều khiển, ID, schema, tên biến người dùng, dữ liệu chương trình hoặc firmware.

## Quy tắc kỹ thuật
1. Không xem 35 ứng viên chuỗi là địa chỉ patch. `strings` không xác định Dart object, kích thước, encoding, object pool hay call site. Không replace byte mù, không giả lập menu/overlay rồi gọi là toàn app. Không xóa kiểm tra chữ ký hoặc cơ chế bảo vệ. Chỉ nghiên cứu/phân phối trong phạm vi được phép.
2. Dùng skill Android Reverse Engineering (ZIP gốc trong `local/input/`; đọc SKILL.md, kiểm tra script trước khi chạy). Flutter cần tooling AOT khớp snapshot/engine; JADX chỉ hữu ích lớp Android/plugin. Rust-anything chỉ tham khảo phương pháp kiểm thử tương đương, không dùng để chuyển ngôn ngữ code.
3. Ưu tiên source chính thức nếu có thể xin hợp pháp; hiện không có source. Đừng giả định có thể khôi phục Dart source hoàn chỉnh. Nếu Blutter không hỗ trợ Dart/ABI, tìm công cụ phù hợp có bằng chứng, ghi rõ blocker; không tạo APK lỗi hoặc tuyên bố hoàn thành.
4. Dùng stage3 làm baseline Blockly, stage1 ảnh và stage5 từ điển chỉ là draft. Cần kiểm tra `DEFAULT_LIST_ITEM`, `PROCEDURE_DEFAULT_NAME`, placeholders và tương đương XML. Chuyển từ localStorage độc lập sang một source-of-truth native locale sau khi xác minh bridge hiện có hoặc có phương án được kiểm chứng.
5. Không commit `local/`, APK, khóa, code/ảnh bên thứ ba. Giữ nguyên APK gốc, kiểm tra hash. Build mỗi phiên bản thành file riêng; dùng Android SDK chính thức `zipalign`, `apksigner`, `adb`; khóa mới local, không gửi lên Git. Không đảm bảo cài đè do chữ ký khác.
6. Mỗi phiên tạo báo cáo kết quả, lệnh chạy, log, test, file sửa, hash, rủi ro và bước kế tiếp. Đừng đánh dấu PASS khi chưa chạy. Tách static, desktop, Android emulator, real hardware và native language review. Không hứa hoàn hảo nếu chưa đạt nghiệm thu.

## Bắt đầu ngay ở mốc AOT
Fingerprint lại APK, đối chiếu SHA-256, Dart/engine snapshot, cả hai ABI. Lập bản đồ locale thực tế, `Settings`/`language`, image routing, state persistence, Flutter-WebView bridge. Kiểm tra tool version compatibility trước khi cài. Chứng minh 1 màn hình Settings và 1 locale mới hoạt động trên Android cùng ngôn ngữ gốc, rồi mới mở rộng. Ghi bằng chứng đường dẫn/hàm/object/reference và giải pháp patch hoặc source build. Nếu chưa chứng minh, giữ checkpoint Blockly và báo chính xác công cụ/phần cứng cần bổ sung. Sau đó hoàn thành roadmap, kiểm thử tất cả gate và chỉ xuất `PowerBox_2.1.1_Multilingual.apk` khi đã đạt.
