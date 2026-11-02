## reference
https://www.geeksforgeeks.org/linux-unix/proc-file-system-linux/

https://www.redhat.com/en/blog/linux-proc-filesystem

https://medium.com/@kisanthr22/mastering-proc-a-practical-guide-to-linux-process-and-system-monitoring-b5a24c1734e4

## Các thư mục và tệp tin trong `/proc` trên Linux

Trong Linux, `/proc` bao gồm một thư mục cho mỗi tiến trình đang chạy, bao gồm cả các tiến trình của kernel, nằm trong các thư mục có tên `/proc/PID`. Dưới đây là các thư mục/tệp hiện có:

| Thư mục / Tệp | Mô tả |
| :--- | :--- |
| `/proc/PID/cmdline` | Các tham số dòng lệnh. |
| `/proc/PID/cpu` | CPU hiện tại và CPU gần nhất mà tiến trình đã thực thi. |
| `/proc/PID/cwd` | Liên kết tới thư mục làm việc hiện tại. |
| `/proc/PID/environ` | Giá trị của các biến môi trường. |
| `/proc/PID/exe` | Liên kết tới tệp thực thi của tiến trình này. |
| `/proc/PID/fd` | Thư mục chứa tất cả các mô tả tệp (file descriptors). |
| `/proc/PID/maps` | Ánh xạ bộ nhớ tới các tệp thực thi và thư viện. |
| `/proc/PID/mem` | Bộ nhớ do tiến trình này nắm giữ. |
| `/proc/PID/root` | Liên kết tới thư mục gốc của tiến trình này. |
| `/proc/PID/stat` | Trạng thái của tiến trình. |
| `/proc/PID/statm` | Thông tin trạng thái bộ nhớ của tiến trình. |
| `/proc/PID/status` | Trạng thái tiến trình ở dạng dễ đọc cho con người. |

---

### Một số tệp khác trong hệ thống tệp `/proc`:

| Tệp | Mô tả |
| :--- | :--- |
| `/proc/crypto` | Danh sách các mô-đun mã hóa có sẵn |
| `/proc/diskstats` | Thông tin (bao gồm số hiệu thiết bị) cho từng thiết bị đĩa logic |
| `/proc/filesystems` | Danh sách các hệ thống tệp được kernel hỗ trợ tại thời điểm kiểm tra |
| `/proc/kmsg` | Chứa các thông điệp xuất ra bởi kernel |
| `/proc/meminfo` | Tóm tắt cách kernel đang quản lý bộ nhớ |
| `/proc/scsi` | Thông tin về bất kỳ thiết bị nào được kết nối qua bộ điều khiển SCSI hoặc RAID |
| `/proc/tty` | Thông tin về các thiết bị đầu cuối (terminals) hiện tại |
| `/proc/version` | Chứa phiên bản Linux kernel, số bản phân phối, phiên bản gcc (được sử dụng để biên dịch kernel) và bất kỳ thông tin có liên quan nào khác liên quan đến phiên bản kernel đang chạy |