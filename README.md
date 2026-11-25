# Power Box 2.1.1 — Multilingual handoff

**Trạng thái: CHƯA HOÀN THIỆN.** Repo bàn giao kỹ thuật cho Claude Code; không phải mã nguồn Flutter gốc. APK thử nghiệm chỉ thay đổi Blockly. Mục tiêu là bổ sung English (`en`), Thai (`th`), Lao (`lo`), Khmer (`km`) vào toàn app, giữ nguyên tất cả locale gốc. Tiếng Việt không nằm trong phạm vi ngôn ngữ bổ sung theo yêu cầu chốt.

## Đọc trước khi làm
- `CLAUDE.md`: chỉ dẫn bắt buộc và nhiệm vụ tiếp theo.
- `docs/HANDOFF.md`: kết quả thực tế, dữ liệu, đường dẫn và giới hạn.
- `docs/ROADMAP.md`: kế hoạch triển khai Flutter AOT, menu chính, dịch toàn app, kiểm thử.
- `docs/ACCEPTANCE.md`: điều kiện nghiệm thu và kiểm thử phần cứng.
- `docs/ARTIFACTS.md`: danh mục tài liệu bàn giao.

## Mở trong Claude Code
1. Giải nén toàn bộ ZIP vào một thư mục local. Giữ nguyên thư mục `local/`.
2. Mở thư mục này làm workspace trong Claude Code. Cho Claude đọc `CLAUDE.md` và tài liệu `docs/` trước.
3. Chạy `python scripts/verify_inputs.py` tại thư mục gốc. Python 3.10+ là đủ cho kiểm tra này.
4. Kiểm thử lại checkpoint và xác định tính khả thi của Flutter AOT trước khi thay đổi binary.
5. Nếu tạo GitHub repo, chỉ commit tài liệu và mã tự viết được phép phân phối. Mặc định tạo repo PRIVATE. Không đẩy APK, bản vá chứa code/ảnh gốc, tài nguyên trích xuất, thư viện, hay khóa ký lên GitHub (kể cả private nếu chưa có quyền). `.gitignore` loại toàn bộ `local/` ra khỏi Git. Clone repo trên máy khác không tự có các file local: chuyển chúng qua kênh riêng được phép.

## Git (tùy chọn, thực hiện trên máy người dùng)
```bash
 git init
 git add README.md CLAUDE.md .gitignore docs scripts
 git status --short
 git diff --cached --stat
 git commit -m "Document Power Box multilingual handoff"
 # Nếu đã xác thực GitHub CLI và có quyền:
 gh repo create powerbox-multilingual --private --source=. --remote=origin --push
```
Không chạy lệnh push nếu chưa rà soát quyền sử dụng, quyền sở hữu và nội dung staged. Không có repo GitHub nào được tạo bởi gói bàn giao này.

## APK hiện có
`local/input/base_1.apk`: gốc, không sửa. `local/build/PowerBox_2.1.1_Blockly_TEST.apk`: chỉ thử nghiệm Blockly; chữ ký khác bản gốc. Không gỡ app chính nếu chưa sao lưu dữ liệu. Chưa có APK toàn app hoàn thiện. Không có private signing key trong gói này.
