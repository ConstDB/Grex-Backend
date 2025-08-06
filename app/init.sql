-- USER TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    profile_picture TEXT,
    status TEXT CHECK (status IN ('online', 'offline'))
);

-- WORKSPACE TABLE
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    leader_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE
);

-- WORKSPACE MEMBER
CREATE TABLE IF NOT EXISTS workspace_members (
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(20) CHECK (role IN ('leader', 'member')),
    nickname VARCHAR(100),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id)
);

-- TASK TABLE
CREATE TABLE IF NOT EXISTS tasks (
    task_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline DATE,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TASK ASSIGNMENTS
CREATE TABLE IF NOT EXISTS task_assignments (
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('pending', 'done', 'overdue')),
    marked_done_at TIMESTAMP,
    PRIMARY KEY (task_id, user_id)
);

-- TASK ATTACHMENTS
CREATE TABLE IF NOT EXISTS task_attachments (
    attachment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    uploaded_by INTEGER REFERENCES users(user_id),
    file_url TEXT NOT NULL,
    file_type VARCHAR(20) CHECK (file_type IN ('image', 'pdf', 'docs')),
    file_size_mb DECIMAL(10,2),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MESSAGES
CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(user_id),
    content TEXT,
    message_type VARCHAR(20) CHECK (message_type IN ('text', 'image', 'file', 'poll')),
    reply_to INTEGER REFERENCES messages(message_id) ON DELETE SET NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MESSAGE ATTACHMENTS
CREATE TABLE IF NOT EXISTS message_attachments (
    attachment_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_type VARCHAR(20) CHECK (file_type IN ('image', 'video', 'file')),
    file_size_mb DECIMAL(10,2),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    workspace_id INTEGER REFERENCES workspaces(workspace_id),
    content TEXT NOT NULL,
    type VARCHAR(50), -- e.g., 'task_assigned', 'task_completed', 'new_message'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- WEEKLY REPORT
CREATE TABLE IF NOT EXISTS weekly_reports (
    weekly_report_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    summary_content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI REPORT
CREATE TABLE IF NOT EXISTS ai_reports (
    report_id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    report_type VARCHAR(20) CHECK (report_type IN ('final')),
    content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PINNED MESSAGE
CREATE TABLE IF NOT EXISTS pinned_messages (
    pin_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    pinned_by INTEGER REFERENCES users(user_id),
    pinned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    workspace_id INTEGER REFERENCES workspaces(workspace_id)
);

-- POLL
CREATE TABLE IF NOT EXISTS polls (
    poll_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- POLL OPTIONS
CREATE TABLE IF NOT EXISTS poll_options (
    option_id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(poll_id) ON DELETE CASCADE,
    option_text VARCHAR(200) NOT NULL
);

-- POLL VOTES
CREATE TABLE IF NOT EXISTS poll_votes (
    vote_id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(poll_id) ON DELETE CASCADE,
    option_id INTEGER REFERENCES poll_options(option_id),
    voted_by INTEGER REFERENCES users(user_id),
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
