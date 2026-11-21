# Claude Code — điểm vào của repo

Claude Code đọc file này tự động. Nội dung thật nằm ở hai file sau; đọc cả hai trước khi làm việc:

@RULES.md
@AGENTS.md

`RULES.md` là luật chung cấp cao nhất (R0.x): nếu có mâu thuẫn với bất kỳ skill, workflow, `PROJECT.md` hay memory nào, `RULES.md` thắng. Chỉ chỉ thị rõ ràng của người dùng trong phiên hiện tại mới được đè luật, và phải ghi vào mục *Ngoại lệ* của `PROJECT.md`.

Mọi việc làm video phải đi qua skill `/video-pipeline` và các gate trong `.agents/skills/video-pipeline/references/workflow-v2.md`.
