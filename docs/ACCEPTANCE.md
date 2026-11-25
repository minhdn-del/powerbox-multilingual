# Ma trận nghiệm thu

Trạng thái hiện tại: **chưa đủ điều kiện release**. Đừng ghi PASS cho test chưa chạy. Mỗi test phải ghi APK hash, ABI, Android version, thiết bị/firmware, locale, steps, expected/actual, log/screenshot và ngày. Chạy cả bản gốc để so sánh khi cần.

| ID | Gate | Kết quả hiện có | Điều kiện đạt cuối cùng |
|---|---|---|---|
| A01 | Input integrity | PASS ở bàn giao | Hash đúng, CRC OK, gốc không đổi |
| A02 | Flutter native menu | BLOCKED (phiên 2: cần source, xem docs/aot-map.md) | Settings → Language, đủ locale gốc + en/th/lo/km, không mất chức năng |
| A03 | Apply / persist | NOT RUN Android | Đổi đồng bộ mọi màn hình, kill/restart/reopen, fallback và restore |
| A04 | Text coverage | DRAFT | Inventory từng màn hình, không còn chuỗi UI không dịch ngoài whitelist, 4 locale duyệt ngữ cảnh |
| A05 | Images/fonts | DRAFT | Ảnh đúng locale, đủ glyph, không tofu/cắt chữ, không thay biểu tượng |
| A06 | Blockly desktop | PASS giới hạn stage3/4 | 6 trang, 24 lượt locale, XML mẫu/defaults, restore, no JS exceptions; mở rộng test |
| A07 | Android WebView | NOT RUN | Locale native đồng bộ, all blocks/menu, save/open/edit, XML và command equivalence, localStorage behavior |
| A08 | Official package/signing | NOT RUN | zipalign/apksigner PASS, no unapproved entry changes, hash report |
| A09 | Install / launch | APK gốc: chạy trên emulator Android 14 (--abi arm64-v8a); APK mới: NOT RUN | cài sạch, khởi động, logcat không crash/ANR trên ABI và Android đã cam kết |
| A10 | BLE | NOT RUN | scan, connect, disconnect, reconnect, permissions, disconnect safe state, commands như bản gốc |
| A11 | Control regression | NOT RUN | mỗi mode/port hiện có, hướng/tốc độ/stop, sensor/path/voice nếu có, test không tải trước |
| A12 | User data | NOT RUN | chương trình cũ, export/import hoặc save/open nếu app có, không mất dữ liệu do locale |
| A13 | Native review | NOT RUN | reviewer English/Thai/Lao/Khmer duyệt nội dung, ngữ nghĩa và layout |
| A14 | Release permission | NOT CONFIRMED | có quyền sửa/phân phối, license/attribution, không leak key/source proprietary |

## An toàn thiết bị
Dùng thiết bị thử nghiệm, backup dự án, tháo motor hoặc kê bánh trên giá an toàn; kiểm tra dừng và mất kết nối trước các thử nghiệm có chuyển động. Không dùng xe thật đang di chuyển hay tải nặng để thử app chưa xác minh. Không tự gửi BLE payload không hiểu. Không coi byte-identical native libraries là bằng chứng BLE chạy đúng, vì chữ ký, môi trường hoặc WebView có thể ảnh hưởng hành vi.

## Release checklist
- [ ] Tất cả gate A01–A14 PASS hoặc phạm vi ngoại lệ được chủ dự án chấp thuận rõ (không bỏ menu chính/dịch toàn app).
- [ ] Một APK duy nhất, tên final, SHA-256, version và changelog.
- [ ] Báo cáo test chính thức, hướng dẫn cài, cảnh báo chữ ký/backup.
- [ ] Repo không chứa key hoặc file bên thứ ba không có quyền phân phối.
