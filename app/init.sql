CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    refresh_token TEXT,
    refresh_token_expires_at BIGINT,
    revoked BOOLEAN,
    profile_picture TEXT,
    phone_number VARCHAR(20),
    status VARCHAR(10) CHECK (status IN ('online', 'offline'))
);

-- =========================
-- WORKSPACES
-- =========================
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    project_nature TEXT,
    start_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    created_by INTEGER REFERENCES users(user_id) ON DELETE CASCADE, 
    workspace_profile_url TEXT 
);

-- =========================
-- WORKSPACE MEMBERS (M:N)
-- =========================
CREATE TABLE IF NOT EXISTS workspace_members (
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(20) CHECK (role IN ('leader', 'member')),
    nickname VARCHAR(100),
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id)
    
);

-- =========================
-- TASKS
-- =========================
CREATE TABLE IF NOT EXISTS tasks (
    task_id SERIAL PRIMARY KEY,
    
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    subject VARCHAR(200),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline DATE,
    status VARCHAR(20) CHECK (status IN ('pending', 'done', 'overdue')),
    priority_level VARCHAR(20),
    created_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    marked_done_at TIMESTAMPTZ
);

-- =========================
-- SUBTASKS
-- =========================
CREATE TABLE IF NOT EXISTS subtasks (
    subtask_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    is_done BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TASK ASSIGNMENTS (M:N)
-- =========================
CREATE TABLE IF NOT EXISTS task_assignments (
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, user_id)
);

-- =========================
-- COMMENTS
-- =========================
CREATE TABLE IF NOT EXISTS task_comments (
    comment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    sender_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

-- =========================
-- TASK LOGS
-- =========================
CREATE TABLE IF NOT EXISTS task_logs (
    task_log_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    context TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TASK ATTACHMENTS
-- =========================
CREATE TABLE IF NOT EXISTS task_attachments (
    attachment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    uploaded_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    file_url TEXT NOT NULL,
    file_type VARCHAR(20) CHECK (file_type IN ('image', 'pdf', 'docs')),
    file_size_mb DECIMAL(10,2),
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- NOTIFICATIONS
-- =========================
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- MESSAGES
-- =========================
CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    message_type VARCHAR(20) CHECK (message_type IN ('text', 'image', 'file', 'poll')),
    reply_to INTEGER REFERENCES messages(message_id) ON DELETE SET NULL,
    sent_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TEXT MESSAGES
-- =========================
CREATE TABLE IF NOT EXISTS text_messages (
    text_message_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    content TEXT NOT NULL
);

-- =========================
-- MESSAGE READ STATUS
-- =========================
CREATE TABLE IF NOT EXISTS message_read_status (
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    last_read_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id)
);

-- =========================
-- MESSAGE ATTACHMENTS
-- =========================
CREATE TABLE IF NOT EXISTS message_attachments (
    attachment_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_type VARCHAR(20) CHECK (file_type IN ('image', 'video', 'file')),
    file_size_mb DECIMAL(10,2),
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- PINNED MESSAGES
-- =========================
CREATE TABLE IF NOT EXISTS pinned_messages (
    pin_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    pinned_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    pinned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE
);

-- =========================
-- POLLS
-- =========================
CREATE TABLE IF NOT EXISTS polls (
    poll_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    created_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- POLL OPTIONS
-- =========================
CREATE TABLE IF NOT EXISTS poll_options (
    option_id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(poll_id) ON DELETE CASCADE,
    option_text VARCHAR(200) NOT NULL
);

-- =========================
-- POLL VOTES
-- =========================
CREATE TABLE IF NOT EXISTS poll_votes (
    vote_id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(poll_id) ON DELETE CASCADE,
    option_id INTEGER REFERENCES poll_options(option_id) ON DELETE CASCADE,
    voted_by INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    voted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- WEEKLY REPORTS
-- =========================
CREATE TABLE IF NOT EXISTS weekly_reports (
    weekly_report_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    summary_content TEXT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- AI REPORTS
-- =========================
CREATE TABLE IF NOT EXISTS ai_reports (
    report_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    report_type VARCHAR(20) CHECK (report_type IN ('final')),
    content TEXT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- VIEWS
-- =========================

CREATE OR REPLACE VIEW message_details AS
SELECT m.message_id,
       m.workspace_id,
       m.sender_id,
       u.profile_picture,
       wm.nickname,
       m.message_type,
       m.reply_to,
       m.sent_at,
       t.content,
       a.file_url,
       a.file_type,
       p.question
FROM messages m
LEFT JOIN workspace_members wm ON m.workspace_id = wm.workspace_id AND m.sender_id = wm.user_id
LEFT JOIN users u ON m.sender_id = u.user_id
LEFT JOIN text_messages t ON m.message_id = t.message_id
LEFT JOIN message_attachments a ON m.message_id = a.message_id
LEFT JOIN polls p ON m.message_id = p.message_id;
