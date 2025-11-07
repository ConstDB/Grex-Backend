import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import numpy as np
from app.ai_assistant.vectorstore.message_vector_store import ProcessMessageLogs
# from ..ai_assistant.vectorstore.message_vector_store import ProcessMessageLogs

@pytest.mark.asyncio
async def test_insert_message_to_vdb_success():
    # Arrange
    process_logs = ProcessMessageLogs()
    mock_embedding = np.array([0.1, 0.2, 0.3])

    with patch("ai_assistant.vectorstore.message_vector_store.compute_embedding", return_value=mock_embedding):
        with patch("ai_assistant.vectorstore.message_vector_store.qdrant.upsert", new_callable=AsyncMock) as mock_upsert:
            
            # Act
            await process_logs.insert_message_to_vdb(1, 123, "Hello World")

            # Assert
            mock_upsert.assert_called_once()
            args, kwargs = mock_upsert.call_args
            assert kwargs["collection_name"] == process_logs.message
            assert kwargs["points"][0].payload["workspace_id"] == 1
            assert kwargs["points"][0].payload["message_id"] == 123


@pytest.mark.asyncio
async def test_get_message_embeddings_calls_qdrant_search():
    process_logs = ProcessMessageLogs()
    fake_embedding = np.array([0.5, 0.5, 0.5])
    
    fake_result = [
        type("Record", (), {"id": 1, "vector": [0.1, 0.2], "payload": {"message_id": 123}})
    ]
    
    with patch("ai_assistant.vectorstore.message_vector_store.qdrant.search", new_callable=AsyncMock, return_value=fake_result) as mock_search:
        await process_logs.get_message_embeddings(fake_embedding, 1)
        
        mock_search.assert_called_once()
        args, kwargs = mock_search.call_args
        assert kwargs["collection_name"] == process_logs.message
        assert kwargs["limit"] == 10
        assert kwargs["query_vector"] is fake_embedding
        assert kwargs["query_filter"] is not None


@pytest.mark.asyncio
async def test_queue_processes_messages(monkeypatch):
    process_logs = ProcessMessageLogs()

    # Fake async insert function
    mock_insert = AsyncMock()
    monkeypatch.setattr(process_logs, "insert_message_to_vdb", mock_insert)

    # Add some messages to the queue
    process_logs.message_queue.append({"workspace_id": 1, "message_id": 101, "content": "first"})
    process_logs.message_queue.append({"workspace_id": 1, "message_id": 102, "content": "second"})

    # Run the queue
    await process_logs.queue()

    # Assert that insert_message_to_vdb was called for each message
    assert mock_insert.await_count == 2
    mock_insert.assert_any_await(1, 101, "first")
    mock_insert.assert_any_await(1, 102, "second")

    # After queue runs, it should be empty
    assert len(process_logs.message_queue) == 0
    
@pytest.mark.asyncio
async def test_insert_message_to_vdb_failure(capsys):
    process_logs = ProcessMessageLogs()

    with patch("ai_assistant.vectorstore.message_vector_store.compute_embedding", return_value=np.array([0.1, 0.2])):
        with patch("ai_assistant.vectorstore.message_vector_store.qdrant.upsert", new_callable=AsyncMock) as mock_upsert:
            # Force qdrant.upsert to raise an error
            mock_upsert.side_effect = Exception("DB insert failed")

            await process_logs.insert_message_to_vdb(1, 123, "failing content")

            # Capture the printed error
            captured = capsys.readouterr()
            assert "failed to insert message into qdrant" in captured.out


@pytest.mark.asyncio
async def test_get_message_embeddings_failure(capsys):
    process_logs = ProcessMessageLogs()

    with patch("ai_assistant.vectorstore.message_vector_store.qdrant.search", new_callable=AsyncMock) as mock_search:
        # Force search to fail
        mock_search.side_effect = Exception("Search failed")

        await process_logs.get_message_embeddings(np.array([0.5, 0.5]), 1)

        captured = capsys.readouterr()
        assert "Failed to fetch message logs embeddings" in captured.out


@pytest.mark.asyncio
async def test_queue_failure_logs(monkeypatch, caplog):
    process_logs = ProcessMessageLogs()

    async def fake_insert_message_to_vdb(workspace_id, message_id, content):
        raise Exception("Insert failed")

    monkeypatch.setattr(process_logs, "insert_message_to_vdb", fake_insert_message_to_vdb)

    # Add a message to the queue
    process_logs.message_queue.append({
        "workspace_id": 1,
        "message_id": 42,
        "content": "bad message"
    })

    # Run the queue
    await process_logs.queue()

    # Check that the logger captured the error
    assert any("Failed to insert message log:42 to qdrant" in msg for msg in caplog.text.splitlines())

